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

"""Test general health of the fonts."""

import unittest

from robofab.world import OpenFont
from nototools.unittests import font_tests

import roboto_data

FONTS = font_tests.load_fonts(
    ['hinted/*.ttf'],
    expected_count=18)

UFOS = font_tests.load_fonts(
    ['out/RobotoUFO/*.ufo', 'out/RobotoCondensedUFO/*.ufo'],
    expected_count=18,
    font_class=OpenFont)

UFO_MASTERS = font_tests.load_fonts(
    ['src/v2/*.ufo'],
    expected_count=3,
    font_class=OpenFont)

class TestItalicAngle(font_tests.TestItalicAngle):
    loaded_fonts = FONTS
    expected_italic_angle = -12.0


class TestMetaInfo(font_tests.TestMetaInfo):
    """Bugs:
    https://code.google.com/a/google.com/p/roboto/issues/detail?id=8
    https://code.google.com/a/google.com/p/roboto/issues/detail?id=29
    """

    loaded_fonts = FONTS
    mark_heavier_as_bold = True
    test_us_weight = None

    #expected_version = '2.' + roboto_data.get_build_number()
    test_version_numbers = None

    # fsType of 0 marks the font free for installation, embedding, etc.
    expected_os2_fsType = 0
    expected_os2_achVendID = 'GOOG'


class TestDigitWidths(font_tests.TestDigitWidths):
    loaded_fonts = FONTS


class TestCharacterCoverage(font_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    include = frozenset([
        0x2117,  # SOUND RECORDING COPYRIGHT
        0xEE01, 0xEE02, 0xF6C3])  # legacy PUA

    exclude = frozenset([
        0x2072, 0x2073, 0x208F] +  # unassigned characters
        range(0xE000, 0xF8FF + 1) + range(0xF0000, 0x10FFFF + 1)  # other PUA
        ) - include  # don't exclude legacy PUA


class TestLigatures(font_tests.TestLigatures):
    loaded_fonts = FONTS


class TestFeatures(font_tests.TestFeatures):
    loaded_fonts = FONTS


class TestVerticalMetrics(font_tests.TestVerticalMetrics):
    loaded_fonts = FONTS
    test_ymin_ymax = None
    test_hhea_table_metrics = None
    test_os2_metrics = None

    expected_head_yMin = -555
    expected_head_yMax = 2163


class TestGlyphAreas(font_tests.TestGlyphAreas):
    loaded_fonts = UFOS
    masters = UFO_MASTERS


if __name__ == '__main__':
    unittest.main()
