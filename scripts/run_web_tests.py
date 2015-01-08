#!/usr/bin/python
"""Test assumptions that web fonts rely on."""

import unittest

from nototools import font_data

import common_tests

FONTS = common_tests.load_fonts(
    ['out/web/*.ttf'],
    expected_count=18)

class TestCharacterCoverage(common_tests.TestCharacterCoverage):
    loaded_fonts = FONTS
    test_inclusion_of_sound_recording_copyright = None


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


class TestMetaInfo(common_tests.TestMetaInfo):
    loaded_fonts = FONTS
    # Since different font files are hinted at different times, the actual
    # outlines differ slightly. So we are keeping the version numbers as a hint.
    test_version_numbers = None


class TestNames(common_tests.TestNames):
    loaded_fonts = FONTS
    family_name = 'RobotoDraft'

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
        _, self.fonts = FONTS

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

