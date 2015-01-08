#!/usr/bin/python
# coding=UTF-8
#
# Copyright 2014 Google Inc. All rights reserved.
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

"""Subset for web fonts."""

__author__ = 'roozbeh@google.com (Roozbeh Pournader)'

import sys

from nototools import subset


def read_charlist(filename):
    """Returns a list of characters read from a charset text file."""
    with open(filename) as datafile:
        charlist = []
        for line in datafile:
            if '#' in line:
                line = line[:line.index('#')]
            line = line.strip()
            if not line:
                continue
            if line.startswith('U+'):
                line = line[2:]
            char = int(line, 16)
            charlist.append(char)
        return charlist

LATIN = (
    range(0x0020, 0x007F) + range(0x00A0, 0x0100) +
    [0x0131, 0x0152, 0x0153, 0x02C6, 0x02DA, 0x02DC, 0x2013, 0x2014, 0x2018,
     0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2022, 0x2039, 0x203A, 0x2044,
     0x2074, 0x20AC, 0x2212, 0x2215])

CYRILLIC = range(0x0400, 0x0460) + [0x0490, 0x0491, 0x04B0, 0x04B1, 0x2116]

SUBSETS = {
    'cyrillic': LATIN + CYRILLIC,
    'cyrillic-ext': (
        LATIN + CYRILLIC + range(0x0460, 0x0530) + [0x20B4] +
        range(0x2DE0, 0x2E00) + range(0xA640, 0xA6A0)),
    'greek': LATIN + range(0x0384, 0x0400),
#    'greek-ext': LATIN + range(0x0384, 0x0400) + range(0x1F00, 0x2000),
    'latin': LATIN,
    'latin-ext': (
        LATIN + range(0x0100, 0x0250) +
        [0x02BC, 0x0300, 0x0301, 0x0303, 0x030F] +
        range(0x1E00, 0x1F00) +
        [0x2026, 0x2070, 0x2075, 0x2076, 0x2077, 0x2078, 0x2079, 0x207F] +
        range(0x20A0, 0x20D0) + range(0x2C60, 0x2C80) +
        range(0xA720, 0xA800)),
    'menu': [ord(c) for c in u' ()DNQRabcfgortu΄ΕάαεηικλνКаилрцốữ'],
}
SUBSETS = {k: frozenset(v) for k, v in SUBSETS.iteritems()}


def main(argv):
    """Subset the first argument to second, dropping unused parts of the font.
    """
    charlist = read_charlist('res/charsets/web.txt')
    # Add private use characters for legacy reasons
    charlist += [0xEE01, 0xEE02, 0xF6C3]

    features_to_keep = [
        'c2sc', 'ccmp', 'cpsp', 'dlig', 'dnom', 'frac', 'kern', 'liga', 'lnum',
        'locl', 'numr', 'onum', 'pnum', 'smcp', 'ss01', 'ss02', 'ss03', 'ss04',
        'ss05', 'ss06', 'ss07', 'tnum']

    source_filename = argv[1]
    target_filename = argv[2]
    subset.subset_font(
        source_filename, target_filename,
        include=charlist,
        options={'layout_features': features_to_keep})

    for suffix in SUBSETS.keys():
        subset_filename = target_filename.replace('ttf', suffix)
        subset.subset_font(
            target_filename, subset_filename,
            include=SUBSETS[suffix])


if __name__ == '__main__':
    main(sys.argv)
