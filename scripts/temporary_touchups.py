#!/usr/bin/python
"""Temporary post-build changes for Roboto."""

from datetime import date
import os
from os import path

from nototools import font_data

import roboto_data

def apply_temporary_fixes(font):
    """Apply some temporary fixes."""
    # Fix usWeight:
    font_name = font_data.font_name(font)
    weight = roboto_data.extract_weight_name(font_name)
    weight_number = roboto_data.WEIGHTS[weight]
    font['OS/2'].usWeightClass = weight_number

    # Update version number from buildnumber.txt
    build_number_txt = path.join(
        path.dirname(__file__), os.pardir, 'res', 'buildnumber.txt')
    build_number = open(build_number_txt).read().strip()
    version_record = 'Version 2.%s; %d' % (build_number, date.today().year)
    font_data.set_name_record(font, 5, version_record)

