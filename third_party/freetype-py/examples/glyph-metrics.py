#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Show glyph metrics in horizontal and vertical layout
'''
from freetype import *

def arrow( x,y, dx, dy, **kwargs):
    kwargs['shape'] = 'full'
    kwargs['head_width'] = 30
    kwargs['head_length'] = 40
    kwargs['length_includes_head'] =True
    kwargs['facecolor'] = 'k'
    kwargs['edgecolor'] ='k'
    kwargs['linewidth'] =.5
    plt.arrow(x,y,dx,dy,**kwargs)

def double_arrow(x, y, dx, dy, **kwargs):
    cx,cy = x+dx/2., y+dy/2.
    dx /= 2.0
    dy /= 2.0
    arrow(cx,cy,+dx,+dy,**kwargs)
    arrow(cx,cy,-dx,-dy,**kwargs)

def line(x, y, dx, dy, **kwargs):
    kwargs['color'] = 'k'
    kwargs['linewidth'] =.5
    plt.plot([x,x+dx],[y,y+dy],**kwargs)

def point(x, y, r, **kwargs):
    kwargs['color'] = 'k'
    plt.scatter([x],[y],r,**kwargs)
    
def text( x,y,text, **kwargs):
    kwargs['fontsize'] = 18
    plt.text(x, y, text, **kwargs)



if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches


    face = Face('./Vera.ttf')
    face.set_char_size( 32*64 )
    face.load_char('g')
    slot = face.glyph
    bitmap = slot.bitmap
    width  = slot.bitmap.width
    rows   = slot.bitmap.rows
    pitch  = slot.bitmap.pitch
    outline= slot.outline

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
    VERTS = np.array(VERTS)
    x,y = VERTS[:,0], VERTS[:,1]
    VERTS[:,0], VERTS[:,1] = x, y


    path = Path(VERTS, CODES)
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    width,height = xmax-xmin, ymax-ymin
    dw, dh = 0.2*width, 0.1*height
    bearing = xmin - slot.metrics.horiBearingX, ymin - slot.metrics.horiBearingY
    advance = slot.advance
    origin  = bearing


    figure = plt.figure(figsize=(16,10), frameon=False, facecolor="white")

    axes = plt.subplot(121, frameon=False, aspect=1)
    glyph = patches.PathPatch(path, fill = True, facecolor='k', lw=0)
    plt.xlim(xmin - .25*width,  xmax + .75*width)
    plt.ylim(ymin - .5*height, xmax + .75*height)
    plt.xticks([]), plt.yticks([])
    axes.add_patch(glyph)

    # Y axis
    arrow(origin[0], ymin-dh, 0, height+3*dh)

    # X axis
    arrow(origin[0]-dw, 0, width+3*dw, 0)

    # origin
    point(0,0,50)
    text( -20, -20, "$origin$", va='top', ha='right')

    # Bounding box
    bbox = patches.Rectangle( (xmin,ymin), width, height, fill = False, lw=.5)
    axes.add_patch(bbox)

    # Width
    line(xmin, ymax, 0, 3*dh, linestyle="dotted")
    text( xmin, ymax+3.25*dh, "$x_{min}$", va='bottom', ha='center')
    line(xmax, ymax, 0, 3*dh, linestyle="dotted")
    text( xmax, ymax+3.25*dh, "$x_{max}$", va='bottom', ha='center')
    double_arrow(xmin, ymax+2.5*dh, width, 0)
    text(xmin+width/2., ymax+1.75*dh, "$width$", va='bottom', ha='center')

    # Height
    line(xmax, ymin, 3*dw, 0, linestyle="dotted")
    text(xmax+3.25*dw, ymin, "$y_{min}$", va='baseline', ha='left')
    line(xmax, ymax, 3*dw, 0, linestyle="dotted")
    text(xmax+3.25*dw, ymax, "$y_{max}$", va='baseline', ha='left')
    double_arrow(xmax+2.5*dw, ymin, 0, height)
    text(xmax+2.75*dw, ymin+height/2., "$height$", va='center', ha='left')

    # Advance
    point(advance.x,0,50)
    line(advance.x, 0, 0, ymin-dh, linestyle="dotted")
    arrow(0, ymin-.5*dh, advance.x, 0)
    text(advance.x/2., ymin-1.25*dh, "$advance$", va='bottom', ha='center')

    # Bearing Y
    arrow(xmax+.25*dw, 0, 0, ymax)
    text(xmax+.5*dw, ymax/2, "$Y_{bearing}$", va='center', ha='left')

    # Bearing X
    arrow(0, ymax/2., xmin, 0)
    text(-10, ymax/2, "$X_{bearing}$", va='baseline', ha='right')

    
    # -------------------------------------------------------------------------

    axes = plt.subplot(122, frameon=False, aspect=1)
    glyph = patches.PathPatch(path, fill = True, facecolor='k', lw=0)
    axes.add_patch(glyph)

    plt.xlim(xmin - .25*width,  xmax + .75*width)
    plt.ylim(ymin - .5*height, xmax + .75*height)
    plt.xticks([]), plt.yticks([])


    advance   = slot.metrics.vertAdvance
    x_bearing = slot.metrics.vertBearingX
    y_bearing = slot.metrics.vertBearingY

    # Y axis
    arrow(xmin-x_bearing, ymax+y_bearing+2*dh, 0, -advance-3*dh)

    # X axis
    arrow(xmin-2*dw, ymax+y_bearing, width+4*dw, 0)

    # origin
    point( xmin-x_bearing, ymax+y_bearing, 50)
    text( xmin-x_bearing-30, ymax+y_bearing+10, "$origin$", va='bottom', ha='right')

    # Bounding box
    bbox = patches.Rectangle( (xmin,ymin), width, height, fill = False, lw=.5)
    axes.add_patch(bbox)


    # # Advance
    point(xmin-x_bearing, ymax+y_bearing-advance, 50)
    line(xmin-x_bearing, ymax+y_bearing-advance, xmax-dw, 0, linestyle="dotted")
    arrow(xmax+dw, ymax+y_bearing, 0, -advance)
    text(xmax+1.25*dw, ymax+y_bearing-advance/2., "$advance$", va='baseline', ha='left')


    # Width
    line(xmin, ymin, 0, -4*dh, linestyle="dotted")
    text( xmin, ymin-4.25*dh, "$x_{min}$", va='top', ha='center')
    line(xmax, ymin, 0, -4*dh, linestyle="dotted")
    text( xmax, ymin-4.25*dh, "$x_{max}$", va='top', ha='center')
    double_arrow(xmin, ymin-3.5*dh, width, 0)
    text(xmin+width/2., ymin-3.75*dh, "$width$", va='top', ha='center')

    # Height
    line(xmin, ymin, -3*dw, 0, linestyle="dotted")
    text(xmin-1.5*dw, ymin, "$y_{min}$", va='baseline', ha='right')
    line(xmin, ymax, -3*dw, 0, linestyle="dotted")
    text(xmin-1.5*dw, ymax, "$y_{max}$", va='baseline', ha='right')
    double_arrow(xmin-.5*dw, ymin, 0, height)
    text(xmin-.75*dw, ymin+height/2., "$height$", va='center', ha='right')


    #point(xmin-x_bearing, ymax+y_bearing, 50)
    # Bearing Y
    arrow(xmax-.5*dw, ymax+y_bearing, 0, -y_bearing)
    text(xmax-.5*dw, ymax+y_bearing+.25*dh, "$Y_{bearing}$", va='bottom', ha='center')

    # # Bearing X
    line(xmin, ymax, 0, 3*dh, linestyle="dotted")
    arrow(xmin-x_bearing, ymax+y_bearing+dh, x_bearing, 0)
    text(xmin-.25*dw,  ymax+y_bearing+dh, "$X_{bearing}$", va='baseline', ha='right')

    plt.savefig('glyph-metrics.pdf')
    plt.show()
