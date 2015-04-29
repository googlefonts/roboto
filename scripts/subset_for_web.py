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


if __name__ == '__main__':
    main(sys.argv)
