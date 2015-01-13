#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
# -----------------------------------------------------------------------------
from __future__ import print_function
from __future__ import division
from freetype import *

def platform_name(platform_id):
    for key, value in TT_PLATFORMS.items():
        if value == platform_id:
            return key
    return 'Unknown platform'

def encoding_name(platform_id, encoding_id):
    if platform_id == TT_PLATFORM_APPLE_UNICODE:
        encodings = TT_APPLE_IDS
    elif platform_id == TT_PLATFORM_MACINTOSH:
        encodings = TT_MAC_IDS
    elif platform_id == TT_PLATFORM_MICROSOFT:
        encodings = TT_MS_IDS
    elif platform_id == TT_PLATFORM_ADOBE:
        encodings = TT_ADOBE_IDS
    else:
        return 'Unknown encoding'
    for key, value in encodings.items():
        if value == encoding_id:
            return key
    return 'Unknown encoding'

def language_name(platform_id, language_id):
    if platform_id == TT_PLATFORM_MACINTOSH:
        languages = TT_MAC_LANGIDS
    elif platform_id == TT_PLATFORM_MICROSOFT:
        languages = TT_MS_LANGIDS
    else:
        return 'Unknown language'
    for key, value in languages.items():
        if value == language_id:
            return key
    return 'Unknown language'


if __name__ == '__main__':
    import os, sys

    if len(sys.argv) < 2:
        print("Usage: %s font_filename" % sys.argv[0])
        sys.exit()
    face = Face(sys.argv[1])

    name = face.get_sfnt_name(0)
    print( 'platform_id:', platform_name(name.platform_id) )
    print( 'encoding_id:', encoding_name(name.platform_id,
                                        name.encoding_id) )
    print( 'language_id:', language_name(name.platform_id,
                                        name.language_id) )
    for i in range(face.sfnt_name_count):
        name = face.get_sfnt_name(i).string
        print(i, name.decode('utf-8', 'ignore'))


    

