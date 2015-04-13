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

"""Post-subset changes for Roboto for Android."""

import sys

from fontTools import ttLib

from nototools import font_data


def output_protruding_glyphs(font, ymin, ymax):
    """Outputs all glyphs going outside the specified vertical range."""
    protruding_glyphs = []
    glyf_table = font['glyf']
    for glyph_name in glyf_table.keys():
        glyph = glyf_table[glyph_name]
        if glyph.numberOfContours == 0:
            continue
        if glyph.yMin < ymin or glyph.yMax > ymax:
            protruding_glyphs.append(glyph_name)
    if protruding_glyphs:
        print "Protruding glyphs in %s:" % font_data.font_name(font),
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
    output_protruding_glyphs(font, YMIN, YMAX)

    font.save(target_font_name)

    # Make sure the values are set correctly
    font = ttLib.TTFont(target_font_name, recalcBBoxes=False)
    head = font['head']
    assert head.yMin == YMIN and head.yMax == YMAX


if __name__ == "__main__":
    main(sys.argv)
