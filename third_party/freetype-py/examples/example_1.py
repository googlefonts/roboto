#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011-2014 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
#
# Direct translation of example 1 from the freetype tutorial:
# http://www.freetype.org/freetype2/docs/tutorial/step1.html
#
import math
from freetype import *


if __name__ == '__main__':
    from PIL import Image
    from freetype import *

    WIDTH, HEIGHT = 640, 480
    image = Image.new('L', (WIDTH,HEIGHT))
    def draw_bitmap( bitmap, x, y):
        x_max = x + bitmap.width
        y_max = y + bitmap.rows
        p = 0
        for p,i in enumerate(range(x,x_max)):
            for q,j in enumerate(range(y,y_max)):
                if i < 0  or j < 0 or i >= WIDTH or j >= HEIGHT:
                    continue;
                pixel = image.getpixel((i,j))
                pixel |= int(bitmap.buffer[q * bitmap.width + p]);
                image.putpixel((i,j), pixel)

    library = FT_Library()
    matrix  = FT_Matrix()
    face    = FT_Face()
    pen     = FT_Vector()
    filename= './Vera.ttf'
    text    = 'Hello World !'
    num_chars = len(text)
    angle   = ( 25.0 / 360 ) * 3.14159 * 2

    # initialize library, error handling omitted
    error = FT_Init_FreeType( byref(library) )

    # create face object, error handling omitted
    error = FT_New_Face( library, filename, 0, byref(face) )

    # set character size: 50pt at 100dpi, error handling omitted
    error = FT_Set_Char_Size( face, 50 * 64, 0, 100, 0 )
    slot = face.contents.glyph

    # set up matrix
    matrix.xx = (int)( math.cos( angle ) * 0x10000L )
    matrix.xy = (int)(-math.sin( angle ) * 0x10000L )
    matrix.yx = (int)( math.sin( angle ) * 0x10000L )
    matrix.yy = (int)( math.cos( angle ) * 0x10000L )

    # the pen position in 26.6 cartesian space coordinates; */
    # start at (300,200) relative to the upper left corner  */
    pen.x = 200 * 64;
    pen.y = ( HEIGHT - 300 ) * 64

    for n in range(num_chars):
        # set transformation
        FT_Set_Transform( face, byref(matrix), byref(pen) )

        # load glyph image into the slot (erase previous one)
        charcode = ord(text[n])
        index = FT_Get_Char_Index( face, charcode )
        FT_Load_Glyph( face, index, FT_LOAD_RENDER )

        # now, draw to our target surface (convert position)
        draw_bitmap( slot.contents.bitmap,
                     slot.contents.bitmap_left,
                     HEIGHT - slot.contents.bitmap_top )

        # increment pen position
        pen.x += slot.contents.advance.x
        pen.y += slot.contents.advance.y

    FT_Done_Face(face)
    FT_Done_FreeType(library)

    import matplotlib.pyplot as plt
    plt.imshow(image, origin='lower',
               interpolation='nearest', cmap=plt.cm.gray)
    plt.show()
