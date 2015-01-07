#!/usr/bin/python
"""Post-build web fonts changes for Roboto."""

import sys

from fontTools import ttLib
from nototools import font_data

import temporary_touchups


def apply_web_specific_fixes(font, family_name):
    """Apply fixes needed for web fonts."""
    # Set ascent, descent, and lineGap values to Android K values
    hhea = font['hhea']
    hhea.ascent = 1900
    hhea.descent = -500
    hhea.lineGap = 0

    os2 = font['OS/2']
    os2.sTypoAscender = 1536
    os2.sTypoDescender = -512
    os2.sTypoLineGap = 102
    os2.usWinAscent = 1946
    os2.usWinDescent = 512

    subfamily_name = font_data.get_name_records(font)[2].encode('ASCII')
    assert(subfamily_name in
        ['Thin', 'Thin Italic',
         'Light', 'Light Italic',
         'Regular', 'Italic',
         'Medium', 'Medium Italic',
         'Bold', 'Bold Italic',
         'Black', 'Black Italic'])
    full_name = family_name + ' ' + subfamily_name
    year = '2014'

    # Copyright message
    font_data.set_name_record(
        font, 0, 'Copyright %s Google Inc. All Rights Reserved.' % year)

    # Family name
    font_data.set_name_record(font, 1, family_name)
    font_data.set_name_record(font, 16, family_name)

    # Unique identifier and full name
    font_data.set_name_record(font, 3, full_name)
    font_data.set_name_record(font, 4, full_name)
    font_data.set_name_record(font, 18, None)

    # PostScript name
    font_data.set_name_record(
        font, 6, family_name+'-'+subfamily_name.replace(' ', ''))


def correct_font(source_font_name, target_font_name, family_name):
    """Corrects metrics and other meta information."""
    font = ttLib.TTFont(source_font_name)
    temporary_touchups.apply_temporary_fixes(font)
    apply_web_specific_fixes(font, family_name)
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(argv[1], argv[2], argv[3])


if __name__ == "__main__":
    main(sys.argv)
