#!/usr/bin/python
"""Test general health of the fonts."""

import unittest

import common_tests

FONTS = common_tests.load_fonts(
    ['out/RobotoTTF/*.ttf', 'out/RobotoCondensedTTF/*.ttf'],
    expected_count=18)

class TestItalicAngle(common_tests.TestItalicAngle):
    loaded_fonts = FONTS


class TestMetaInfo(common_tests.TestMetaInfo):
    loaded_fonts = FONTS
    test_us_weight = None
    test_version_numbers = None


class TestDigitWidths(common_tests.TestDigitWidths):
    loaded_fonts = FONTS


class TestCharacterCoverage(common_tests.TestCharacterCoverage):
    loaded_fonts = FONTS


class TestLigatures(common_tests.TestLigatures):
    loaded_fonts = FONTS


if __name__ == '__main__':
    unittest.main()

