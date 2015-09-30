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

from nototools import font_data

import common_tests

FONTS = common_tests.load_fonts(
    ['out/web/*.ttf'],
    expected_count=18)

class TestItalicAngle(common_tests.TestItalicAngle):
    loaded_fonts = FONTS


class TestMetaInfo(common_tests.TestMetaInfo):
    loaded_fonts = FONTS
    mark_heavier_as_bold = True
    # Since different font files are hinted at different times, the actual
    # outlines differ slightly. So we are keeping the version numbers as a hint.
    test_version_numbers = None


class TestNames(common_tests.TestNames):
    loaded_fonts = FONTS
    family_name = 'Roboto'
    mark_heavier_as_bold = True


class TestDigitWidths(common_tests.TestDigitWidths):
    loaded_fonts = FONTS
    # disable this test while *.frac and *superior glyphs are separate
    # the webfont glyph subset contains *.frac but not *superior
    test_superscript_digits = False


class TestCharacterCoverage(common_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    include = frozenset([
        0xEE01, 0xEE02, 0xF6C3])  # legacy PUA

    exclude = frozenset([
        0x2072, 0x2073, 0x208F] +  # unassigned characters
        range(0xE000, 0xF8FF + 1) + range(0xF0000, 0x10FFFF + 1)  # other PUA
        ) - include  # don't exclude legacy PUA


class TestVerticalMetrics(common_tests.TestVerticalMetrics):
    loaded_fonts = FONTS

    def test_os2_metrics(self):
        """Tests OS/2 vertical metrics to be equal to the old values."""
        for font in self.fonts:
            os2_table = font['OS/2']
            self.assertEqual(os2_table.sTypoDescender, -512)
            self.assertEqual(os2_table.sTypoAscender, 1536)
            self.assertEqual(os2_table.sTypoLineGap, 102)
            self.assertEqual(os2_table.usWinDescent, 512)
            self.assertEqual(os2_table.usWinAscent, 1946)


class TestLigatures(common_tests.TestLigatures):
    loaded_fonts = FONTS


class TestHints(unittest.TestCase):
    """Tests hints."""

    def setUp(self):
        self.fontfiles, self.fonts = FONTS

    def test_existance_of_hints(self):
        """Tests all glyphs and makes sure non-composite ones have hints."""
        missing_hints = []
        for font in self.fonts:
            glyf_table = font['glyf']
            for glyph_name in font.getGlyphOrder():
                glyph = glyf_table[glyph_name]
                if glyph.numberOfContours <= 0:  # composite or empty glyph
                    continue
                if len(glyph.program.bytecode) <= 0:
                    missing_hints.append(
                        (glyph_name, font_data.font_name(font)))

        self.assertTrue(missing_hints == [])

    def test_height_of_lowercase_o(self):
        """Tests the height of the lowercase o in low resolutions."""
        for fontfile in self.fontfiles:
            for size in range(8, 30):  # Kind of arbitrary
                o_height = common_tests.get_rendered_char_height(
                    fontfile, size, 'o')
                n_height = common_tests.get_rendered_char_height(
                    fontfile, size, 'n')
                self.assertEqual(o_height, n_height)


if __name__ == '__main__':
    unittest.main()

