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

"""Test assumptions that Android relies on."""

import unittest
from nototools.unittests import font_tests

import run_general_tests


FONTS = font_tests.load_fonts(
    ['out/android/*.ttf'],
    expected_count=20)


class TestItalicAngle(run_general_tests.TestItalicAngle):
    loaded_fonts = FONTS


class TestMetaInfo(run_general_tests.TestMetaInfo):
    """Bugs:
    https://github.com/google/roboto/issues/142
    """

    loaded_fonts = FONTS
    mark_heavier_as_bold = True

    def test_glyphs_dont_round_to_grid(self):
        """Bug: https://github.com/google/roboto/issues/153"""

        for font in self.fonts:
            glyph_set = font.getGlyphSet()

            # only concerned with this glyph for now, but maybe more later
            for name in ['ellipsis']:
                glyph = glyph_set[name]._glyph
                for component in glyph.components:
                    self.assertFalse(component.flags & (1 << 2))


class TestNames(run_general_tests.TestNames):
    """Bugs:
    https://github.com/google/roboto/issues/37
    """

    loaded_fonts = FONTS


class TestVerticalMetrics(font_tests.TestVerticalMetrics):
    loaded_fonts = FONTS
    test_os2_metrics = None

    # tests yMin and yMax to be equal to Roboto v1 values
    # android requires this, and web fonts expect this
    expected_head_yMin = -555
    expected_head_yMax = 2163

    # test ascent, descent, and lineGap to be equal to Roboto v1 values
    expected_hhea_descent = -500
    expected_hhea_ascent = 1900
    expected_hhea_lineGap = 0


class TestDigitWidths(font_tests.TestDigitWidths):
    loaded_fonts = FONTS


class TestCharacterCoverage(font_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    include = frozenset([
        0x2117,  # SOUND RECORDING COPYRIGHT
        0xEE01, 0xEE02, 0xF6C3])  # legacy PUA

    exclude = frozenset([
        0x20E3,  # COMBINING ENCLOSING KEYCAP
        0x2191,  # UPWARDS ARROW
        0x2193,  # DOWNWARDS ARROW
        0x2072, 0x2073, 0x208F] +  # unassigned characters
        range(0xE000, 0xF8FF + 1) + range(0xF0000, 0x10FFFF + 1)  # other PUA
        ) - include  # don't exclude legacy PUA


class TestLigatures(run_general_tests.TestLigatures):
    loaded_fonts = FONTS


if __name__ == '__main__':
    unittest.main()
