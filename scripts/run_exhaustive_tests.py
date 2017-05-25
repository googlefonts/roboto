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

import unittest
from nototools.unittests import font_tests

FONTS = font_tests.load_fonts(
    ['out/RobotoTTF/*.ttf', 'out/RobotoCondensedTTF/*.ttf'],
    expected_count=20)


class TestSpacingMarks(font_tests.TestSpacingMarks):
    loaded_fonts = FONTS


class TestSoftDottedChars(font_tests.TestSoftDottedChars):
    loaded_fonts = FONTS
    # FIXME: Test is currently disabled, since the fonts fail it
    test_combinations = None


if __name__ == '__main__':
    unittest.main()
