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


class TestSpacingMarks(unittest.TestCase):
    """Tests that spacing marks are indeed spacing."""

    def setUp(self):
        self.font_files, _ = load_fonts()
        charset = coverage.character_set(self.font_files[0])
        self.marks_to_test = [char for char in charset
                              if unicode_data.category(char) in ['Lm', 'Sk']]
        self.advance_cache = {}

    def get_advances(self, text, font):
        """Get a list of horizontal advances for text rendered in a font."""
        try:
            return self.advance_cache[(text, font)]
        except KeyError:
            hb_output = render.run_harfbuzz_on_text(text, font, '')
            hb_output = json.loads(hb_output)
            advances = [glyph['ax'] for glyph in hb_output]
            self.advance_cache[(text, font)] = advances
            return advances

    def test_individual_spacing_marks(self):
        """Tests that spacing marks are spacing by themselves."""
        for font in self.font_files:
            print 'Testing %s for stand-alone spacing marks...' % font
            for mark in self.marks_to_test:
                mark = unichr(mark)
                advances = self.get_advances(mark, font)
                assert len(advances) == 1
                self.assertNotEqual(advances[0], 0)

    def test_spacing_marks_in_combination(self):
        """Tests that spacing marks do not combine with base letters."""
        for font in self.font_files:
            print 'Testing %s for spacing marks in combination...' % font
            for base_letter in (u'A\u00C6BCDEFGHIJKLMNO\u00D8\u01A0PRST'
                                u'U\u01AFVWXYZ'
                                u'a\u00E6bcdefghi\u0131j\u0237klmn'
                                u'o\u00F8\u01A1prs\u017Ftu\u01B0vwxyz'
                                u'\u03D2'):
                print 'Testing %s combinations' % base_letter
                for mark in self.marks_to_test:
                    mark = unichr(mark)
                    advances = self.get_advances(base_letter + mark, font)
                    self.assertEqual(len(advances), 2,
                        'The sequence <%04X, %04X> combines, '
                        'but it should not' % (ord(base_letter), ord(mark)))


if __name__ == '__main__':
    unittest.main()
