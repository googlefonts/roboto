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
#include <string.h>
#include <math.h>
#include <stdio.h>

#include "zmisc.h"
#include "sexp.h"
#include "bezctx_intf.h"
#include "bezctx_hittest.h"
#include "cornu.h"
#include "spiro.h"
#include "plate.h"

/* This is a global while we're playing with the tangent solver. Once we get that
   nailed down, it will go away. */
extern int n_iter;

/**
 * These are functions for editing a Cornu spline ("plate"), intended
 * to be somewhat independent of the UI toolkit specifics.
 **/

plate *
new_plate(void)
{
    plate *p = znew(plate, 1);

    p->n_sp = 0;
    p->n_sp_max = 4;
    p->sp = znew(subpath, p->n_sp_max);
    p->mmode = MOUSE_MODE_ADD_CURVE;
    p->last_curve_mmode = p->mmode;
    return p;
}

void
free_plate(plate *p)
{
    int i;
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];
	zfree(sp->kt);
    }
    zfree(p->sp);
    zfree(p);
}

plate *
copy_plate(const plate *p)
{
    int i;
    plate *n = znew(plate, 1);

    n->n_sp = p->n_sp;
    n->n_sp_max = p->n_sp_max;
    n->sp = znew(subpath, n->n_sp_max);
    for (i = 0; i < n->n_sp; i++) {
	subpath *sp = &p->sp[i];
	subpath *nsp = &n->sp[i];

	nsp->n_kt = sp->n_kt;
	nsp->n_kt_max = sp->n_kt_max;
	nsp->kt = znew(knot, nsp->n_kt_max);
	memcpy(nsp->kt, sp->kt, nsp->n_kt * sizeof(knot));
	nsp->closed = sp->closed;
    }
    n->mmode = p->mmode;
    return n;
}

void
plate_select_all(plate *p, int selected)
{
    int i, j;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    knot *kt = &sp->kt[j];
	    kt->flags &= ~KT_SELECTED;
	    if (selected)
		kt->flags |= KT_SELECTED;
	}
    }
}

subpath *
plate_find_selected_sp(plate *p)
{
    int i, j;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    knot *kt = &sp->kt[j];
	    if (kt->flags & KT_SELECTED)
		return sp;
	}
    }
    return NULL;
}

subpath *
plate_new_sp(plate *p)
{
    subpath *sp;
    if (p->n_sp == p->n_sp_max)
	p->sp = zrenew(subpath, p->sp, p->n_sp_max <<= 1);
    sp = &p->sp[p->n_sp++];
    sp->n_kt = 0;
    sp->n_kt_max = 4;
    sp->kt = znew(knot, sp->n_kt_max);
    sp->closed = 0;
    return sp;
}

static int
try_close_sp(subpath *sp, int ix, int force)
{
    int n_kt = sp->n_kt;

    if (sp->closed) return 0;
    if (n_kt < 3) return 0;
    if (!force) {
	if (ix != 0 && ix != n_kt - 1) return 0;
	if (!(sp->kt[n_kt - 1 - ix].flags & KT_SELECTED)) return 0;
    }
    sp->closed = 1;
    return 1;
}

void
plate_press(plate *p, double x, double y, press_mod mods)
{
    int i, j;
    subpath *sp;
    knot *kt;
    const double srad = 5;
    kt_flags new_kt_flags = KT_SELECTED;

    if (p->mmode == MOUSE_MODE_ADD_CORNER)
	new_kt_flags |= (mods & PRESS_MOD_CTRL) ? KT_OPEN : KT_CORNER;
    else if (p->mmode == MOUSE_MODE_ADD_CORNU)
	new_kt_flags |= (mods & PRESS_MOD_CTRL) ? KT_CORNER : KT_CORNU;
    else if (p->mmode == MOUSE_MODE_ADD_LEFT)
	new_kt_flags |= (mods & PRESS_MOD_CTRL) ? KT_CORNER : KT_LEFT;
    else if (p->mmode == MOUSE_MODE_ADD_RIGHT)
	new_kt_flags |= (mods & PRESS_MOD_CTRL) ? KT_CORNER : KT_RIGHT;
    else
	new_kt_flags |= (mods & PRESS_MOD_CTRL) ? KT_CORNER : KT_OPEN;

    p->x0 = x;
    p->y0 = y;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    kt = &sp->kt[j];
	    if (hypot(kt->x - x, kt->y - y) < srad) {
		int was_closed = try_close_sp(sp, j, mods & PRESS_MOD_DOUBLE);
		if (mods & PRESS_MOD_SHIFT) {
		    kt->flags ^= KT_SELECTED;
		} else if (!(kt->flags & KT_SELECTED)) {
		    plate_select_all(p, 0);
		    kt->flags |= KT_SELECTED;
		}
		p->description = was_closed ? "Close Path" : NULL;
		p->motmode = MOTION_MODE_MOVE;
		return;
	    }
	}
    }

    if (p->mmode == MOUSE_MODE_ADD_RIGHT || p->mmode == MOUSE_MODE_ADD_LEFT)
	p->mmode = p->last_curve_mmode;


#if 1
    /* test whether the button press was on a curve; if so, insert point */
    for (i = 0; i < p->n_sp; i++) {
	bezctx *bc = new_bezctx_hittest(x, y);
	int knot_idx;

	sp = &p->sp[i];
	free_spiro(draw_subpath(sp, bc));
	if (bezctx_hittest_report(bc, &knot_idx) < srad) {
	    knot *kt;

	    if (sp->n_kt == sp->n_kt_max)
		sp->kt = zrenew(knot, sp->kt, sp->n_kt_max <<= 1);
	    plate_select_all(p, 0);
	    kt = &sp->kt[knot_idx + 1];
	    memmove(&kt[1], kt, (sp->n_kt - knot_idx - 1) * sizeof(knot));
	    sp->n_kt++;
	    kt->x = x;
	    kt->y = y;
	    kt->flags = new_kt_flags;
	    p->description = "Insert Point";
	    p->motmode = MOTION_MODE_MOVE;
	    return;
	}
    }
#endif

    if (p->mmode == MOUSE_MODE_SELECT) {
	plate_select_all(p, 0);
	p->sel_x0 = x;
	p->sel_y0 = y;
	p->motmode = MOTION_MODE_SELECT;
	return;
    }

    sp = plate_find_selected_sp(p);
    if (sp == NULL || sp->closed) {
	sp = plate_new_sp(p);
	p->description = p->n_sp > 1 ? "New Subpath" : "New Path";
    }

    if (sp->n_kt == sp->n_kt_max)
	sp->kt = zrenew(knot, sp->kt, sp->n_kt_max <<= 1);
    plate_select_all(p, 0);
    kt = &sp->kt[sp->n_kt++];
    kt->x = x;
    kt->y = y;
    kt->flags = new_kt_flags;
    if (p->description == NULL)
	p->description = "Add Point";
    p->motmode = MOTION_MODE_MOVE;
}

void
plate_motion_move(plate *p, double x, double y)
{
    int i, j, n = 0;
    double dx, dy;

    dx = x - p->x0;
    dy = y - p->y0;
    p->x0 = x;
    p->y0 = y;

    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    knot *kt = &sp->kt[j];
	    if (kt->flags & KT_SELECTED) {
		kt->x += dx;
		kt->y += dy;
		n++;
	    }
	}
    }
    p->description = n == 1 ? "Move Point" : "Move Points";
}

void
plate_motion_select(plate *p, double x1, double y1)
{
    int i, j;
    double x0 = p->sel_x0;
    double y0 = p->sel_y0;

#ifdef VERBOSE
    printf("plate_motion_select %g %g\n", x1, y1);
#endif
    p->x0 = x1;
    p->y0 = y1;

    if (x0 > x1) {
	double tmp = x1;
	x1 = x0;
	x0 = tmp;
    }
    if (y0 > y1) {
	double tmp = y1;
	y1 = y0;
	y0 = tmp;
    }

    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    knot *kt = &sp->kt[j];
	    kt->flags &= ~KT_SELECTED;
	    if (kt->x >= x0 && kt->x <= x1 &&
		kt->y >= y0 && kt->y <= y1)
		kt->flags |= KT_SELECTED;
	}
    }
}

void plate_unpress(plate *p)
{
    p->motmode = MOTION_MODE_IDLE;
}

void
plate_toggle_corner(plate *p)
{
    int i, j;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    knot *kt = &sp->kt[j];
	    if (kt->flags & KT_SELECTED) {
		if (kt->flags & KT_CORNER) {
		    kt->flags |= KT_OPEN;
		    kt->flags &= ~KT_CORNER;
		} else {
		    kt->flags &= ~KT_OPEN;
		    kt->flags |= KT_CORNER;
		}
	    }
	}
    }
}

void
plate_delete_pt(plate *p)
{
    int i, j;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];

	for (j = 0; j < sp->n_kt; j++) {
	    knot *kt = &sp->kt[j];
	    if (kt->flags & KT_SELECTED) {
		memmove(kt, &kt[1], (sp->n_kt - j - 1) * sizeof(knot));
		sp->n_kt--;
		if (sp->n_kt < 3) sp->closed = 0;
		j--;
	    }
	}
    }
}

/* Note: caller is responsible for freeing returned spiro_seg. */
spiro_seg *
draw_subpath(const subpath *sp, bezctx *bc)
{
    int n = sp->n_kt;
    int i;
    spiro_cp *path;
    spiro_seg *s = NULL;

    if (n > 1) {
	path = znew(spiro_cp, n);

	for (i = 0; i < n; i++) {
	    kt_flags flags = sp->kt[i].flags;
	    path[i].x = sp->kt[i].x;
	    path[i].y = sp->kt[i].y;
	    path[i].ty = !sp->closed && i == 0 ? '{' :
		!sp->closed && i == n - 1 ? '}' :
		(flags & KT_OPEN) ? 'o' :
		(flags & KT_LEFT) ? '[' :
		(flags & KT_RIGHT) ? ']' :
		(flags & KT_CORNU) ? 'c' :
		'v';
	}

	s = run_spiro(path, n);
	spiro_to_bpath(s, n, bc);

	zfree(path);
    }
    return s;
} 

int
file_write_plate(const char *fn, const plate *p)
{
    FILE *f = fopen(fn, "w");
    int i, j;
    int st;

    if (f == NULL)
	return -1;
    st = fprintf(f, "(plate\n");
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];
	for (j = 0; j < sp->n_kt; j++) {
	    kt_flags kf = sp->kt[j].flags;
	    const char *cmd;

	    if (kf & KT_OPEN) cmd = "o";
	    else if (kf & KT_CORNER) cmd = "v";
	    else if (kf & KT_CORNU) cmd = "c";
	    else if (kf & KT_LEFT) cmd = "[";
	    else if (kf & KT_RIGHT) cmd = "]";
	    st = fprintf(f, "  (%s %g %g)\n", cmd, sp->kt[j].x, sp->kt[j].y);
	    if (st < 0) break;
	}
	if (st < 0) break;
	if (sp->closed) {
	    st = fprintf(f, "  (z)\n");
	}
	if (st < 0) break;
    }
    if (st >= 0)
	st = fprintf(f, ")\n");
    if (st >= 0)
	st = fclose(f);
    return st < 0 ? -1 : 0;
}

static int
file_read_plate_inner(sexp_reader *sr, plate *p)
{
    subpath *sp = NULL;

    sexp_token(sr);
    if (sr->singlechar != '(') return -1;
    sexp_token(sr);
    if (strcmp(sr->tokbuf, "plate")) return -1;
    for (;;) {
	sexp_token(sr);
	if (sr->singlechar == ')') break;
	else if (sr->singlechar == '(') {
	    int cmd;

	    sexp_token(sr);
	    cmd = sr->singlechar;
	    if (cmd == 'o' || cmd == 'v' || cmd == '[' || cmd == ']' ||
		cmd == 'c') {
		double x, y;
		knot *kt;

		sexp_token(sr);
		if (!sr->is_double) return -1;
		x = sr->d;
		sexp_token(sr);
		if (!sr->is_double) return -1;
		y = sr->d;
		sexp_token(sr);
		if (sr->singlechar != ')') return -1;

		if (sp == NULL || sp->closed)
		    sp = plate_new_sp(p);

		if (sp->n_kt == sp->n_kt_max)
		    sp->kt = zrenew(knot, sp->kt, sp->n_kt_max <<= 1);
		kt = &sp->kt[sp->n_kt++];
		kt->x = x;
		kt->y = y;
		switch (cmd) {
		case 'o':
		    kt->flags = KT_OPEN;
		    break;
		case '[':
		    kt->flags = KT_LEFT;
		    break;
		case ']':
		    kt->flags = KT_RIGHT;
		    break;
		case 'c':
		    kt->flags = KT_CORNU;
		    break;
		default:
		    kt->flags = KT_CORNER;
		    break;
		}
	    } else if (cmd == 'z') {
		if (sp == NULL) return -1;
		sp->closed = 1;
		sexp_token(sr);
		if (sr->singlechar != ')') return -1;
	    } else
		return -1;
	} else return -1;
    }
    return 0;
}

plate *
file_read_plate(const char *fn)
{
    FILE *f = fopen(fn, "r");
    plate *p;
    sexp_reader sr;

    if (f == NULL)
	return NULL;
    sr.f = f;
    p = new_plate();
    if (file_read_plate_inner(&sr, p)) {
	free_plate(p);
	p = NULL;
    }
    fclose(f);
    p->mmode = MOUSE_MODE_SELECT;
    p->motmode = MOTION_MODE_IDLE;
    return p;
}
