#!/usr/bin/python
"""Test assumptions that Android relies on."""

import glob
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data


def load_fonts():
    """Load all fonts built for Android."""
    all_fonts = glob.glob('out/android/*.ttf')
    all_fonts = [ttLib.TTFont(font) for font in all_fonts]
    return all_fonts


class TestVerticalMetrics(unittest.TestCase):
    """Test the vertical metrics of fonts."""

    def setUp(self):
        self.fonts = load_fonts()

    def test_ymin_ymax(self):
        """Tests yMin and yMax to be equal to what Android expects."""
        for font in self.fonts:
            head_table = font['head']
            self.assertEqual(head_table.yMin, -555)
            self.assertEqual(head_table.yMax, 2163)


class TestDigitWidths(unittest.TestCase):
    """Tests the width of digits."""

    def setUp(self):
        self.fonts = load_fonts()
        self.digits = [
            'zero', 'one', 'two', 'three', 'four',
            'five', 'six', 'seven', 'eight', 'nine']

    def test_digit_widths(self):
        """Tests all decimal digits to make sure they have the same width."""
        for font in self.fonts:
            hmtx_table = font['hmtx']
            widths = [hmtx_table[digit][0] for digit in self.digits]
            self.assertEqual(len(set(widths)), 1)


class TestCharacterCoverage(unittest.TestCase):
    """Tests character coverage."""

    def setUp(self):
        self.fonts = load_fonts()

    def test_lack_of_arrows_and_combining_keycap(self):
        """Tests that arrows and combining keycap are not in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertNotIn(0x20E3, charset)  # COMBINING ENCLOSING KEYCAP
            self.assertNotIn(0x2191, charset)  # UPWARDS ARROW
            self.assertNotIn(0x2193, charset)  # DOWNWARDS ARROW

    def test_inclusion_of_sound_recording_copyright(self):
        """Tests that sound recording copyright symbol is in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertIn(
                0x2117, charset,  # SOUND RECORDING COPYRIGHT
                'U+2117 not found in %s.' % font_data.font_name(font))


if __name__ == '__main__':
    unittest.main()
