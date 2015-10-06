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

import common_tests
import roboto_data

FONTS = common_tests.load_fonts(
    ['hinted/*.ttf'],
    expected_count=18)

UFOS = common_tests.load_fonts(
    ['out/RobotoUFO/*.ufo', 'out/RobotoCondensedUFO/*.ufo'],
    expected_count=18,
    font_class=OpenFont)

UFO_MASTERS = common_tests.load_fonts(
    ['src/v2/*.ufo'],
    expected_count=3,
    font_class=OpenFont)

class TestItalicAngle(common_tests.TestItalicAngle):
    loaded_fonts = FONTS
    expected_italic_angle = -12.0


class TestMetaInfo(common_tests.TestMetaInfo):
    """Bugs:
    https://code.google.com/a/google.com/p/roboto/issues/detail?id=8
    https://code.google.com/a/google.com/p/roboto/issues/detail?id=29
    """

    loaded_fonts = FONTS
    mark_heavier_as_bold = True
    test_us_weight = None
    test_version_numbers = None

    # fsType of 0 marks the font free for installation, embedding, etc.
    expected_os2_fsType = 0
    expected_os2_achVendID = 'GOOG'


class TestDigitWidths(common_tests.TestDigitWidths):
    loaded_fonts = FONTS


class TestCharacterCoverage(common_tests.TestCharacterCoverage):
    loaded_fonts = FONTS

    include = frozenset([
        0x2117,  # SOUND RECORDING COPYRIGHT
        0xEE01, 0xEE02, 0xF6C3])  # legacy PUA

    exclude = frozenset([
        0x2072, 0x2073, 0x208F] +  # unassigned characters
        range(0xE000, 0xF8FF + 1) + range(0xF0000, 0x10FFFF + 1)  # other PUA
        ) - include  # don't exclude legacy PUA


class TestLigatures(common_tests.TestLigatures):
    loaded_fonts = FONTS


class TestFeatures(common_tests.TestFeatures):
    loaded_fonts = FONTS


class TestVerticalMetrics(common_tests.TestVerticalMetrics):
    loaded_fonts = FONTS
    test_ymin_ymax = None
    test_hhea_table_metrics = None
    test_os2_metrics = None

    expected_head_yMin = -555
    expected_head_yMax = 2163


class TestGlyphAreas(common_tests.TestGlyphAreas):
    loaded_fonts = UFOS
    masters = UFO_MASTERS


if __name__ == '__main__':
    unittest.main()
