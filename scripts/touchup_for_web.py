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

"""Post-build web fonts changes for Roboto."""

import sys

from fontTools import ttLib
from nototools import font_data

import temporary_touchups


def apply_web_specific_fixes(font, unhinted, family_name):
    """Apply fixes needed for web fonts."""

    # set vertical metrics to old values
    hhea = font['hhea']
    hhea.ascent = 1900
    hhea.descent = -500

    os2 = font['OS/2']
    os2.sTypoAscender = 1536
    os2.sTypoDescender = -512
    os2.sTypoLineGap = 102
    os2.usWinAscent = 1946
    os2.usWinDescent = 512

    # correct anything else needed for both web and Chrome OS
    apply_web_cros_common_fixes(font, unhinted, family_name)


def apply_web_cros_common_fixes(font, unhinted, family_name):
    """Apply fixes needed for web and CrOS targets"""
    subfamily_name = font_data.get_name_records(font)[2].encode('ASCII')
    assert(subfamily_name in
        ['Thin', 'Thin Italic',
         'Light', 'Light Italic',
         'Regular', 'Italic',
         'Medium', 'Medium Italic',
         'Bold', 'Bold Italic',
         'Black', 'Black Italic'])

    if 'Condensed' in font_data.get_name_records(font)[1]:
        family_name += ' Condensed'
    full_name = family_name
    if subfamily_name != 'Regular':
        full_name += ' ' + subfamily_name

    # Family, subfamily names
    font_data.set_name_record(font, 16, family_name)
    style_map = ['Regular', 'Bold', 'Italic', 'Bold Italic']
    if subfamily_name in style_map:
        font_data.set_name_record(font, 1, family_name)
    else:
        weight = subfamily_name.split()[0]
        new_family_name = family_name
        if weight != 'Regular':
            new_family_name += ' ' + weight
        font_data.set_name_record(font, 1, new_family_name)

        # all weights outside regular and bold should only have subfamily
        # "Regular" or "Italic"
        italic = subfamily_name.endswith('Italic')
        font_data.set_name_record(font, 2, style_map[italic << 1])

    # Unique identifier and full name
    font_data.set_name_record(font, 3, full_name)
    font_data.set_name_record(font, 4, full_name)
    font_data.set_name_record(font, 18, None)

    # PostScript name
    font_data.set_name_record(
        font, 6, (family_name+'-'+subfamily_name).replace(' ', ''))

    # Copyright message
    font_data.set_name_record(
        font, 0, 'Copyright 2011 Google Inc. All Rights Reserved.')

    # hotpatch glyphs by swapping
    # https://github.com/google/roboto/issues/18
    glyf = font['glyf']
    glyf['chi'], glyf['chi.alt'] = glyf['chi.alt'], glyf['chi']

    # make glyph orders consistent for feature copying
    # https://github.com/google/roboto/issues/71
    glyph_order = font.getGlyphOrder()
    for i, glyph_name in enumerate(glyph_order):
        if glyph_name.endswith('.lnum'):
            new_name = glyph_name.replace('.lnum', '.pnum')
            glyph_order[i] = new_name
            font['glyf'][new_name] = font['glyf'][glyph_name]

            # append old name to glyph order so del succeeds
            glyph_order.append(glyph_name)
            del font['glyf'][glyph_name]

    # copy features from unhinted
    # https://github.com/google/roboto/pull/163
    for table in ['GDEF', 'GPOS', 'GSUB']:
        font[table] = unhinted[table]


def correct_font(source_name, unhinted_name, target_font_name, family_name):
    """Corrects metrics and other meta information."""

    font = ttLib.TTFont(source_name)
    unhinted = ttLib.TTFont(unhinted_name)

    # apply web-specific fixes before shared, so that sub/family names are
    # correct for black weights and their bold bits will be set
    apply_web_specific_fixes(font, unhinted, family_name)
    temporary_touchups.apply_temporary_fixes(font, is_for_web=True)
    temporary_touchups.update_version_and_revision(font)
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(*argv[1:])


if __name__ == "__main__":
    main(sys.argv)
