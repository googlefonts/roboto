#!/usr/bin/python
"""Post-build changes for Roboto for Android."""

import sys

from fontTools import ttLib
from nototools import font_data

import temporary_touchups


def apply_android_specific_fixes(font):
    """Apply fixes needed for Android."""
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
    temporary_touchups.update_version_and_revision(font)
    apply_android_specific_fixes(font)
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
