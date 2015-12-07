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

"""Temporary post-build changes for Roboto."""

from datetime import date
from nototools import font_data
from nototools import noto_fonts

import roboto_data

def apply_temporary_fixes(font):
    """Apply some temporary fixes."""
    # Fix usWeight:
    font_name = font_data.font_name(font)
    weight = noto_fonts.parse_weight(font_name)
    weight_number = noto_fonts.WEIGHTS[weight]
    font['OS/2'].usWeightClass = weight_number

    # Set ascent, descent, and lineGap values to Android K values
    hhea = font['hhea']
    hhea.ascent = 1900
    hhea.descent = -500
    hhea.lineGap = 0

    # Copyright message
    font_data.set_name_record(
        font, 0, 'Copyright 2011 Google Inc. All Rights Reserved.')


def update_version_and_revision(font):
    """Update version and revision numbers from buildnumber.txt."""
    build_number = roboto_data.get_build_number()
    version_number = '2.' + build_number
    version_record = 'Version %s; %d' % (version_number, date.today().year)
    font_data.set_name_record(font, 5, version_record)
    font['head'].fontRevision = float(version_number)

