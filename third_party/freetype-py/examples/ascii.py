#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
import numpy
import os, sys
from freetype import *


class ColorMap:
    ''' A colormap is used to map scalar values to colors. It is build by
        adding couples of (value,color) where value must be between 0 and 1.
        The 'scale' method allows to specify the range of the colormap and
        the 'color' method then returns a color for any value. '''

    def __init__ (self, colors):
        self.colors = colors
        self.min    = 0
        self.max    = 1

    def scale (self, min, max):
        self.min, self.max = min,max

    def color (self, value):
        ''' Return the color corresponding to value. '''
        if not len(self.colors):
            return (0,0,0)
        elif len(self.colors) == 1:
            return self.colors[0][1]
        elif value < self.min:
            return self.colors[0][1]
        elif value > self.max:
            return self.colors[-1][1]
        value = (value-self.min)/(self.max-self.min)
        sup_color = self.colors[0]
        inf_color = self.colors[-1]
        for i in range (len(self.colors)-1):
            if value < self.colors[i+1][0]:
                inf_color = self.colors[i]
                sup_color = self.colors[i+1]
                break
        r = (value-inf_color[0]) / (sup_color[0] - inf_color[0])
        if r < 0: r = -r
        color = [sup_color[1][0]*r + inf_color[1][0]*(1-r),
                 sup_color[1][1]*r + inf_color[1][1]*(1-r),
                 sup_color[1][2]*r + inf_color[1][2]*(1-r)]
        return color

# Some colormaps
CM_IceAndFire = ColorMap([(0.00, (0.0, 0.0, 1.0)),
                         (0.25, (0.0, 0.5, 1.0)),
                         (0.50, (1.0, 1.0, 1.0)),
                         (0.75, (1.0, 1.0, 0.0)),
                         (1.00, (1.0, 0.0, 0.0))])
CM_Ice = ColorMap([(0.00, (0.0, 0.0, 1.0)),
                   (0.50, (0.5, 0.5, 1.0)),
                   (1.00, (1.0, 1.0, 1.0))])
CM_Fire = ColorMap([(0.00, (1.0, 1.0, 1.0)),
                    (0.50, (1.0, 1.0, 0.0)),
                    (1.00, (1.0, 0.0, 0.0))])
CM_Hot = ColorMap([(0.00, (0.0, 0.0, 0.0)),
                   (0.33, (1.0, 0.0, 0.0)),
                   (0.66, (1.0, 1.0, 0.0)),
                   (1.00, (1.0, 1.0, 1.0))])
CM_Grey = ColorMap([(0.00, (0.0, 0.0, 0.0)),
                    (1.00, (1.0, 1.0, 1.0))])



def imshow (Z, vmin=None, vmax=None, cmap=CM_Hot, show_cmap=False):
    ''' Show a 2D numpy array using terminal colors '''

    if len(Z.shape) != 2:
        print "Cannot display non 2D array"
        return

    vmin = vmin or Z.min()
    vmax = vmax or Z.max()
    cmap.scale (vmin, vmax)

    # Build initialization string that setup terminal colors
    init = ''
    for i in range(240):
        v = cmap.min + (i/240.0)* (cmap.max - cmap.min)
        r,g,b = cmap.color (v)
        init += "\x1b]4;%d;rgb:%02x/%02x/%02x\x1b\\" % (16+i, int(r*255),int(g*255),int(b*255))

    # Build array data string
    data = ''
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            c = 16 + int( ((Z[Z.shape[0]-i-1,j]-cmap.min) / (cmap.max-cmap.min))*239)
            if (c < 16):
                c=16
            elif (c > 255):
                c=255
            data += "\x1b[48;5;%dm  " % c
            u = cmap.max - (i/float(Z.shape[0]-1)) * ((cmap.max-cmap.min))
        if show_cmap:
            data += "\x1b[0m  "
            data += "\x1b[48;5;%dm  " % (16 + (1-i/float(Z.shape[0]))*239)
            data += "\x1b[0m %+.2f" % u
        data += "\x1b[0m\n"
    print init+data[:-1]+'\x1b[0m'


if __name__ == '__main__':
    face = Face('./Vera.ttf')
    face.set_char_size( 32*64 )
    face.load_glyph(face.get_char_index('S'))
    slot = face.glyph
    bitmap = slot.bitmap
    data, rows, width = bitmap.buffer, bitmap.rows, bitmap.width
    Z = numpy.array(data,dtype=float).reshape(rows,width)
    Z = Z[::-1,:]
    imshow (Z, cmap=CM_Grey)

