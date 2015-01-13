#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Glyph colored rendering (with outline)
'''
from freetype import *

if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    face = Face('./Vera.ttf')
    face.set_char_size( 96*64 )
    RGBA = [('R',float), ('G',float), ('B',float), ('A',float)]

    # Outline
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
    Z = np.array(data).reshape(rows, width)/255.0
    O = np.zeros((rows,width), dtype=RGBA)
    O['A'] = Z
    O['R'] = 1
    O['G'] = 0
    O['B'] = 0

    # Plain
    flags = FT_LOAD_RENDER
    face.load_char('S', flags)
    F = np.zeros((rows,width), dtype=RGBA)
    Z = np.zeros((rows, width))
    bitmap = face.glyph.bitmap
    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    top, left = face.glyph.bitmap_top, face.glyph.bitmap_left
    dy = blyph.top - face.glyph.bitmap_top
    dx = face.glyph.bitmap_left - blyph.left
    data = []
    for i in range(rows):
        data.extend(bitmap.buffer[i*pitch:i*pitch+width])
    Z[dx:dx+rows,dy:dy+width] = np.array(data).reshape(rows, width)/255.
    F['R'] = 1
    F['G'] = 1
    F['B'] = 0
    F['A'] = Z

    # Combine outline and plain
    R1,G1,B1,A1 = O['R'],O['G'],O['B'],O['A']
    R2,G2,B2,A2 = F['R'],F['G'],F['B'],F['A']
    Z = np.zeros(O.shape, dtype=RGBA)
    Z['R'] = (A1 * R1 + A2 * (1 - A1) * R2)
    Z['G'] = (A1 * G1 + A2 * (1 - A1) * G2)
    Z['B'] = (A1 * B1 + A2 * (1 - A1) * B2)
    Z['A'] = (A1      + A2 * (1 - A1))


    # Draw
    plt.figure(figsize=(12,5))

    plt.subplot(1,3,1)
    plt.title('Plain')
    plt.xticks([]), plt.yticks([])
    I = F.view(dtype=float).reshape(O.shape[0],O.shape[1],4)
    plt.imshow(I, interpolation='nearest', origin='lower')

    plt.subplot(1,3,2)
    plt.title('Outline')
    plt.xticks([]), plt.yticks([])
    I = O.view(dtype=float).reshape(O.shape[0],O.shape[1],4)
    plt.imshow(I, interpolation='nearest', origin='lower')

    plt.subplot(1,3,3)
    plt.title('Outline + Plain')
    plt.xticks([]), plt.yticks([])
    I = Z.view(dtype=float).reshape(O.shape[0],O.shape[1],4)
    plt.imshow(I, interpolation='nearest', origin='lower')

    plt.show()
