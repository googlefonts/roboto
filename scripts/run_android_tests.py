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

import unittest
from nototools.unittests import font_tests

import run_general_tests


FONTS = font_tests.load_fonts(
    ['out/android/*.ttf'],
    expected_count=18)


class TestMetaInfo(run_general_tests.TestMetaInfo):
    """Bugs:
    https://github.com/google/roboto/issues/142
    """

    loaded_fonts = FONTS
    mark_heavier_as_bold = True


class TestNames(run_general_tests.TestNames):
    """Bugs:
    https://github.com/google/roboto/issues/37
    """

    loaded_fonts = FONTS
    mark_heavier_as_bold = True


class TestVerticalMetrics(font_tests.TestVerticalMetrics):
    loaded_fonts = FONTS
    test_glyphs_ymin_ymax = None
    test_hhea_table_metrics = None
    test_os2_metrics = None

    expected_head_yMin = -555
    expected_head_yMax = 2163


class TestDigitWidths(font_tests.TestDigitWidths):
    loaded_fonts = FONTS
    test_superscript_digits = None


class TestCharacterCoverage(font_tests.TestCharacterCoverage):
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


class TestSpacingMarks(font_tests.TestSpacingMarks):
    loaded_fonts = FONTS


if __name__ == '__main__':
    unittest.main()
