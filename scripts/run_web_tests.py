#!/usr/bin/python
"""Test assumptions that Android relies on."""

import glob
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data


def load_fonts():
    """Load all web fonts."""
    all_font_files = glob.glob('out/web/*.ttf')
    all_fonts = [ttLib.TTFont(font) for font in all_font_files]
    assert len(all_font_files) == 12
    return all_font_files, all_fonts


class TestVerticalMetrics(unittest.TestCase):
    """Test the vertical metrics of fonts."""

    def setUp(self):
        _, self.fonts = load_fonts()

    def test_ymin_ymax(self):
        """Tests yMin and yMax to be equal to the old values."""
        for font in self.fonts:
            head_table = font['head']
            self.assertEqual(head_table.yMin, -555)
            self.assertEqual(head_table.yMax, 2163)

    def test_other_metrics(self):
        """Tests other vertical metrics to be equal to the old values."""
        for font in self.fonts:
            hhea_table = font['hhea']
            self.assertEqual(hhea_table.descent, -500)
            self.assertEqual(hhea_table.ascent, 1900)

            os2_table = font['OS/2']
            self.assertEqual(os2_table.sTypoDescender, -512)
            self.assertEqual(os2_table.sTypoAscender, 1536)
            self.assertEqual(os2_table.sTypoLineGap, 102)
            self.assertEqual(os2_table.usWinDescent, 512)
            self.assertEqual(os2_table.usWinAscent, 1946)


class TestCharacterCoverage(unittest.TestCase):
    """Tests character coverage."""

    def setUp(self):
        _, self.fonts = load_fonts()
        self.LEGACY_PUA = frozenset({0xEE01, 0xEE02, 0xF6C3})

    def test_inclusion_of_legacy_pua(self):
        """Tests that legacy PUA characters remain in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            for char in self.LEGACY_PUA:
                self.assertIn(char, charset)

    def test_non_inclusion_of_other_pua(self):
        """Tests that there are not other PUA characters except legacy ones."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            pua_chars = {
                char for char in charset
                if 0xE000 <= char <= 0xF8FF or 0xF0000 <= char <= 0x10FFFF}
            self.assertTrue(pua_chars <= self.LEGACY_PUA)

    def test_lack_of_unassigned_chars(self):
        """Tests that unassigned characters are not in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertNotIn(0x2072, charset)
            self.assertNotIn(0x2073, charset)
            self.assertNotIn(0x208F, charset)


class TestItalicAngle(unittest.TestCase):
    """Test the italic angle of fonts."""

    def setUp(self):
        _, self.fonts = load_fonts()

    def test_italic_angle(self):
        """Tests the italic angle of fonts to be correct."""
        for font in self.fonts:
            post_table = font['post']
            if 'Italic' in font_data.font_name(font):
                expected_angle = -12.0
            else:
                expected_angle = 0.0
            self.assertEqual(post_table.italicAngle, expected_angle)


class TestDigitWidths(unittest.TestCase):
    """Tests the width of digits."""

    def setUp(self):
        _, self.fonts = load_fonts()
        self.digits = [
            'zero', 'one', 'two', 'three', 'four',
            'five', 'six', 'seven', 'eight', 'nine']

    def test_digit_widths(self):
        """Tests all decimal digits to make sure they have the same width."""
        for font in self.fonts:
            hmtx_table = font['hmtx']
            widths = [hmtx_table[digit][0] for digit in self.digits]
            self.assertEqual(len(set(widths)), 1)


class TestHints(unittest.TestCase):
    """Tests hints."""

    def setUp(self):
        _, self.fonts = load_fonts()

        # FIXME: remove as soon as issue 100 is fixed
        bad_glyphs = ['uniFB01', 'uniFB02', 'uniFB03',
                      'uniFB04', 'uniFFFC', 'uni048C']
        self.known_missing_hints = [
            (g, 'Roboto Light Italic') for g in bad_glyphs]

    def test_digit_widths(self):
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

        self.assertTrue(missing_hints <= self.known_missing_hints)


if __name__ == '__main__':
    unittest.main()
