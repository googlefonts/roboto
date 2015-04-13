#!/usr/bin/python
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

"""Post-build changes for Glass."""

import os
from os import path
import sys

from fontTools import ttLib
from nototools import font_data


def apply_glass_hacks(font):
    """Apply glass-specific hacks to a fonttools font instance."""
    # Really ugly hack, expecting the proportional digit one to be at
    # glyph01965.
    font_data.add_to_cmap(font, {0xEE00: 'glyph01965'})

    # Fix version number from buildnumber.txt
    from datetime import date

    build_number_txt = path.join(
        path.dirname(__file__), os.pardir, 'res', 'buildnumber.txt')
    build_number = open(build_number_txt).read().strip()

    version_record = 'Version 2.0%s; %d; Glass' % (
        build_number, date.today().year)

    for record in font['name'].names:
        if record.nameID == 5:
            if record.platformID == 1 and record.platEncID == 0:  # MacRoman
                record.string = version_record
            elif record.platformID == 3 and record.platEncID == 1:
                # Windows UCS-2
                record.string = version_record.encode('UTF-16BE')
            else:
                assert False


def hack_font(source_font_name, target_font_name):
    """Hacks the source font and saves it as the target."""
    font = ttLib.TTFont(source_font_name)
    apply_glass_hacks(font)
    font.save(target_font_name)


def main(argv):
    """Hack the font specified in the command line."""
    hack_font(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
