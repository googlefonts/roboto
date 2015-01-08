#!/usr/bin/python
"""Test assumptions that web fonts rely on."""

import glob
import json
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data
from nototools import render
from nototools import unicode_data


def load_fonts():
    """Load all web fonts."""
    all_font_files = glob.glob('out/web/*.ttf')
    all_fonts = [ttLib.TTFont(font) for font in all_font_files]
    assert len(all_font_files) == 18
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


class TestNames(unittest.TestCase):
    """Tests various strings in the name table."""

    def setUp(self):
        self.family_name = 'RobotoDraft'
        _, self.fonts = load_fonts()
        self.names = []
        for font in self.fonts:
            self.names.append(font_data.get_name_records(font))

    def test_copyright(self):
        """Tests the copyright message."""
        for records in self.names:
            self.assertEqual(
                records[0],
                'Copyright 2014 Google Inc. All Rights Reserved.')

    def test_family_name(self):
        """Tests the family name."""
        for records in self.names:
            self.assertEqual(records[1], self.family_name)
            if 16 in records:
                self.assertEqual(records[16], self.family_name)

    def test_unique_identifier_and_full_name(self):
        """Tests the unique identifier and full name."""
        for records in self.names:
            expected_name = records[1] + ' ' + records[2]
            self.assertEqual(records[3], expected_name)
            self.assertEqual(records[4], expected_name)
            self.assertFalse(records.has_key(18))

    def test_postscript_name(self):
        """Tests the postscript name."""
        for records in self.names:
            expected_name = records[1] + '-' + records[2].replace(' ', '')
            self.assertEqual(records[6], expected_name)


class TestHints(unittest.TestCase):
    """Tests hints."""

    def setUp(self):
        _, self.fonts = load_fonts()

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


if __name__ == '__main__':
    unittest.main()

