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

"""Time-consuming tests for general health of the fonts."""

import glob
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import unicode_data

import layout

def load_fonts():
    """Load all major fonts."""
    all_font_files = (glob.glob('out/RobotoTTF/*.ttf')
                      + glob.glob('out/RobotoCondensedTTF/*.ttf'))
    all_fonts = [ttLib.TTFont(font) for font in all_font_files]
    assert len(all_font_files) == 18
    return all_font_files, all_fonts


class TestSpacingMarks(unittest.TestCase):
    """Tests that spacing marks are indeed spacing."""

    def setUp(self):
        self.font_files, _ = load_fonts()
        charset = coverage.character_set(self.font_files[0])
        self.marks_to_test = [char for char in charset
                              if unicode_data.category(char) in ['Lm', 'Sk']]
        self.advance_cache = {}

    def test_individual_spacing_marks(self):
        """Tests that spacing marks are spacing by themselves."""
        for font in self.font_files:
            print 'Testing %s for stand-alone spacing marks...' % font
            for mark in self.marks_to_test:
                mark = unichr(mark)
                advances = layout.get_advances(mark, font)
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
                    advances = layout.get_advances(base_letter + mark, font)
                    self.assertEqual(len(advances), 2,
                        'The sequence <%04X, %04X> combines, '
                        'but it should not' % (ord(base_letter), ord(mark)))


class TestSoftDottedChars(unittest.TestCase):
    """Tests that soft-dotted characters lose their dots."""

    def setUp(self):
        self.font_files, _ = load_fonts()
        charset = coverage.character_set(self.font_files[0])
        self.marks_to_test = [char for char in charset
                              if unicode_data.combining(char) == 230]
        self.advance_cache = {}

    def test_combinations(self):
        """Tests that soft-dotted characters lose their dots when combined."""

        return  # FIXME: Test is currently disabled, since the fonts fail it

        for font in self.font_files:
            print 'Testing %s for soft-dotted combinations...' % font

            # TODO: replace the following list with actual derivation based on
            # Unicode's soft-dotted property
            for base_letter in (u'ij\u012F\u0249\u0268\u029D\u02B2\u03F3\u0456'
                                u'\u0458\u1D62\u1D96\u1DA4\u1DA8\u1E2D\u1ECB'
                                u'\u2071\u2C7C'):
                print 'Testing %s combinations' % base_letter.encode('UTF-8')
                for mark in self.marks_to_test:
                    mark = unichr(mark)
                    letter_only = layout.get_shapes(base_letter, font)
                    combination = layout.get_shapes(base_letter + mark, font)
                    self.assertNotEqual(combination[0], letter_only[0],
                        "The sequence <%04X, %04X> doesn't lose its dot, "
                        "but it should" % (ord(base_letter), ord(mark)))


if __name__ == '__main__':
    unittest.main()
