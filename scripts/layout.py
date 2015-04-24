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

_advance_cache = {}
def get_advances(text, font):
    """Get a list of horizontal advances for text rendered in a font."""
    try:
        return _advance_cache[(text, font)]
    except KeyError:
        pass

    hb_output = render.run_harfbuzz_on_text(text, font, None)
    hb_output = json.loads(hb_output)
    advances = [glyph['ax'] for glyph in hb_output]
    _advance_cache[(text, font)] = advances
    return advances

_shape_cache = {}
def get_shapes(text, font):
    """Get a list of shaped glyphs for text rendered in a font."""
    try:
        return _shape_cache[(text, font)]
    except KeyError:
        pass

    hb_output = render.run_harfbuzz_on_text(text, font, None)
    hb_output = json.loads(hb_output)
    shapes = [glyph['g'] for glyph in hb_output]
    _shape_cache[(text, font)] = shapes
    return shapes
