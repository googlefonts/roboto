#!/usr/bin/python
"""Test assumptions that Android relies on."""

import unittest

from nototools import coverage

import common_tests

FONTS = common_tests.load_fonts(
    ['out/android/*.ttf'],
    expected_count=18)

class TestItalicAngle(common_tests.TestItalicAngle):
    loaded_fonts = FONTS


class TestMetaInfo(common_tests.TestMetaInfo):
    loaded_fonts = FONTS


class TestNames(common_tests.TestNames):
    loaded_fonts = FONTS


class TestDigitWidths(common_tests.TestDigitWidths):
    loaded_fonts = FONTS


class TestCharacterCoverage(common_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    def test_lack_of_arrows_and_combining_keycap(self):
        """Tests that arrows and combining keycap are not in Android fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertNotIn(0x20E3, charset)  # COMBINING ENCLOSING KEYCAP
            self.assertNotIn(0x2191, charset)  # UPWARDS ARROW
            self.assertNotIn(0x2193, charset)  # DOWNWARDS ARROW


class TestLigatures(common_tests.TestLigatures):
    loaded_fonts = FONTS


class TestVerticalMetrics(common_tests.TestVerticalMetrics):
    loaded_fonts = FONTS


if __name__ == '__main__':
    unittest.main()

