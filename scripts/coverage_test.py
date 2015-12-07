#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Routines for checking character coverage of Roboto fonts.

This scripts takes the name of the directory where the fonts are and checks
that they cover all characters required in the Roboto extension contract.

The data is in res/char_requirements.tsv.
"""

__author__ = (
    "roozbeh@google.com (Roozbeh Pournader) and "
    "cibu@google.com (Cibu Johny)")

import sys

import glob

from fontTools import ttLib
from nototools import coverage
from nototools import font_data
from nototools import unicode_data


def load_fonts():
    """Load all fonts built for Android."""
    all_fonts = (glob.glob('out/RobotoTTF/*.ttf')
                 + glob.glob('out/RobotoCondensedTTF/*.ttf'))
    all_fonts = [ttLib.TTFont(font) for font in all_fonts]
    return all_fonts


def _character_name(code):
    """Returns the printable name of a character."""
    return unicode_data.name(unichr(code), '<Unassigned>')


def _print_char(code, additional_info=None):
    """Print a Unicode character as code and name and perhaps extra info."""
    sys.stdout.write('U+%04X %s' % (code, _character_name(code)))

    if additional_info is not None:
        sys.stdout.write('\t' + additional_info)

    sys.stdout.write('\n')


def _range_string_to_set(range_str):
    """Convert a range encoding in a string to a set."""
    if '..' in range_str:
        range_start, range_end = range_str.split('..')
        range_start = int(range_start, 16)
        range_end = int(range_end, 16)
        return set(range(range_start, range_end+1))
    else:
        return {int(range_str, 16)}


def _multiple_range_string_to_set(ranges_str):
    """Convert a string of multiple ranges to a set."""
    char_set = set()
    for range_str in ranges_str.split(', '):
        if range_str.startswith('and '):
            range_str = range_str[4:]  # drop the 'and '
        char_set.update(_range_string_to_set(range_str))
    return char_set


def _defined_characters_in_range(range_str):
    """Given a range string, returns defined Unicode characters in the range."""
    characters = set()
    for code in _range_string_to_set(range_str):
        if unicode_data.is_defined(code) and unicode_data.age(code) is not None:
            characters.add(code)
    return characters


_EXCEPTION_STARTER = 'Everything except '


def _find_required_chars(block_range, full_coverage_required, exceptions):
    """Finds required coverage based on a row of the spreadsheet."""
    chars_defined_in_block = _defined_characters_in_range(block_range)
    if full_coverage_required:
        return chars_defined_in_block
    else:
        if not exceptions:
            return set()
        if exceptions.startswith(_EXCEPTION_STARTER):
            exceptions = exceptions[len(_EXCEPTION_STARTER):]
            chars_to_exclude = _multiple_range_string_to_set(exceptions)
            return chars_defined_in_block - chars_to_exclude
        else:
            chars_to_limit_to = _multiple_range_string_to_set(exceptions)
            return chars_defined_in_block & chars_to_limit_to


def main():
    """Checkes the coverage of all Roboto fonts."""
    with open('res/char_requirements.tsv') as char_reqs_file:
        char_reqs_data = char_reqs_file.read()

    # The format of the data to be parsed is like the following:
    # General Punctuation\t2000..206F\t111\t35\t54\t0\tEverything except 2028..202E, 2060..2064, and 2066..206F
    # Currency Symbols\t20A0..20CF\t29\t5\t24\t1\t
    required_set = set()
    for line in char_reqs_data.split('\n'):
        if line.startswith('#'):  # Skip comment lines
            continue
        line = line.split('\t')
        if not line[0]:
            continue  # Skip the first line and empty lines
        block_range = line[1]
        full_coverage_required = (line[5] == '1')
        exceptions = line[6]
        required_set.update(
            _find_required_chars(block_range,
                                 full_coverage_required,
                                 exceptions))

    # Skip Unicode 8.0 characters
    required_set = {ch for ch in required_set
                    if float(unicode_data.age(ch)) <= 7.0}

    # Skip ASCII and C1 controls
    required_set -= set(range(0, 0x20) + range(0x7F, 0xA0))

    missing_char_found = False
    for font in load_fonts():
        font_coverage = coverage.character_set(font)
        missing_chars = required_set - font_coverage
        if missing_chars:
            missing_char_found = True
            font_name = font_data.font_name(font)
            print 'Characters missing from %s:' % font_name
            for char in sorted(missing_chars):
                _print_char(char)
            print

    if missing_char_found:
        sys.exit(1)

if __name__ == '__main__':
    main()
