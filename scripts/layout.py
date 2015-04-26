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

import json

from nototools import render

def _run_harfbuzz(text, font, language, extra_parameters=None):
    """Run harfbuzz on some text and return the shaped list."""
    try:
        # if extra_parameters is a string, split it into a list
        extra_parameters = extra_parameters.split(' ')
    except AttributeError:
        pass
    hb_output = render.run_harfbuzz_on_text(
        text, font, language, extra_parameters)
    return json.loads(hb_output)


_advance_cache = {}
def get_advances(text, font, extra_parameters=None):
    """Get a list of horizontal advances for text rendered in a font."""
    try:
        return _advance_cache[(text, font, extra_parameters)]
    except KeyError:
        pass

    hb_output = _run_harfbuzz(text, font, None, extra_parameters)
    advances = [glyph['ax'] for glyph in hb_output]
    _advance_cache[(text, font, extra_parameters)] = advances
    return advances


_shape_cache = {}
def get_glyphs(text, font, extra_parameters=None):
    """Get a list of shaped glyphs for text rendered in a font."""
    try:
        return _shape_cache[(text, font, extra_parameters)]
    except KeyError:
        pass

    hb_output = _run_harfbuzz(text, font, None, extra_parameters)
    shapes = [glyph['g'] for glyph in hb_output]
    _shape_cache[(text, font, extra_parameters)] = shapes
    return shapes
