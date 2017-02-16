#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run ESLint and return structured results.
"""

import os
import sys
import subprocess
import re
from script_finder import only_scripts

class ValidateError(Exception):
    """ Report a validation error. """
    def __init__(self, message, path=None):
        super(self.__class__, self).__init__(message)
        self.message = message
        self.path = path

    def __str__(self):
        return repr(self.message)

class Validator(object):
    """
    Run ESLint and return structured results.
    """

    def __init__(self, eslint_command='eslint'):
        """
        Initialize a new Validator.

        eslint_command -- the eslint command to run
        """
        self.eslint_command = eslint_command


    def fix(self, filename, cwd):
        """
        Run the eslint --fix command.
        """
        env = os.environ.copy()
        env['PATH'] = Validator.get_path()

        args = [
            self.eslint_command,
            '--fix',
            filename
        ]

        try:
            subprocess.call(args, env=env, cwd=cwd)
        except OSError as err:
            raise ValidateError(err.__str__(), env['PATH'])


    def run(self, input_iterable=sys.stdin, filename=None, input_is_html=False,
            line_offset=0, cwd=None):
        """
        Run the validator.

        input_iterable -- what to stream to ESLint (default: stdin)
        filename -- if passed, it is used in report messages
        input_is_html -- if True, only validates stuff inside
            <script>…</script> tags
        line_offset -- if the input_iterable is not the entire file,
            this is used to correct the line numbers
        cwd -- the project directory, or the file’s directory if no
            project is open; used by eslint to find its config
        """

        env = os.environ.copy()
        env['PATH'] = Validator.get_path()

        args = [
            self.eslint_command,
            '-f',
            'compact',
            '--no-color',
            '--stdin'
        ]

        # if we know the filename, pass it
        if filename:
            args.append('--stdin-filename')
            args.append(os.path.relpath(filename, cwd))

        try:
            eslint = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=cwd
            )
        except OSError as err:
            raise ValidateError(err.message, env['PATH'])

        if input_is_html:
            input_iterable = only_scripts(input_iterable)

        (stdout, stderr) = eslint.communicate(''.join(input_iterable))

        if stderr:
            raise ValidateError(stderr)

        return Validator.parse_results(stdout, line_offset, filename)

    @classmethod
    def parse_results(cls, results, line_offset=0, filename=None):
        """
        Parse the stdout after running ESLint. Returns a list of
        detected issues.
        """
        rxp = re.compile(
            r'^[^:]+\: line (?P<line>\d+), col (?P<character>\d+), ' +
            r'(?P<code>\w+) - (?P<reason>.+?)(\s\((?P<shortname>[\w\-]+)\))?$'
        )

        issues = []

        for line in results.split('\n'):
            line = line.strip()
            if not line:
                continue

            match = rxp.match(line)

            if not match:
                continue

            issue = {
                'isError': match.group('code')[0] == 'E',
                'isWarning': match.group('code')[0] == 'W',
                'line': int(match.group('line')),
                'character': int(match.group('character')) + 1,
                'reason': match.group('reason')
            }

            if match.group('shortname'):
                issue['shortname'] = match.group('shortname')

            issues.append(issue)

        # normalize line numbers
        for issue in issues:
            issue['line'] += line_offset


        # add URLs to the issues
        if filename:
            url_maker = lambda x: \
                'txmt://open?url=file://%s&line=%d&column=%d' % \
                (filename, x['line'], x['character'])
        else:
            url_maker = lambda x: \
                'txmt://open?line=%d&column=%d' % (x['line'], x['character'])

        for issue in issues:
            issue['url'] = url_maker(issue)

        return issues

    @classmethod
    def get_path(cls):
        """ Return the value to be used as the PATH setting. """
        # ESLint (and Node) are often installed to /usr/local/bin,
        # which may not be on the bundle’s PATH in a default install
        # of TextMate.
        path_parts = os.environ.get('PATH', []).split(':')

        node_path = os.environ.get('NODE_PATH', None)
        if node_path:
            path_parts.extend(node_path.split(':'))

        # pre-pend project-specific node_modules/.bin if it exists
        project_dir = os.environ.get('TM_PROJECT_DIRECTORY', None)
        if project_dir:
            node_bin = os.path.join(project_dir, 'node_modules', '.bin')
            if node_bin not in path_parts:
                path_parts.insert(0, node_bin)

        if '/bin' not in path_parts:
            path_parts.append('/bin')
        if '/usr/bin' not in path_parts:
            path_parts.append('/usr/bin')
        if '/usr/local/bin' not in path_parts:
            path_parts.append('/usr/local/bin')

        return ':'.join(path_parts)
