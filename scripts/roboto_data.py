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

import ConfigParser
import os
import re


def get_version_number():
    """Returns the version number as a string."""

    config_parser = ConfigParser.RawConfigParser()
    config_file = os.path.join(
        os.path.dirname(__file__), os.pardir, 'res', 'roboto.cfg')
    config_parser.read(config_file)
    version_number = config_parser.get('main', 'version')
    assert re.match(r'[0-9]+\.[0-9]{3}', version_number)
    return version_number
