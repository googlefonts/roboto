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
#include <x3.h>
#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_x3.h"

typedef struct {
    bezctx base;
    x3dc *dc;
    int is_open;
} bezctx_x3;

static void
bezctx_x3_moveto(bezctx *z, double x, double y, int is_open) {
    bezctx_x3 *bc = (bezctx_x3 *)z;

    if (!bc->is_open) x3closepath(bc->dc);
    x3moveto(bc->dc, x, y);
    bc->is_open = is_open;
}

void
bezctx_x3_lineto(bezctx *z, double x, double y) {
    bezctx_x3 *bc = (bezctx_x3 *)z;

    x3lineto(bc->dc, x, y);
}

void
bezctx_x3_quadto(bezctx *z, double x1, double y1, double x2, double y2)
{
    bezctx_x3 *bc = (bezctx_x3 *)z;
    double x0, y0;

    x3getcurrentpoint(bc->dc, &x0, &y0);
    x3curveto(bc->dc,
		  x1 + (1./3) * (x0 - x1),
		  y1 + (1./3) * (y0 - y1),
		  x1 + (1./3) * (x2 - x1),
		  y1 + (1./3) * (y2 - y1),
		  x2,
		  y2);
}

void
bezctx_x3_curveto(bezctx *z, double x1, double y1, double x2, double y2,
		      double x3, double y3)
{
    bezctx_x3 *bc = (bezctx_x3 *)z;

    x3curveto(bc->dc, x1, y1, x2, y2, x3, y3);
}

void
bezctx_x3_finish(bezctx *z)
{
    bezctx_x3 *bc = (bezctx_x3 *)z;

    if (!bc->is_open)
	x3closepath(bc->dc);

    zfree(bc);
}

bezctx *
new_bezctx_x3(x3dc *dc) {
    bezctx_x3 *result = znew(bezctx_x3, 1);

    result->base.moveto = bezctx_x3_moveto;
    result->base.lineto = bezctx_x3_lineto;
    result->base.quadto = bezctx_x3_quadto;
    result->base.curveto = bezctx_x3_curveto;
    result->base.mark_knot = NULL;
    result->dc = dc;
    result->is_open = 1;
    return &result->base;
}
