#!/usr/bin/python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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

"""Post-build changes for Roboto to deploy on Google Chrome/Chromium OS"""

import sys

from fontTools import ttLib
from nototools import font_data
from touchup_for_web import apply_web_cros_common_fixes

import temporary_touchups

def drop_non_windows_name_records(font):
    """Drop name records whose (PID,EID,Lang) != (3,1,0x409)"""
    names = font['name'].names
    records_to_drop = set()
    for record_number, record in enumerate(names):
        name_ids = (record.platformID, record.platEncID, record.langID)
        if name_ids != (3, 1, 0x409):
             records_to_drop.add(record_number)

    # Taken from nototools/font_data.py
    if records_to_drop:
        font['name'].names = [
            record for record_number, record in enumerate(names)
            if record_number not in records_to_drop]

def correct_font(source_name, unhinted_name, target_font_name, family_name):
    """Corrects metrics and other meta information."""

    font = ttLib.TTFont(source_name)
    unhinted = ttLib.TTFont(unhinted_name)

    apply_web_cros_common_fixes(font, unhinted, family_name)
    temporary_touchups.apply_temporary_fixes(font, is_for_cros=True)
    temporary_touchups.update_version_and_revision(font)
    drop_non_windows_name_records(font)
    font.save(target_font_name)

def main(argv):
    """Correct the font specified in the command line."""
    correct_font(*argv[1:])


if __name__ == "__main__":
    main(sys.argv)
