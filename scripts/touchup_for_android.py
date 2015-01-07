#!/usr/bin/python
"""Post-build changes for Roboto for Android."""

import collections
import os
from os import path
import sys

from fontTools import ttLib
from nototools import font_data
from nototools import unicode_data

import temporary_touchups


def drop_lookup(table, lookup_number):
    """Drop a lookup from an OpenType table by number.

    Actually remove pointers from features to the lookup, which should be less
    intrusive.
    """
    for feature in table.table.FeatureList.FeatureRecord:
        if lookup_number in feature.Feature.LookupListIndex:
            feature.Feature.LookupListIndex.remove(lookup_number)
            feature.Feature.LookupCount -= 1


def apply_temporary_fixes(font):
    """Apply some temporary fixes.
    """
    # Fix version number from buildnumber.txt
    # https://code.google.com/a/google.com/p/roboto/issues/detail?id=50
    from datetime import date

    build_number_txt = path.join(
        path.dirname(__file__), os.pardir, 'res', 'buildnumber.txt')
    build_number = open(build_number_txt).read().strip()

    version_record = 'Version 2.0%s; %d' % (build_number, date.today().year)

    for record in font['name'].names:
        if record.nameID == 5:
            if record.platformID == 1 and record.platEncID == 0:  # MacRoman
                record.string = version_record
            elif record.platformID == 3 and record.platEncID == 1:
                # Windows UCS-2
                record.string = version_record.encode('UTF-16BE')
            else:
                assert False


def apply_android_specific_fixes(font):
    """Apply fixes needed for Android."""
    # Set ascent, descent, and lineGap values to Android K values
    hhea = font['hhea']
    hhea.ascent = 1900
    hhea.descent = -500
    hhea.lineGap = 0

    # Remove tab, combining keycap, and the arrows from the cmap table.
    #
    # Arrows are removed to maximize consistency of arrows, since the rest
    # of the arrows come from Noto Symbols.
    #
    # And here are the bugs for the other two issues:
    # https://code.google.com/a/google.com/p/roboto/issues/detail?id=51
    # https://code.google.com/a/google.com/p/roboto/issues/detail?id=52
    font_data.delete_from_cmap(font, [
        0x0009, # tab
        0x20E3, # combining keycap
        0x2191, 0x2193, # vertical arrows
    ])

    # Drop tables not useful on Android
    for table in ['LTSH', 'hdmx', 'VDMX', 'gasp']:
        if table in font:
            del font[table]


def correct_font(source_font_name, target_font_name):
    """Corrects metrics and other meta information."""
    font = ttLib.TTFont(source_font_name)
    temporary_touchups.apply_temporary_fixes(font)
    apply_android_specific_fixes(font)
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
