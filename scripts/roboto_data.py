#!/usr/bin/python
"""Post-build changes for Roboto for Android."""

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
        assert font_name in ['Roboto Italic', 'Roboto Condensed Italic']
        return 'Regular'
    else:
        return match.group(1)
