#!/usr/bin/python
"""Post-build touch ups for Roboto."""

from os import path
import sys

from fontTools import ttLib


def correct_font(source_font_name, target_font_name):
    """Corrects metrics and other meta information."""
    font = ttLib.TTFont(source_font_name)
    
    head = font['head']
    head.yMax = 2163
    head.yMin = -555
    
    hhea = font['hhea']
    hhea.ascent = 1900
    hhea.descent = -500
    hhea.lineGap = 0
    
    basename = path.basename(source_font_name)
    bold = ('Bold' in basename) or ('Black' in basename)
    italic = 'Italic' in basename
    head.macStyle = (italic << 1) | bold
    
    font.save(target_font_name)


def main(argv):
    """Correct all fonts specified in the command line."""
    for font_name in argv[1:]:
        correct_font(font_name, path.basename(font_name))


if __name__ == "__main__":
    main(sys.argv)
