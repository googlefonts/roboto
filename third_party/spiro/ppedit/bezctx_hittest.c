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
#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_hittest.h"
#include <math.h>

typedef struct {
    bezctx base;
    double x, y;

    double x0, y0;
    int knot_idx;

    int knot_idx_min;
    double r_min;
} bezctx_hittest;

static void
bezctx_hittest_moveto(bezctx *z, double x, double y, int is_open) {
    bezctx_hittest *bc = (bezctx_hittest *)z;

    bc->x0 = x;
    bc->y0 = y;
}

static void
bezctx_hittest_lineto(bezctx *z, double x, double y) {
    bezctx_hittest *bc = (bezctx_hittest *)z;
    double x0 = bc->x0;
    double y0 = bc->y0;
    double dx = x - x0;
    double dy = y - y0;
    double dotp = (bc->x - x0) * dx + (bc->y - y0) * dy;
    double lin_dotp = dx * dx + dy * dy;
    double r_min, r;

    r = hypot(bc->x - x0, bc->y - y0);
    r_min = r;
    r = hypot(bc->x - x, bc->y - y);
    if (r < r_min) r_min = r;

    if (dotp >= 0 && dotp <= lin_dotp) {
	double norm = (bc->x - x0) * dy - (bc->y - y0) * dx;
	r = fabs(norm / sqrt(lin_dotp));
	if (r < r_min) r_min = r;
    }

    if (r_min < bc->r_min) {
	bc->r_min = r_min;
	bc->knot_idx_min = bc->knot_idx;
    }

    bc->x0 = x;
    bc->y0 = y;
}

#define cube(x) ((x) * (x) * (x))

static double
my_cbrt(double x)
{
    if (x >= 0)
	return pow(x, 1.0 / 3.0);
    else
	return -pow(-x, 1.0 / 3.0);
}

/**
 * Give real roots to eqn c0 + c1 * x + c2 * x^2 + c3 * x^3 == 0.
 * Return value is number of roots found.
 **/
static int
solve_cubic(double c0, double c1, double c2, double c3, double root[3])
{
    double p, q, r, a, b, Q, x0;

    p = c2 / c3;
    q = c1 / c3;
    r = c0 / c3;
    a = (3 * q - p * p) / 3;
    b = (2 * cube(p) - 9 * p * q + 27 * r) / 27;
    Q = b * b / 4 + cube(a) / 27;
    x0 = p / 3;
    if (Q > 0) {
        double sQ = sqrt(Q);
        double t1 = my_cbrt(-b/2 + sQ) + my_cbrt(-b/2 - sQ);
	root[0] = t1 - x0;
        return 1;
    } else if (Q == 0) {
        double t1 = my_cbrt(b / 2);
        double x1 = t1 - x0;
	root[0] = x1;
	root[1] = x1;
	root[2] = -2 * t1 - x0;
        return 3;
    } else {
        double sQ = sqrt(-Q);
        double rho = hypot(-b/2, sQ);
        double th = atan2(sQ, -b/2);
        double cbrho = my_cbrt(rho);
        double c = cos(th / 3);
        double s = sin(th / 3);
	double sqr3 = sqrt(3);
	root[0] = 2 * cbrho * c - x0;
	root[1] = -cbrho * (c + sqr3 * s) - x0;
	root[2] = -cbrho * (c - sqr3 * s) - x0;
	return 3;
    }
}


static double
dist_to_quadratic(double x, double y,
		  double x0, double y0,
		  double x1, double y1,
		  double x2, double y2)
{
    double u0, u1, t0, t1, t2, c0, c1, c2, c3;
    double roots[3];
    int n_roots;
    double ts[4];
    int n_ts;
    int i;
    double minerr = 0;

    u0 = x1 - x0;
    u1 = x0 - 2 * x1 + x2;
    t0 = x0 - x;
    t1 = 2 * u0;
    t2 = u1;
    c0 = t0 * u0;
    c1 = t1 * u0 + t0 * u1;
    c2 = t2 * u0 + t1 * u1;
    c3 =           t2 * u1;

    u0 = y1 - y0;
    u1 = y0 - 2 * y1 + y2;
    t0 = y0 - y;
    t1 = 2 * u0;
    t2 = u1;
    c0 += t0 * u0;
    c1 += t1 * u0 + t0 * u1;
    c2 += t2 * u0 + t1 * u1;
    c3 +=           t2 * u1;

    n_roots = solve_cubic(c0, c1, c2, c3, roots);
    n_ts = 0;
    for (i = 0; i < n_roots; i++) {
	double t = roots[i];
	if (t > 0 && t < 1)
	    ts[n_ts++] = t;
    }
    if (n_ts < n_roots) {
	ts[n_ts++] = 0;
	ts[n_ts++] = 1;
    }
    for (i = 0; i < n_ts; i++) {
        double t = ts[i];
	double xa = x0 * (1 - t) * (1 - t) + 2 * x1 * (1 - t) * t + x2 * t * t;
	double ya = y0 * (1 - t) * (1 - t) + 2 * y1 * (1 - t) * t + y2 * t * t;
	double err = hypot(xa - x, ya - y);
	if (i == 0 || err < minerr) {
	    minerr = err;
	}
    }
    return minerr;
}

static void
bezctx_hittest_quadto(bezctx *z, double x1, double y1, double x2, double y2)
{
    bezctx_hittest *bc = (bezctx_hittest *)z;
    double r = dist_to_quadratic(bc->x, bc->y,
				 bc->x0, bc->y0, x1, y1, x2, y2);

    if (r < bc->r_min) {
	bc->r_min = r;
	bc->knot_idx_min = bc->knot_idx;
    }
    bc->x0 = x2;
    bc->y0 = y2;
}

static void
bezctx_hittest_curveto(bezctx *z, double x1, double y1, double x2, double y2,
		       double x3, double y3)
{
    bezctx_hittest *bc = (bezctx_hittest *)z;
    double x0 = bc->x0;
    double y0 = bc->y0;
    int n_subdiv = 32;
    int i;
    double xq2, yq2;

    /* todo: subdivide to quadratics rather than lines */
    for (i = 0; i < n_subdiv; i++) {
	double t = (1. / n_subdiv) * (i + 1);
	double mt = 1 - t;

	xq2 = x0 * mt * mt * mt + 3 * x1 * mt * t * t + 3 * x2 * mt * mt * t +
	    x3 * t * t * t;
	yq2 = y0 * mt * mt * mt + 3 * y1 * mt * t * t + 3 * y2 * mt * mt * t +
	    y3 * t * t * t;
	bezctx_hittest_lineto(z, xq2, yq2);
    }
}

static void
bezctx_hittest_mark_knot(bezctx *z, int knot_idx) {
    bezctx_hittest *bc = (bezctx_hittest *)z;

    bc->knot_idx = knot_idx;
}

bezctx *
new_bezctx_hittest(double x, double y) {
    bezctx_hittest *result = znew(bezctx_hittest, 1);

    result->base.moveto = bezctx_hittest_moveto;
    result->base.lineto = bezctx_hittest_lineto;
    result->base.quadto = bezctx_hittest_quadto;
    result->base.curveto = bezctx_hittest_curveto;
    result->base.mark_knot = bezctx_hittest_mark_knot;
    result->x = x;
    result->y = y;
    result->knot_idx_min = -1;
    result->r_min = 1e12;
    return &result->base;
}

double
bezctx_hittest_report(bezctx *z, int *p_knot_idx)
{
    bezctx_hittest *bc = (bezctx_hittest *)z;
    double r_min = bc->r_min;

    if (p_knot_idx)
	*p_knot_idx = bc->knot_idx_min;

    zfree(z);
    return r_min;
}
