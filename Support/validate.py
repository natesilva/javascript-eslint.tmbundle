#!/usr/bin/env python
# encoding: utf-8

"""
Validate a JavaScript file using eslint.

Author: Nate Silva
Copyright 2014 Nate Silva
License: MIT
"""

from __future__ import print_function
import sys
import os
import re
import time
import json
import subprocess
import tempfile
import hashlib
import shutil


def show_error_message(message):
    context = {
        'message': message,
        'timestamp': time.strftime('%c')
    }

    my_dir = os.path.abspath(os.path.dirname(__file__))

    error_ejs_path = os.path.join(my_dir, 'error.ejs')
    error_ejs = open(error_ejs_path, 'r').read()

    template_path = os.path.join(my_dir, 'template.html')
    template = open(template_path, 'r').read()
    template = template.replace(
        '{{ TM_BUNDLE_SUPPORT }}',
        os.environ['TM_BUNDLE_SUPPORT']
    )
    template = template.replace('{{ EJS_TEMPLATE }}', json.dumps(error_ejs))
    template = template.replace('{{ CONTEXT }}', json.dumps(context))

    print(template)


def get_marker_directory():
    """
    Create the directory that will hold "marker" files that we use
    to detect which files have a validation window open. Used to
    implement the following feature:

    Normally, when you hit Cmd-S, the validation window appears
    only if there is a warning or error.

    Assume you had previously validated a file, and the validation
    window showing its errors is still open. Now you fix the
    errors and press Cmd-S. We want that validation window to
    update to show no errors.

    In order to do this, we have to somehow detect if TextMate has
    a validation window open for the current file. It’s not easy.
    We use marker files.

    This script creates a marker file before returning the HTML
    document that will be shown in the validation window.

    When the HTML document detects that it is being hidden (closed),
    it runs a TextMate.system command to delete its marker file.
    """
    baseDir = os.path.join(tempfile.gettempdir(), 'javascript-eslint-tmbundle')
    if not os.path.isdir(baseDir):
        os.makedirs(baseDir)

    today = time.strftime('%Y-%m-%d')
    markerDir = os.path.join(baseDir, today)
    if not os.path.isdir(markerDir):
        os.makedirs(markerDir)

    # Deletion should happen automatically, but to be clean(er),
    # delete any previous-day marker dirs.
    children = os.listdir(baseDir)
    children = [_ for _ in children if _ != today]
    children = [os.path.join(baseDir, _) for _ in children]
    children = [_ for _ in children if os.path.isdir(_)]
    [shutil.rmtree(_, True) for _ in children]

    return markerDir


def validate(quiet=False):
    # absolute path of this file, used to reference other files
    my_dir = os.path.abspath(os.path.dirname(__file__))

    # build eslint args
    args = [
        os.environ.get('TM_JAVASCRIPT_ESLINT_ESLINT', 'eslint'),
        '-f',
        'compact',
        '--no-color',
        '--stdin'
    ]

    # if we know the filename, pass it
    if 'TM_FILEPATH' in os.environ:
        args.append('--stdin-filename')
        args.append(os.path.basename(os.environ['TM_FILEPATH']))

    # the working directory; used by eslint to find its config files
    cwd = os.environ.get('TM_DIRECTORY', None)
    if not cwd:
        cwd = os.environ.get('TM_PROJECT_DIRECTORY', None)

    # Build env for our command: ESLint (and Node) are often
    # installed to /usr/local/bin, which may not be on the
    # bundle’s PATH in a default install of TextMate.
    env = os.environ.copy()
    path_parts = env['PATH'].split(':')
    if '/bin' not in path_parts:
        path_parts.append('/bin')
    if '/usr/bin' not in path_parts:
        path_parts.append('/usr/bin')
    if '/usr/local/bin' not in path_parts:
        path_parts.append('/usr/local/bin')
    env['PATH'] = ':'.join(path_parts)

    try:
        eslint = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=cwd
        )
    except OSError as e:
        msg = [
            'Hi there. This is the “JavaScript ESLint” bundle for ' +
            'TextMate. I validate your code using ESLint.',
            '',
            'I had the following problem running <code>eslint</code>:',
            '',
            '<code>%s</code>' % e,
            '',
            '<h4>How to fix it</h4>',
            'Make sure the <code>eslint</code> and <code>node</code> ' +
            'commands are on the <code>PATH</code>.',
            '',
            '<ol>' +
            '   <li>Go to <i>TextMate</i> > <i>Preferences…</i> > ' +
            '       <i>Variables</i></li>' +
            '   <li>Ensure the <code>PATH</code> is enabled there and that ' +
            '       it includes the location of your <code>eslint</code> ' +
            '       and <code>node</code> commands.</li>'
            '</ol>',
            'The path currently used by TextMate bundles is:',
            '',
            '<div style="overflow:auto"><code>%s</code></div>' % env['PATH'],
            '<h4>How to disable validation</h4>',
            'If you mistakenly installed this validation tool and want to ' +
            'disable it, you can do so in TextMate:',
            '',
            '<ol>' +
            '   <li>On the TextMate menu, choose ' +
            '   <i>Bundles</i> > <i>Edit Bundles…</i></li>' +
            '   <li>Locate “JavaScript ESLint”</li>' +
            '   <li>Uncheck “Enable this item”</li>' +
            '   <li>Close the Bundle Editor and choose “Save”</li>' +
            '</ol>'
        ]
        show_error_message('<br>'.join(msg))
        sys.exit()

    # Pipe stdin to the subprocess; if we are validating an HTML
    # file with embedded JavaScript, only pipe content within the
    # <script>…</script> tags to the subprocess.
    lines = []
    if os.environ['TM_SCOPE'].startswith('source.js'):
        for line in sys.stdin:
            lines.append(line)
    else:
        start_tag = re.compile('(\<\s*script)[\s\>]', re.IGNORECASE)
        end_tag = re.compile('\<\/\s*script[\s\>]', re.IGNORECASE)
        state = 'IGNORE'
        for line in sys.stdin:
            while line:
                if state == 'IGNORE':
                    match = start_tag.search(line)
                    if match:
                        # found a script tag
                        line = ' ' * match.end(1) + line[match.end(1):]
                        state = 'LOOK_FOR_END_OF_OPENING_TAG'
                    else:
                        lines.append('\n')
                        line = None

                elif state == 'LOOK_FOR_END_OF_OPENING_TAG':
                    gt_pos = line.find('>')
                    if gt_pos != -1:
                        line = ' ' * (gt_pos + 1) + line[gt_pos + 1:]
                        state = 'PIPE_TO_OUTPUT'
                    else:
                        lines.append('\n')
                        line = None

                elif state == 'PIPE_TO_OUTPUT':
                    match = end_tag.search(line)
                    if match:
                        # found closing </script> tag
                        lines.append(line[:match.start()])
                        line = line[match.end():]
                        state = 'IGNORE'
                    else:
                        lines.append(line)
                        line = None

    (stdout, stderr) = eslint.communicate(''.join(lines))

    if stderr:
        msg = [
            'Hi there. This is the “JavaScript ESLint” bundle for ' +
            'TextMate. I validate your code using ESLint.',
            '',
            'I had the following problem running <code>eslint</code>:',
            '',
            '<code>%s</code>' % stderr,
            '',
            '<h4>How to disable validation</h4>',
            'If you mistakenly installed this validation tool and want to ' +
            '   disable it, you can do so in TextMate:',
            '',
            '<ol>' +
            '   <li>On the TextMate menu, choose ' +
            '   <i>Bundles</i> > <i>Edit Bundles…</i></li>' +
            '   <li>Locate “JavaScript ESLint”</li>' +
            '   <li>Uncheck “Enable this item”</li>' +
            '   <li>Close the Bundle Editor and choose “Save”</li>' +
            '</ol>'
        ]
        show_error_message('<br>'.join(msg))
        sys.exit()

    # parse the results

    rx = re.compile(
        '^[^:]+\: line (?P<line>\d+), col (?P<character>\d+), ' +
        '(?P<code>\w+) - (?P<reason>.+?)(\s\((?P<shortname>[\w\-]+)\))?$'
    )

    issues = []

    for line in stdout.split('\n'):
        line = line.strip()
        if not line:
            continue

        m = rx.match(line)

        if not m:
            continue

        issue = {
            'line': int(m.group('line')),
            'character': int(m.group('character')) + 1,
            'code': m.group('code'),
            'reason': m.group('reason')
        }

        if m.group('shortname'):
            issue['shortname'] = m.group('shortname')

        issues.append(issue)

    # normalize line numbers
    input_start_line = int(os.environ['TM_INPUT_START_LINE']) - 1
    for issue in issues:
        issue['line'] += input_start_line

    # add URLs to the issues
    if 'TM_FILEPATH' in os.environ:
        url_maker = lambda x: \
            'txmt://open?url=file://%s&amp;line=%d&amp;column=%d' % \
            (os.environ['TM_FILEPATH'], x['line'], x['character'])
    else:
        url_maker = lambda x: \
            'txmt://open?line=%d&amp;column=%d' % (x['line'], x['character'])

    for issue in issues:
        issue['url'] = url_maker(issue)

    # context data we will send to JavaScript
    context = {
        'issues': issues,
        'timestamp': time.strftime('%c')
    }

    if 'TM_FILEPATH' in os.environ:
        context['fileUrl'] = \
            'txmt://open?url=file://%s' % os.environ['TM_FILEPATH']
        context['targetFilename'] = os.path.basename(os.environ['TM_FILEPATH'])
    else:
        context['fileUrl'] = 'txmt://open?line=1&amp;column=0'
        context['targetFilename'] = '(current unsaved file)'

    # Identify the marker file that we will use to indicate the
    # TM_FILEPATH of the file currently shown in the validation
    # window.
    markerDir = get_marker_directory()
    hash = hashlib.sha224(context['fileUrl']).hexdigest()
    context['markerFile'] = os.path.join(markerDir, hash + '.marker')

    context['errorCount'] = \
        len([_ for _ in context['issues'] if _['code'][0] == 'E'])
    context['warningCount'] = \
        len([_ for _ in context['issues'] if _['code'][0] == 'W'])

    if context['errorCount'] == 0 and context['warningCount'] == 0:
        # There are no errors or warnings. We can bail out if all of
        # the following are True:
        #
        #     * There is no validation window currently open for
        #       this document.
        #     * quiet is True.
        if not os.path.exists(context['markerFile']):
            if quiet:
                return

    # create the marker file
    markerFile = open(context['markerFile'], 'w+')
    markerFile.close()

    # read and prepare the template
    content_ejs_path = os.path.join(my_dir, 'content.ejs')
    content_ejs = open(content_ejs_path, 'r').read()

    template_path = os.path.join(my_dir, 'template.html')
    template = open(template_path, 'r').read()
    template = template.replace(
        '{{ TM_BUNDLE_SUPPORT }}',
        os.environ['TM_BUNDLE_SUPPORT']
    )
    template = template.replace('{{ EJS_TEMPLATE }}', json.dumps(content_ejs))
    template = template.replace('{{ CONTEXT }}', json.dumps(context))

    print(template)


if __name__ == '__main__':
    quiet = ('-q' in sys.argv or '--quiet' in sys.argv)
    validate(quiet)
