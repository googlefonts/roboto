#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Show how to access glyph outline description.
'''
from freetype import *

if __name__ == '__main__':
    import numpy
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches

    face = Face('./Vera.ttf')
    face.set_char_size( 32*64 )
    face.load_char('g')
    slot = face.glyph

    bitmap = face.glyph.bitmap
    width  = face.glyph.bitmap.width
    rows   = face.glyph.bitmap.rows
    pitch  = face.glyph.bitmap.pitch

    data = []
    for i in range(rows):
        data.extend(bitmap.buffer[i*pitch:i*pitch+width])
    Z = numpy.array(data,dtype=numpy.ubyte).reshape(rows, width)

    outline = slot.outline
    points = numpy.array(outline.points, dtype=[('x',float), ('y',float)])
    x, y = points['x'], points['y']

    figure = plt.figure(figsize=(8,10))
    axis = figure.add_subplot(111)
    #axis.scatter(points['x'], points['y'], alpha=.25)
    start, end = 0, 0

    VERTS, CODES = [], []
    # Iterate over each contour
    for i in range(len(outline.contours)):
        end    = outline.contours[i]
        points = outline.points[start:end+1]
        points.append(points[0])
        tags   = outline.tags[start:end+1]
        tags.append(tags[0])

        segments = [ [points[0],], ]
        for j in range(1, len(points) ):
            segments[-1].append(points[j])
            if tags[j] & (1 << 0) and j < (len(points)-1):
                segments.append( [points[j],] )
        verts = [points[0], ]
        codes = [Path.MOVETO,]
        for segment in segments:
            if len(segment) == 2:
                verts.extend(segment[1:])
                codes.extend([Path.LINETO])
            elif len(segment) == 3:
                verts.extend(segment[1:])
                codes.extend([Path.CURVE3, Path.CURVE3])
            else:
                verts.append(segment[1])
                codes.append(Path.CURVE3)
                for i in range(1,len(segment)-2):
                    A,B = segment[i], segment[i+1]
                    C = ((A[0]+B[0])/2.0, (A[1]+B[1])/2.0)
                    verts.extend([ C, B ])
                    codes.extend([ Path.CURVE3, Path.CURVE3])
                verts.append(segment[-1])
                codes.append(Path.CURVE3)
        VERTS.extend(verts)
        CODES.extend(codes)
        start = end+1


    # Draw glyph
    path = Path(VERTS, CODES)
    glyph = patches.PathPatch(path, fill = True, facecolor=(0.8,0.5,0.8), alpha=.25, lw=0)
    glyph_outline = patches.PathPatch(path, fill = False, edgecolor='black', lw=3)

    plt.imshow(Z, extent=[x.min(), x.max(),y.min(), y.max()], origin='lower',
               interpolation='nearest', cmap = plt.cm.gray_r, vmin=0, vmax=400)
    plt.xticks(numpy.linspace(x.min(), x.max(), Z.shape[1]+1), ())
    plt.yticks(numpy.linspace(y.min(), y.max(), Z.shape[0]+1), ())
    plt.grid(color='k', linewidth=1, linestyle='-')
    axis.add_patch(glyph)
    axis.add_patch(glyph_outline)
    axis.set_xlim(x.min(), x.max())
    axis.set_ylim(y.min(), y.max())

    plt.savefig('test.svg')
    plt.show()
