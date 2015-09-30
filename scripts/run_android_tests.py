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

"""Test assumptions that Android relies on."""

import glob
import json
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data
from nototools import render
from nototools import unicode_data
import common_tests


FONTS = common_tests.load_fonts(
    ['out/android/*.ttf'],
    expected_count=18)


class TestVerticalMetrics(common_tests.TestVerticalMetrics):
    loaded_fonts = FONTS
    test_glyphs_ymin_ymax = None
    test_hhea_table_metrics = None
    test_os2_metrics = None

    expected_head_yMin = -555
    expected_head_yMax = 2163



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


class TestCharacterCoverage(common_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    include = frozenset([
        0x2117,  # SOUND RECORDING COPYRIGHT
        0xEE01, 0xEE02, 0xF6C3])  # legacy PUA

    exclude = frozenset([
        0x20E3,  # COMBINING ENCLOSING KEYCAP
        0x2191,  # UPWARDS ARROW
        0x2193,  # DOWNWARDS ARROW
        0x2072, 0x2073, 0x208F] +  # unassigned characters
        range(0xE000, 0xF8FF + 1) + range(0xF0000, 0x10FFFF + 1)  # other PUA
        ) - include  # don't exclude legacy PUA


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
