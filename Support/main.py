#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ESLint validation plugin for TextMate
"""

from __future__ import print_function
import os
import sys
import time
import re
import subprocess
import validator
from ashes import AshesEnv

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_PATH = 'tm-file://' + os.environ['TM_BUNDLE_SUPPORT']
ASHES_ENV = AshesEnv([os.path.join(THIS_DIR, 'templates')])
IGNORE_ISSUES = [
    '^File ignored because of a matching ignore pattern'
]

def get_cwd():
    """ What directory should we cd to before running eslint? """
    cwd = os.environ.get('TM_PROJECT_DIRECTORY', None)
    if not cwd:
        cwd = os.environ.get('TM_DIRECTORY', None)
    return cwd

def should_ignore(issue_reason):
    """ Given the reason text for an issue, should we ignore it? """
    for rx in IGNORE_ISSUES:
        if re.match(rx, issue_reason):
            return True
    return False

def validate():
    """
    Run ESLint validation using settings from the current TextMate
    environment. Return a list of issues.
    """

    eslint_command = os.environ.get('TM_JAVASCRIPT_ESLINT_ESLINT', 'eslint')
    the_validator = validator.Validator(eslint_command)

    filename = os.environ.get('TM_FILEPATH', None)
    input_is_html = not os.environ['TM_SCOPE'].startswith('source.js')
    line_offset = int(os.environ.get('TM_INPUT_START_LINE', 1)) - 1
    cwd = get_cwd()

    try:
        issues = the_validator.run(
            filename=filename,
            input_is_html=input_is_html,
            line_offset=line_offset,
            cwd=cwd
        )
    except validator.ValidateError as err:
        context = {
            'BASE_PATH': BASE_PATH,
            'timestamp': time.strftime('%c'),
            'errorMessage': err.message,
        }
        if err.path:
            context['searchPath'] = err.path
            html = ASHES_ENV.render('error_eslint_path.html', context)
        else:
            html = ASHES_ENV.render('error_eslint_other.html', context)
        print(html)
        sys.exit()

    return issues

def full_report():
    """ Run ESLint and output an HTML report. """

    issues = validate()

    context = {
        'BASE_PATH': BASE_PATH,
        'issues': issues,
        'targetFilename': '(current unsaved file)',
        'targetUrl': 'txmt://open?line=1&amp;column=0'
    }

    if 'TM_FILEPATH' in os.environ:
        context['targetFilename'] = os.path.relpath(os.environ['TM_FILEPATH'], get_cwd())
        context['targetUrl'] = 'txmt://open?url=file://%s' % os.environ['TM_FILEPATH']

    error_count = 0
    warning_count = 0

    for issue in issues:
        if issue['isError']:
            error_count += 1
        if issue['isWarning']:
            warning_count += 1

    context['hasErrorsOrWarnings'] = error_count + warning_count > 0

    if error_count == 1:
        context['errorCountString'] = '1 error'
    elif error_count:
        context['errorCountString'] = '%s errors' % error_count

    if warning_count == 1:
        context['warningCountString'] = '1 warning'
    elif warning_count:
        context['warningCountString'] = '%s warnings' % warning_count

    html = ASHES_ENV.render('report.html', context)
    print(html)


def quiet():
    """ Run ESLint and display a summary of the results as a tooltip. """

    issues = validate()
    update_gutter_marks(issues)

    error_count = 0
    warning_count = 0

    for issue in issues:
        if should_ignore(issue['reason']):
            continue
        if issue['isError']:
            error_count += 1
        if issue['isWarning']:
            warning_count += 1

    parts = []
    if error_count:
        parts.append('{0} error{1}'.format(error_count, 's' if error_count > 1 else ''))
    if warning_count > 0:
        parts.append('{0} warning{1}'.format(warning_count, 's' if warning_count > 1 else ''))
    result = ', '.join(parts)
    if result:
        result += '\r\rPress Shift-Ctrl-V to view the full report.'
    print(result)


def update_gutter_marks(issues):
    """
    Update the gutter marks in TextMate that indicate an issue on a
    particular line.
    """
    mate = os.environ['TM_MATE']
    file_path = os.environ['TM_FILEPATH']

    marks = []

    for item in issues:
        if should_ignore(item['reason']):
            continue
        msg = item['reason']
        if 'shortname' in item:
            msg += ' ({0})'.format(item['shortname'])
        pos = '{0}:{1}'.format(item['line'] or 1, item['character'])
        marks.append((msg, pos))

    subprocess.call([mate, '--clear-mark=warning', file_path])

    # set the gutter marks 10 at a time to improve performance
    # the choice of 10 is arbitrary -- enough to improve performance
    # but shouldn’t cause the cmd line to be too long

    def chunks(list_to_chunk, chunk_size):
        """
        Yield successive chunk_size-sized chunks from list_to_chunk.
        """
        for i in xrange(0, len(list_to_chunk), chunk_size):
            yield list_to_chunk[i:i + chunk_size]

    for chunk in list(chunks(marks, 10)):
        args = [mate]
        for mark in chunk:
            args.append('--set-mark=warning:[ESLint] {0}'.format(mark[0]))
            args.append('--line={0}'.format(mark[1]))
        args.append(file_path)
        subprocess.call(args)


def fix():
    """ Run the eslint --fix command against the current file. """
    if 'TM_FILEPATH' not in os.environ:
        # ignore if file is not saved
        return

    if not os.environ['TM_SCOPE'].startswith('source.js'):
        # refuse to run against HTML-embedded JavaScript
        return

    eslint_command = os.environ.get('TM_JAVASCRIPT_ESLINT_ESLINT', 'eslint')
    the_validator = validator.Validator(eslint_command)
    filename = os.environ['TM_FILEPATH']
    cwd = get_cwd()

    try:
        the_validator.fix(filename, cwd)
    except validator.ValidateError as err:
        context = {
            'BASE_PATH': BASE_PATH,
            'timestamp': time.strftime('%c'),
            'errorMessage': err.message,
        }
        if err.path:
            context['searchPath'] = err.path
            html = ASHES_ENV.render('error_eslint_path.html', context)
        else:
            html = ASHES_ENV.render('error_eslint_other.html', context)
        print(html)
        sys.exit()

    mate = os.environ['TM_MATE']
    subprocess.call([mate, '--clear-mark=warning', filename])


if __name__ == '__main__':
    if '--html' in sys.argv:
        full_report()
    elif '--fix' in sys.argv:
        fix()
    else:
        quiet()
