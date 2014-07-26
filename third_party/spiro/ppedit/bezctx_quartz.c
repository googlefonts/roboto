/*
ppedit - A pattern plate editor for Spiro splines.
Copyright (C) 2007 Raph Levien

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

*/
#include <Carbon/Carbon.h>

#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_quartz.h"


typedef struct {
    bezctx base;
    CGMutablePathRef pathref;
    int is_open;
} bezctx_quartz;

static void
bezctx_quartz_moveto(bezctx *z, double x, double y, int is_open) {
    bezctx_quartz *bc = (bezctx_quartz *)z;
    if (!bc->is_open) CGPathCloseSubpath(bc->pathref);
    CGPathMoveToPoint(bc->pathref, NULL, x, y);
    bc->is_open = is_open;
}

static void
bezctx_quartz_lineto(bezctx *z, double x, double y) {
    bezctx_quartz *bc = (bezctx_quartz *)z;
    CGPathAddLineToPoint(bc->pathref, NULL, x, y);
}

static void
bezctx_quartz_quadto(bezctx *z, double x1, double y1, double x2, double y2)
{
    bezctx_quartz *bc = (bezctx_quartz *)z;
    CGPathAddQuadCurveToPoint(bc->pathref, NULL, x1, y1, x2, y2);
}

bezctx *
new_bezctx_quartz(void) {
    bezctx_quartz *result = znew(bezctx_quartz, 1);

    result->base.moveto = bezctx_quartz_moveto;
    result->base.lineto = bezctx_quartz_lineto;
    result->base.quadto = bezctx_quartz_quadto;
    result->base.mark_knot = NULL;
    result->pathref = CGPathCreateMutable();
    result->is_open = 1;
    return &result->base;
}


CGMutablePathRef
bezctx_to_quartz(bezctx *z)
{
    bezctx_quartz *bc = (bezctx_quartz *)z;
    CGMutablePathRef result = bc->pathref;

    if (!bc->is_open) CGPathCloseSubpath(result);
    zfree(bc);
    return result;
}
