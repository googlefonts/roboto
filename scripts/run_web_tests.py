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

"""Test assumptions that web fonts rely on."""

import unittest
from nototools.unittests import font_tests

import run_general_tests


FONTS = font_tests.load_fonts(
    ['out/web/*.ttf'],
    expected_count=18)


class TestItalicAngle(run_general_tests.TestItalicAngle):
    loaded_fonts = FONTS


class TestMetaInfo(font_tests.TestMetaInfo):
    loaded_fonts = FONTS
    mark_heavier_as_bold = False

    # Since different font files are hinted at different times, the actual
    # outlines differ slightly. So we are keeping the version numbers as a hint.
    test_version_numbers = None

    # fsType of 0 marks the font free for installation, embedding, etc.
    expected_os2_fsType = 0
    expected_os2_achVendID = 'GOOG'


class TestNames(run_general_tests.TestNames):
    """Bugs:
    https://github.com/google/roboto/issues/37
    """

    loaded_fonts = FONTS

    def expected_unique_id(self, family, style):
        expected = family
        if style != 'Regular':
            expected += ' ' + style
        return expected


class TestDigitWidths(font_tests.TestDigitWidths):
    loaded_fonts = FONTS
    # disable this test while *.frac and *superior glyphs are separate
    # the webfont glyph subset contains *.frac but not *superior
    test_superscript_digits = False


class TestCharacterCoverage(font_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    include = frozenset([
        0xEE01, 0xEE02, 0xF6C3])  # legacy PUA

    exclude = frozenset([
        0x2072, 0x2073, 0x208F] +  # unassigned characters
        range(0xE000, 0xF8FF + 1) + range(0xF0000, 0x10FFFF + 1)  # other PUA
        ) - include  # don't exclude legacy PUA


class TestVerticalMetrics(font_tests.TestVerticalMetrics):
    loaded_fonts = FONTS

    # tests yMin and yMax to be equal to Roboto v1 values
    # android requires this, and web fonts expect this
    expected_head_yMin = -555
    expected_head_yMax = 2163

    # test ascent, descent, and lineGap to be equal to Roboto v1 values
    expected_hhea_descent = -500
    expected_hhea_ascent = 1900
    expected_hhea_lineGap = 0

    # test OS/2 vertical metrics to be equal to the old values
    expected_os2_sTypoDescender = -512
    expected_os2_sTypoAscender = 1536
    expected_os2_sTypoLineGap = 102
    expected_os2_usWinDescent = 512
    expected_os2_usWinAscent = 1946


class TestLigatures(run_general_tests.TestLigatures):
    loaded_fonts = FONTS


class TestGlyphBounds(run_general_tests.TestGlyphBounds):
    loaded_fonts = FONTS

    # a bug in which monotonic and polytonic glyphs extend too far left is
    # fixed in the unhinted output, but still present in the hinted binaries and
    # not fixed by the web target
    should_not_exceed = ()


class TestHints(font_tests.TestHints):
    loaded_fonts = FONTS


if __name__ == '__main__':
    unittest.main()
