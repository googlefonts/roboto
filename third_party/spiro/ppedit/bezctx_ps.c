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
#include <stdio.h>

#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_ps.h"

typedef struct {
    bezctx base;
    int is_open;
    double x, y;
    FILE *f;
} bezctx_ps;

const char *ps_prolog = "%!PS\n"
"/m { moveto } bind def\n"
"/l { lineto } bind def\n"
"/c { curveto } bind def\n"
"/z { closepath } bind def\n"
"1 -1 scale\n"
"0 -792 translate\n";

const char *ps_postlog = "stroke\n"
"showpage\n";

static void
bezctx_ps_moveto(bezctx *z, double x, double y, int is_open) {
    bezctx_ps *bc = (bezctx_ps *)z;

    if (!bc->is_open) fprintf(bc->f, "z\n");
    fprintf(bc->f, "%g %g m\n", x, y);
    bc->is_open = is_open;
    bc->x = x;
    bc->y = y;
}

void
bezctx_ps_lineto(bezctx *z, double x, double y) {
    bezctx_ps *bc = (bezctx_ps *)z;

    fprintf(bc->f, "%g %g l\n", x, y);
    bc->x = x;
    bc->y = y;
}

void
bezctx_ps_quadto(bezctx *z, double xm, double ym, double x3, double y3)
{
    bezctx_ps *bc = (bezctx_ps *)z;
    double x0, y0;
    double x1, y1;
    double x2, y2;

    x0 = bc->x;
    y0 = bc->y;
    x1 = xm + (1./3) * (x0 - xm);
    y1 = ym + (1./3) * (y0 - ym);
    x2 = xm + (1./3) * (x3 - xm);
    y2 = ym + (1./3) * (y3 - ym);
    fprintf(bc->f, "%g %g %g %g %g %g c\n", x1, y1, x2, y2, x3, y3);
    bc->x = x3;
    bc->y = y3;
}

void
bezctx_ps_curveto(bezctx *z, double x1, double y1, double x2, double y2,
		  double x3, double y3)
{
    bezctx_ps *bc = (bezctx_ps *)z;

    fprintf(bc->f, "%g %g %g %g %g %g c\n", x1, y1, x2, y2, x3, y3);
    bc->x = x3;
    bc->y = y3;
}

bezctx *
new_bezctx_ps(FILE *f) {
    bezctx_ps *result = znew(bezctx_ps, 1);

    result->base.moveto = bezctx_ps_moveto;
    result->base.lineto = bezctx_ps_lineto;
    result->base.quadto = bezctx_ps_quadto;
    result->base.curveto = bezctx_ps_curveto;
    result->base.mark_knot = NULL;
    result->is_open = 1;
    result->f = f;
    return &result->base;
}

void
bezctx_ps_close(bezctx *z)
{
    bezctx_ps *bc = (bezctx_ps *)z;

    if (!bc->is_open) fprintf(bc->f, "z\n");
    zfree(bc);
}
