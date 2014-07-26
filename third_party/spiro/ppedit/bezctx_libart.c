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
#include <libart_lgpl/libart.h>
#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_libart.h"

typedef struct {
    bezctx base;
    int n_bez;
    int n_bez_max;
    ArtBpath *bez;
} bezctx_libart;

static void
bezctx_libart_moveto(bezctx *z, double x, double y, int is_open) {
    bezctx_libart *bc = (bezctx_libart *)z;
    ArtBpath *bp;

    if (bc->n_bez == bc->n_bez_max) {
	bc->bez = zrenew(ArtBpath, bc->bez, bc->n_bez_max <<= 1);
    }
    bp = &bc->bez[bc->n_bez++];
    bp->code = is_open ? ART_MOVETO_OPEN : ART_MOVETO;
    bp->x3 = x;
    bp->y3 = y;
}

void
bezctx_libart_lineto(bezctx *z, double x, double y) {
    bezctx_libart *bc = (bezctx_libart *)z;
    ArtBpath *bp;

    if (bc->n_bez == bc->n_bez_max) {
	bc->bez = zrenew(ArtBpath, bc->bez, bc->n_bez_max <<= 1);
    }
    bp = &bc->bez[bc->n_bez++];
    bp->code = ART_LINETO;
    bp->x3 = x;
    bp->y3 = y;
}

void
bezctx_libart_quadto(bezctx *z, double x1, double y1, double x2, double y2)
{
    bezctx_libart *bc = (bezctx_libart *)z;
    ArtBpath *bp;
    double x0, y0;

    if (bc->n_bez == bc->n_bez_max) {
	bc->bez = zrenew(ArtBpath, bc->bez, bc->n_bez_max <<= 1);
    }
    bp = &bc->bez[bc->n_bez++];
    x0 = bp[-1].x3;
    y0 = bp[-1].y3;
    bp->code = ART_CURVETO;
    bp->x1 = x1 + (1./3) * (x0 - x1);
    bp->y1 = y1 + (1./3) * (y0 - y1);
    bp->x2 = x1 + (1./3) * (x2 - x1);
    bp->y2 = y1 + (1./3) * (y2 - y1);
    bp->x3 = x2;
    bp->y3 = y2;
}

void
bezctx_libart_curveto(bezctx *z, double x1, double y1, double x2, double y2,
		      double x3, double y3)
{
    bezctx_libart *bc = (bezctx_libart *)z;
    ArtBpath *bp;

    if (bc->n_bez == bc->n_bez_max) {
	bc->bez = zrenew(ArtBpath, bc->bez, bc->n_bez_max <<= 1);
    }
    bp = &bc->bez[bc->n_bez++];
    bp->code = ART_CURVETO;
    bp->x1 = x1;
    bp->y1 = y1;
    bp->x2 = x2;
    bp->y2 = y2;
    bp->x3 = x3;
    bp->y3 = y3;
}

ArtBpath *
bezctx_to_bpath(bezctx *z) {
    bezctx_libart *bc = (bezctx_libart *)z;
    ArtBpath *result;

    if (bc->n_bez == bc->n_bez_max) {
	bc->bez = zrenew(ArtBpath, bc->bez, bc->n_bez_max <<= 1);
    }
    bc->bez[bc->n_bez].code = ART_END;
    result = bc->bez;
    zfree(bc);
    return result;
}

bezctx *
new_bezctx_libart(void) {
    bezctx_libart *result = znew(bezctx_libart, 1);

    result->base.moveto = bezctx_libart_moveto;
    result->base.lineto = bezctx_libart_lineto;
    result->base.quadto = bezctx_libart_quadto;
    result->base.curveto = bezctx_libart_curveto;
    result->base.mark_knot = NULL;
    result->n_bez = 0;
    result->n_bez_max = 4;
    result->bez = znew(ArtBpath, result->n_bez_max);
    return &result->base;
}

