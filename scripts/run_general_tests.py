#!/usr/bin/python
"""Test general health of the fonts."""

import glob
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data


def load_fonts():
    """Load all major fonts."""
    all_font_files = (glob.glob('out/RobotoTTF/*.ttf')
                      + glob.glob('out/RobotoCondensedTTF/*.ttf'))
    all_fonts = [ttLib.TTFont(font) for font in all_font_files]
    assert len(all_font_files) == 18
    return all_font_files, all_fonts


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


class TestMetaInfo(unittest.TestCase):
    """Test various meta information."""

    def setUp(self):
        _, self.fonts = load_fonts()

    def test_mac_style(self):
        """Tests the macStyle of the fonts to be correct.

        Bug: https://code.google.com/a/google.com/p/roboto/issues/detail?id=8
        """
        for font in self.fonts:
            font_name = font_data.font_name(font)
            bold = ('Bold' in font_name) or ('Black' in font_name)
            italic = 'Italic' in font_name
            expected_mac_style = (italic << 1) | bold
            self.assertEqual(font['head'].macStyle, expected_mac_style)

    def test_fs_type(self):
        """Tests the fsType of the fonts to be 0.

        fsType of 0 marks the font free for installation, embedding, etc.

        Bug: https://code.google.com/a/google.com/p/roboto/issues/detail?id=29
        """
        for font in self.fonts:
            self.assertEqual(font['OS/2'].fsType, 0)

    def test_vendor_id(self):
        """Tests the vendor ID of the fonts to be 'GOOG'."""
        for font in self.fonts:
            self.assertEqual(font['OS/2'].achVendID, 'GOOG')


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


class TestCharacterCoverage(unittest.TestCase):
    """Tests character coverage."""

    def setUp(self):
        _, self.fonts = load_fonts()

    def test_lack_of_unassigned_chars(self):
        """Tests that unassigned characters are not in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertNotIn(0x2072, charset)
            self.assertNotIn(0x2073, charset)
            self.assertNotIn(0x208F, charset)

    def test_inclusion_of_sound_recording_copyright(self):
        """Tests that sound recording copyright symbol is in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertIn(
                0x2117, charset,  # SOUND RECORDING COPYRIGHT
                'U+2117 not found in %s.' % font_data.font_name(font))


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
                    if mark == 0x02DE:
                        # Skip rhotic hook, as it's perhaps OK for it to form
                        # ligatures
                        continue
                    mark = unichr(mark)
                    advances = self.get_advances(base_letter + mark, font)
                    self.assertEqual(len(advances), 2,
                        'The sequence <%04X, %04X> combines, '
                        'but it should not' % (ord(base_letter), ord(mark)))


if __name__ == '__main__':
    unittest.main()
