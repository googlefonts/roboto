#!/usr/bin/python
"""Test assumptions that Android relies on."""

import glob
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data

import roboto_data


def load_fonts():
    """Load all fonts built for Android."""
    all_font_files = glob.glob('out/android/*.ttf')
    all_fonts = [ttLib.TTFont(font) for font in all_font_files]
    assert len(all_font_files) == 18
    return all_font_files, all_fonts


class TestMetaInfo(unittest.TestCase):
    """Test various meta information."""

    def setUp(self):
        _, self.fonts = load_fonts()

    def test_us_weight(self):
        "Tests the usWeight of the fonts to be correct."""
        for font in self.fonts:
            weight = roboto_data.extract_weight_name(font_data.font_name(font))
            expected_numeric_weight = roboto_data.WEIGHTS[weight]
            self.assertEqual(
                font['OS/2'].usWeightClass,
                expected_numeric_weight)

    def test_version_numbers(self):
        "Tests the two version numbers of the font to be correct."""
        for font in self.fonts:
            build_number = roboto_data.get_build_number()
            expected_version = '2.' + build_number
            version = font_data.font_version(font)
            usable_part_of_version = version.split(';')[0]
            self.assertEqual(usable_part_of_version,
                             'Version ' + expected_version)

            revision = font_data.printable_font_revision(font, accuracy=5)
            self.assertEqual(revision, expected_version)


class TestVerticalMetrics(unittest.TestCase):
    """Test the vertical metrics of fonts."""

    def setUp(self):
        _, self.fonts = load_fonts()

    def test_ymin_ymax(self):
        """Tests yMin and yMax to be equal to what Android expects."""
        for font in self.fonts:
            head_table = font['head']
            self.assertEqual(head_table.yMin, -555)
            self.assertEqual(head_table.yMax, 2163)


class TestCharacterCoverage(unittest.TestCase):
    """Tests character coverage."""

    def setUp(self):
        _, self.fonts = load_fonts()
        self.LEGACY_PUA = frozenset({0xEE01, 0xEE02, 0xF6C3})

    def test_lack_of_arrows_and_combining_keycap(self):
        """Tests that arrows and combining keycap are not in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertNotIn(0x20E3, charset)  # COMBINING ENCLOSING KEYCAP
            self.assertNotIn(0x2191, charset)  # UPWARDS ARROW
            self.assertNotIn(0x2193, charset)  # DOWNWARDS ARROW

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


if __name__ == '__main__':
    unittest.main()
