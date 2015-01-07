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

