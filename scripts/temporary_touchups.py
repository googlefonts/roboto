#!/usr/bin/python
"""Temporary post-build changes for Roboto."""

from nototools import font_data

import roboto_data

def apply_temporary_fixes(font):
    """Apply some temporary fixes."""
    # Fix usWeight:
    font_name = font_data.font_name(font)
    weight = roboto_data.extract_weight_name(font_name)
    weight_number = roboto_data.WEIGHTS[weight]
    font['OS/2'].usWeightClass = weight_number
