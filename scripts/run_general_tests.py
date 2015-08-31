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


class TestFeatures(common_tests.TestFeatures):
    loaded_fonts = FONTS


class TestVerticalMetrics(common_tests.TestVerticalMetrics):
    loaded_fonts = FONTS
    test_ymin_ymax = None
    test_hhea_table_metrics = None

if __name__ == '__main__':
    unittest.main()

