#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
import math
import numpy as np
from freetype import *
import matplotlib.pyplot as plt


def make_label(text, filename, size=12, angle=0):
    '''
    Parameters:
    -----------
    text : string
        Text to be displayed
    filename : string
        Path to a font
    size : int
        Font size in 1/64th points
    angle : float
        Text angle in degrees
    '''
    face = Face(filename)
    face.set_char_size( size*64 )
    angle = (angle/180.0)*math.pi
    matrix  = FT_Matrix( (int)( math.cos( angle ) * 0x10000L ),
                         (int)(-math.sin( angle ) * 0x10000L ),
                         (int)( math.sin( angle ) * 0x10000L ),
                         (int)( math.cos( angle ) * 0x10000L ))
    flags = FT_LOAD_RENDER
    pen = FT_Vector(0,0)
    FT_Set_Transform( face._FT_Face, byref(matrix), byref(pen) )
    previous = 0
    xmin, xmax = 0, 0
    ymin, ymax = 0, 0
    for c in text:
        face.load_char(c, flags)
        kerning = face.get_kerning(previous, c)
        previous = c
        bitmap = face.glyph.bitmap
        pitch  = face.glyph.bitmap.pitch
        width  = face.glyph.bitmap.width
        rows   = face.glyph.bitmap.rows
        top    = face.glyph.bitmap_top
        left   = face.glyph.bitmap_left
        pen.x += kerning.x
        x0 = (pen.x >> 6) + left
        x1 = x0 + width
        y0 = (pen.y >> 6) - (rows - top)
        y1 = y0 + rows
        xmin, xmax = min(xmin, x0),  max(xmax, x1)
        ymin, ymax = min(ymin, y0), max(ymax, y1)
        pen.x += face.glyph.advance.x
        pen.y += face.glyph.advance.y

    L = np.zeros((ymax-ymin, xmax-xmin),dtype=np.ubyte)
    previous = 0
    pen.x, pen.y = 0, 0
    for c in text:
        face.load_char(c, flags)
        kerning = face.get_kerning(previous, c)
        previous = c
        bitmap = face.glyph.bitmap
        pitch  = face.glyph.bitmap.pitch
        width  = face.glyph.bitmap.width
        rows   = face.glyph.bitmap.rows
        top    = face.glyph.bitmap_top
        left   = face.glyph.bitmap_left
        pen.x += kerning.x
        x = (pen.x >> 6) - xmin + left
        y = (pen.y >> 6) - ymin - (rows - top)
        data = []
        for j in range(rows):
            data.extend(bitmap.buffer[j*pitch:j*pitch+width])
        if len(data):
            Z = np.array(data,dtype=np.ubyte).reshape(rows, width)
            L[y:y+rows,x:x+width] |= Z[::-1,::1]
        pen.x += face.glyph.advance.x
        pen.y += face.glyph.advance.y

    return L


if __name__ == '__main__':
    from PIL import Image

    n_words = 100
    H, W, dpi = 600, 800, 72.0
    I = np.zeros((H, W, 3), dtype=np.ubyte)
    S = np.random.normal(0,1,n_words)
    S = (S-S.min())/(S.max()-S.min())
    S = np.sort(1-np.sqrt(S))[::-1]
    sizes = (12 + S*48).astype(int).tolist()

    def spiral():
        eccentricity = 1.5
        radius = 8
        step = 0.1
        t = 0
        while True:
            t += step
            yield eccentricity*radius*t*math.cos(t), radius*t*math.sin(t)

    fails = 0
    for size in sizes:
        angle = np.random.randint(-25,25)
        L = make_label('Hello', './Vera.ttf', size, angle=angle)
        h,w = L.shape
        if h < H and w < W:
            x0 = W//2 + (np.random.uniform()-.1)*50
            y0 = H//2 + (np.random.uniform()-.1)*50
            for dx,dy in spiral():
                c = .25+.75*np.random.random()
                x = int(x0+dx)
                y = int(y0+dy)
                if x <= w//2 or y <= h//2 or x >= (W-w//2) or y >= (H-h//2):
                    fails += 1
                    break
                if (I[y-h//2:y-h//2+h, x-w//2:x-w//2+w,0] * L).sum() == 0:
                    I[y-h//2:y-h//2+h, x-w//2:x-w//2+w,0] |= (c * L).astype(int)
                    I[y-h//2:y-h//2+h, x-w//2:x-w//2+w,1] |= (c * L).astype(int)
                    I[y-h//2:y-h//2+h, x-w//2:x-w//2+w,2] |= (c * L).astype(int)
                    break

    print "Number of fails:", fails
    fig = plt.figure(figsize=(W/dpi,H/dpi), dpi=dpi)
    ax = fig.add_axes([0,0,1,1], frameon=False)
    ax.imshow(I, interpolation='nearest', cmap=plt.cm.gray, origin='upper')
    #plt.axis('off')
    plt.show()
    I = Image.fromarray(I[::-1,::1,::1], mode='RGB')
    I.save('wordle.png')
