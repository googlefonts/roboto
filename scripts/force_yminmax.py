#!/usr/bin/python
"""Post-subset changes for Roboto for Android."""

import sys

from fontTools import ttLib


def output_protruding_glyphs(font, ymin, ymax, file_name):
    """Outputs all glyphs going outside the specified vertical range."""
    protruding_glyphs = []
    glyph_dict = font['glyf'].glyphs
    for glyph_name, glyph in glyph_dict.items():
        if glyph.numberOfContours == 0:
            continue
        if glyph.yMin < ymin or glyph.yMax > ymax:
            protruding_glyphs.append(glyph_name)
    if protruding_glyphs:
        print "Protruding glyphs in %s:" % file_name,
        print ', '.join(sorted(protruding_glyphs))


YMIN = -555
YMAX = 2163

def main(argv):
    """Forces yMin/yMax values and generates a new font."""
    source_font_name = argv[1]
    target_font_name = argv[2]
    font = ttLib.TTFont(source_font_name, recalcBBoxes=False)

    head = font['head']
    head.yMin = YMIN
    head.yMax = YMAX
    output_protruding_glyphs(font, YMIN, YMAX, source_font_name)

    font.save(target_font_name)

    # Make sure the values are set correctly
    font = ttLib.TTFont(target_font_name, recalcBBoxes=False)
    head = font['head']
    assert head.yMin == YMIN and head.yMax == YMAX


if __name__ == "__main__":
    main(sys.argv)
