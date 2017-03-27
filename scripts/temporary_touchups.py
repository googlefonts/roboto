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

def apply_temporary_fixes(font, is_for_cros=False, is_for_web=False):
    """Apply some temporary fixes."""
    # Fix usWeight:
    font_name = font_data.font_name(font)
    weight = noto_fonts.parse_weight(font_name)
    weight_number = noto_fonts.WEIGHTS[weight]
    # Chrome OS wants Thin to have usWeightClass=100
    if is_for_cros and weight == 'Thin':
        weight_number = 100
    font['OS/2'].usWeightClass = weight_number

    # Set bold bits for Black (macStyle bit 0, fsSelection bit 5)
    if is_for_web is False:
        name_records = font_data.get_name_records(font)
        family_name = name_records[1]
        if family_name.endswith('Black'):
            font['head'].macStyle |= (1 << 0)
            font['OS/2'].fsSelection |= (1 << 5)
            font['OS/2'].fsSelection &= ~(1 << 6)

def update_version_and_revision(font):
    """Update version and revision numbers."""

    version_number = roboto_data.get_version_number()
    version_record = 'Version %s; %d' % (version_number, date.today().year)
    font_data.set_name_record(font, 5, version_record)
    font['head'].fontRevision = float(version_number)
