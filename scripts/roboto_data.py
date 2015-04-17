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

"""General module for Roboto-specific data and methods."""

import os
from os import path
import re


WEIGHTS = {
    'Thin': 250,
    'Light': 300,
    'Regular': 400,
    'Medium': 500,
    'Bold': 700,
    'Black': 900,
}

_ALL_WEIGHTS_RE = re.compile(
    '(' + '|'.join(WEIGHTS.keys()) + ')'
)


def extract_weight_name(font_name):
    """Extracts the weight part of the name from a font name."""
    match = re.search(_ALL_WEIGHTS_RE, font_name)
    if match is None:
        assert re.match('^Roboto(Draft)?( Condensed)? Italic$', font_name)
        return 'Regular'
    else:
        return match.group(1)


def get_build_number():
    """Returns the build number as a five-digit string."""
    build_number_txt = path.join(
        path.dirname(__file__), os.pardir, 'res', 'buildnumber.txt')
    build_number = open(build_number_txt).read().strip()
    assert re.match('[0-9]{5}', build_number)
    return build_number

