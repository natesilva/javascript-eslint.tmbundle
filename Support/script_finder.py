#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Given HTML input, return only the content found between
<script>…</script> tags.
"""

import re

def only_scripts(input_iterable):
    """
    Given HTML input, transform it by removing all content that is
    not part of a script (between <script>…</script> tags).

    Any non-script content is blanked out. The number of lines
    returned is identical to the number of lines in the input so
    line-number-based error messages will still be accurate.

    input_iterable -- must be iterable
    """
    lines = []
    start_tag = re.compile(r'(\<\s*script)[\s\>]', re.IGNORECASE)
    end_tag = re.compile(r'\<\/\s*script[\s\>]', re.IGNORECASE)
    state = 'IGNORE'
    for line in input_iterable:
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
                    line_part = line[:match.start()]
                    # if line is all whitespace, strip it
                    if len(line_part.strip()) == 0:
                        line_part = '\n'
                    lines.append(line_part)
                    line = line[match.end():]
                    state = 'IGNORE'
                else:
                    # if line is all whitespace, strip it
                    if len(line.strip()) == 0:
                        line = '\n'
                    lines.append(line)
                    line = None
    return lines
