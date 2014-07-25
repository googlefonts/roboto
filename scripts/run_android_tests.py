#!/usr/bin/python
"""Test assumptions that Android relies on."""

import glob
import unittest

from fontTools import ttLib


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


if __name__ == '__main__':
    unittest.main()
