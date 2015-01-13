#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Glyph outline rendering
'''
from freetype import *

if __name__ == '__main__':
    import numpy
    import matplotlib.pyplot as plt

    face = Face('./Vera.ttf')
    face.set_char_size( 4*48*64 )
    flags = FT_LOAD_DEFAULT | FT_LOAD_NO_BITMAP
    face.load_char('S', flags )
    slot = face.glyph
    glyph = slot.get_glyph()
    stroker = Stroker( )
    stroker.set(64, FT_STROKER_LINECAP_ROUND, FT_STROKER_LINEJOIN_ROUND, 0 )
    glyph.stroke( stroker )
    blyph = glyph.to_bitmap(FT_RENDER_MODE_NORMAL, Vector(0,0))
    bitmap = blyph.bitmap
    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    top, left = blyph.top, blyph.left
    data = []
    for i in range(rows):
        data.extend(bitmap.buffer[i*pitch:i*pitch+width])
    Z = numpy.array(data,dtype=numpy.ubyte).reshape(rows, width)
    plt.figure(figsize=(6,8))
    plt.imshow(Z, interpolation='nearest', cmap=plt.cm.gray_r, origin='lower')
    plt.show()
