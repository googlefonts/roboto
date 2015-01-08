#!/usr/bin/python
"""Temporary post-build changes for Roboto."""

from datetime import date
from nototools import font_data

import roboto_data

def apply_temporary_fixes(font):
    """Apply some temporary fixes."""
    # Fix usWeight:
    font_name = font_data.font_name(font)
    weight = roboto_data.extract_weight_name(font_name)
    weight_number = roboto_data.WEIGHTS[weight]
    font['OS/2'].usWeightClass = weight_number

    # Update version and revision numbers from buildnumber.txt
    build_number = roboto_data.get_build_number()
    version_number = '2.' + build_number
    version_record = 'Version %s; %d' % (version_number, date.today().year)
    font_data.set_name_record(font, 5, version_record)
    font['head'].fontRevision = float(version_number)

