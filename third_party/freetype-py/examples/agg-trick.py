#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
from freetype import *
import numpy as np
import Image


def render(filename = "Vera.ttf", hinting = (False,False), gamma = 1.5, lcd=False):
    text = "A Quick Brown Fox Jumps Over The Lazy Dog 0123456789"

    W,H,D = 680, 280, 1
    Z = np.zeros( (H,W), dtype=np.ubyte )
    face = Face(filename)
    pen = Vector(5*64, (H-10)*64)

    flags = FT_LOAD_RENDER
    if hinting[1]: flags |= FT_LOAD_FORCE_AUTOHINT
    else:          flags |= FT_LOAD_NO_HINTING
    if hinting[0]: hres, hscale = 72,    1.0
    else:          hres, hscale = 72*10, 0.1
    if lcd:
        flags |= FT_LOAD_TARGET_LCD
        Z = np.zeros( (H,W,3), dtype=np.ubyte )
        set_lcd_filter( FT_LCD_FILTER_DEFAULT )


    for size in range(9,23):
        face.set_char_size( size * 64, 0, hres, 72 )
        matrix = Matrix( int((hscale) * 0x10000L), int((0.0) * 0x10000L),
                         int((0.0)    * 0x10000L), int((1.0) * 0x10000L) )
        previous = 0
        pen.x = 5*64
        for current in text:
            face.set_transform( matrix, pen )
            face.load_char( current, flags)
            kerning = face.get_kerning( previous, current, FT_KERNING_UNSCALED )
            pen.x += kerning.x
            glyph = face.glyph
            bitmap = glyph.bitmap
            x, y = glyph.bitmap_left, glyph.bitmap_top
            w, h, p = bitmap.width, bitmap.rows, bitmap.pitch
            buff = np.array(bitmap.buffer, dtype=np.ubyte).reshape((h,p))
            if lcd:
                Z[H-y:H-y+h,x:x+w/3].flat |= buff[:,:w].flatten()
            else:
                Z[H-y:H-y+h,x:x+w].flat |= buff[:,:w].flatten()
            pen.x += glyph.advance.x
            previous = current
        pen.y -= (size+4)*64

    # Gamma correction
    Z = (Z/255.0)**(gamma)
    Z = ((1-Z)*255).astype(np.ubyte)
    if lcd:
        I = Image.fromarray(Z, mode='RGB')
    else:
        I = Image.fromarray(Z, mode='L')
 
    name = filename.split('.')[0]
    filename = '%s-gamma(%.1f)-hinting(%d,%d)-lcd(%d).png' % (name,gamma,hinting[0],hinting[1],lcd)
    I.save(filename)



if __name__ == '__main__':
    render('Vera.ttf', (0,1), 1.25, True)
        
