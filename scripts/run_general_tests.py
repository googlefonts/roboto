#!/usr/bin/python
"""Test general health of the fonts."""

import glob
import unittest

from fontTools import ttLib
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


if __name__ == '__main__':
    unittest.main()
