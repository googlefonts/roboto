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

"""Post-build changes for Roboto for Android."""

import sys

from fontTools import ttLib
from nototools import font_data

import temporary_touchups


def apply_android_specific_fixes(font):
    """Apply fixes needed for Android."""

    # Remove combining keycap and the arrows from the cmap table:
    # https://github.com/google/roboto/issues/99
    font_data.delete_from_cmap(font, [
        0x20E3, # COMBINING ENCLOSING KEYCAP
        0x2191, # UPWARDS ARROW
        0x2193, # DOWNWARDS ARROW
        ])

    # Drop tables not useful on Android
    for table in ['LTSH', 'hdmx', 'VDMX', 'gasp']:
        if table in font:
            del font[table]

    # Set bold bits for Black (macStyle bit 0, fsSelection bit 5, subfamily)
    name_records = font_data.get_name_records(font)
    family_name = name_records[1]
    subfam_name = name_records[2]
    if family_name.endswith('Black'):
        font['head'].macStyle |= (1 << 0)
        font['OS/2'].fsSelection |= (1 << 5)
        font['OS/2'].fsSelection &= ~(1 << 6)
        new_subfam_name = (
            ('Bold ' + subfam_name) if subfam_name != 'Regular' else 'Bold')
        font_data.set_name_record(font, 2, new_subfam_name)

    # turn off round-to-grid flags in certain problem components
    # https://github.com/google/roboto/issues/153
    glyph_set = font.getGlyphSet()
    ellipsis = glyph_set['ellipsis']._glyph
    for component in ellipsis.components:
        component.flags &= ~(1 << 2)


def correct_font(source_font_name, target_font_name):
    """Corrects metrics and other meta information."""

    font = ttLib.TTFont(source_font_name)
    temporary_touchups.apply_temporary_fixes(font)
    temporary_touchups.update_version_and_revision(font)
    apply_android_specific_fixes(font)
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
