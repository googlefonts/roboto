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

#include "x3.h"

#include <string.h>
#include <stdio.h>
#include <math.h>

#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_x3.h"
#include "bezctx_ps.h"
#include "cornu.h"
#include "spiro.h"
#include "plate.h"
#include "image.h"

int n_iter = 10;

typedef struct {
    const char *description;
    plate *p;
} undo_record;

typedef struct {
    x3widget *view;
    const char *description;
    plate *p;
    int undo_n;
    int undo_i;
    undo_record undo_buf[16];
    int undo_xn_state;

    x3widget *undo_me;
    x3widget *redo_me;

    x3widget *show_knots_me;
    x3widget *show_bg_me;
    int show_knots;
    int show_bg;

    image *bg_image;
} plate_edit;

#define C1 0.55228
static void
draw_dot(x3dc *dc,
	 double x, double y, double r, guint32 rgba)
{
    x3setrgba(dc, rgba);
    x3moveto(dc, x + r, y);
    x3curveto(dc, x + r, y - C1 * r, x + C1 * r, y - r, x, y - r);
    x3curveto(dc, x - C1 * r, y - r, x - r, y - C1 * r, x - r, y);
    x3curveto(dc, x - r, y + C1 * r, x - C1 * r, y + r, x, y + r);
    x3curveto(dc, x + C1 * r, y + r, x + r, y + C1 * r, x + r, y);
    x3fill(dc);
}

static void
draw_raw_rect(x3dc *dc,
	      double rx0, double ry0, double rx1, double ry1, guint32 rgba)
{
    x3setrgba(dc, rgba);
    x3rectangle(dc, rx0, ry0, rx1 - rx0, ry1 - ry0);
    x3fill(dc);
}

static void
draw_rect(x3dc *dc,
	 double x, double y, double r, guint32 rgba)
{
    draw_raw_rect(dc,
		  x - r, y - r, x + r, y + r, rgba);
}

static void
draw_half(x3dc *dc,
	 double x, double y, double r, double th, guint32 rgba)
{
    double c = cos(th);
    double s = sin(th);

    x3setrgba(dc, rgba);
    x3moveto(dc, x + c * r, y + s * r);
    x3curveto(dc,
	      x + c * r + C1 * s * r,
	      y + s * r - C1 * c * r,
	      x + s * r + C1 * c * r,
	      y - c * r + C1 * s * r,
	      x + s * r,
	      y - c * r);
    x3curveto(dc,
	      x + s * r - C1 * c * r,
	      y - c * r - C1 * s * r,
	      x - c * r + C1 * s * r,
	      y - s * r - C1 * c * r,
	      x - c * r,
	      y - s * r);
    x3closepath(dc);
    x3fill(dc);
}

static void
draw_plate(x3dc *dc,
	   plate_edit *pe)
{
    plate *p = pe->p;
    int i, j;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	bezctx *bc = new_bezctx_x3(dc);
	subpath *sp = &p->sp[i];
	spiro_seg *s = draw_subpath(sp, bc);

	bezctx_x3_finish(bc);
	x3setrgba(dc, 0x000000ff);
	x3setlinewidth(dc, 1.5);
	x3stroke(dc);

	for (j = 0; j < sp->n_kt; j++) {
	    if (pe->show_knots) {
		knot *kt = &sp->kt[j];
		kt_flags kf = kt->flags;
		if ((kf & KT_SELECTED) && (kf & KT_OPEN)) {
		    draw_dot(dc, kt->x, kt->y,
			     3, 0x000000ff);
		    draw_dot(dc, kt->x, kt->y,
			     1.5, 0xffffffff);
		} else if ((kf & KT_SELECTED) && (kf & KT_CORNER)) {
		    draw_rect(dc, kt->x, kt->y,
			      3, 0x000000ff);
		    draw_rect(dc, kt->x, kt->y,
			      1.5, 0xffffffff);
		} else if (!(kf & KT_SELECTED) && (kf & KT_CORNER)) {
		    draw_rect(dc, kt->x, kt->y,
			      2.5, 0x000080ff);
		} else if ((kf & KT_SELECTED) && (kf & KT_CORNU)) {
		    draw_rect(dc, kt->x, kt->y,
			      3, 0xc000c0ff);
		    draw_rect(dc, kt->x, kt->y,
			      1.5, 0xffffffff);
		} else if (!(kf & KT_SELECTED) && (kf & KT_CORNU)) {
		    draw_rect(dc, kt->x, kt->y,
			      2.5, 0x800080ff);
		} else if ((kf & KT_LEFT) || (kf & KT_RIGHT)) {
		    double th = 1.5708 + (s ? get_knot_th(s, j) : 0);
		    if (kf & KT_LEFT)
			th += 3.1415926;
		    if (kf & KT_SELECTED) {
			draw_half(dc, kt->x, kt->y,
				 4, th, 0x000000ff);
			draw_half(dc,
				  kt->x + sin(th), kt->y - cos(th),
				  2, th, 0xffffffff);
		    } else {
			draw_half(dc, kt->x, kt->y,
				  3, th, 0x000080ff);
		    }
		} else {
		    draw_dot(dc, kt->x, kt->y,
			     2, 0x000080ff);
		}
	    }
	}
	free_spiro(s);
    }
}

static void
draw_selection(x3dc *dc,
	       plate_edit *pe)
{
    plate *p = pe->p;

    if (p->motmode == MOTION_MODE_SELECT) {
	double rx0 = p->sel_x0;
	double ry0 = p->sel_y0;
	double rx1 = p->x0;
	double ry1 = p->y0;
	if (rx0 > rx1) {
	    double tmp = rx1;
	    rx1 = rx0;
	    rx0 = tmp;
	}
	if (ry0 > ry1) {
	    double tmp = ry1;
	    ry1 = ry0;
	    ry0 = tmp;
	}
	if (rx1 > rx0 && ry1 > ry0)
	    draw_raw_rect(dc,
			  rx0, ry0, rx1, ry1, 0x0000ff20);
    }
}

/* Make sure there's room for at least one more undo record. */
static void
makeroom_undo(plate_edit *pe)
{
    const int undo_max = sizeof(pe->undo_buf) / sizeof(undo_record);

    if (pe->undo_n == undo_max) {
	free_plate(pe->undo_buf[0].p);
	memmove(pe->undo_buf, pe->undo_buf + 1, (undo_max - 1) * sizeof(undo_record));
	pe->undo_i--;
	pe->undo_n--;
    }
}

static void
set_undo_menuitem(x3widget *me, const char *name, const char *desc)
{
    char str[256];

    if (desc) {
	sprintf(str, "%s %s", name, desc);
    } else {
	strcpy(str, name);
    }
#if 0
    gtk_container_foreach(GTK_CONTAINER(me),
			  (GtkCallback)gtk_label_set_text,
			  str);
#endif
    x3setactive(me, desc != NULL);
}

static void
set_undo_state(plate_edit *pe, const char *undo_desc, const char *redo_desc)
{
    set_undo_menuitem(pe->undo_me, "Undo", undo_desc);
    set_undo_menuitem(pe->redo_me, "Redo", redo_desc);
}

static void
begin_undo_xn(plate_edit *pe)
{
    int i;

    if (pe->undo_xn_state != 1) {
	for (i = pe->undo_i; i < pe->undo_n; i++)
	    free_plate(pe->undo_buf[i].p);
	pe->undo_n = pe->undo_i;
	makeroom_undo(pe);
	i = pe->undo_i;
	pe->undo_buf[i].description = pe->description;
	pe->undo_buf[i].p = copy_plate(pe->p);
	pe->undo_n = i + 1;
	pe->undo_xn_state = 1;
    }
}

static void
dirty_undo_xn(plate_edit *pe, const char *description)
{
    if (pe->undo_xn_state == 0) {
	g_warning("dirty_undo_xn: not in begin_undo_xn state");
	begin_undo_xn(pe);
    }
    if (description == NULL)
	description = pe->p->description;
    if (pe->undo_xn_state == 1) {
	pe->undo_i++;
	pe->undo_xn_state = 2;
	set_undo_state(pe, description, NULL);
    }
    pe->description = description;
}

static void
begindirty_undo_xn(plate_edit *pe, const char *description)
{
    begin_undo_xn(pe);
    dirty_undo_xn(pe, description);
}
 
static void
end_undo_xn(plate_edit *pe)
{
    if (pe->undo_xn_state == 0) {
	g_warning("end_undo_xn: not in undo xn");
    }
    pe->undo_xn_state = 0;
}

static int
undo(plate_edit *pe)
{
    if (pe->undo_i == 0)
	return 0;

    if (pe->undo_i == pe->undo_n) {
	makeroom_undo(pe);
	pe->undo_buf[pe->undo_i].description = pe->description;
	pe->undo_buf[pe->undo_i].p = pe->p;
	pe->undo_n++;
    } else {
	free_plate(pe->p);
    }
    pe->undo_i--;
    pe->description = pe->undo_buf[pe->undo_i].description;
    set_undo_state(pe,
		   pe->undo_i > 0 ? pe->description : NULL,
		   pe->undo_buf[pe->undo_i + 1].description);
    g_print("undo: %d of %d\n", pe->undo_i, pe->undo_n);
    pe->p = copy_plate(pe->undo_buf[pe->undo_i].p);
    return 1;
}

static int
redo(plate_edit *pe)
{
    if (pe->undo_i >= pe->undo_n - 1)
	return 0;
    free_plate(pe->p);
    pe->undo_i++;
    set_undo_state(pe,
		   pe->undo_buf[pe->undo_i].description,
		   pe->undo_i < pe->undo_n - 1 ?
		   pe->undo_buf[pe->undo_i + 1].description : NULL);
    pe->description = pe->undo_buf[pe->undo_i].description;
    pe->p = copy_plate(pe->undo_buf[pe->undo_i].p);
    g_print("redo: %d of %d\n", pe->undo_i, pe->undo_n);
    return 1;
}

typedef struct {
    x3viewclient base;

    plate_edit *pe;
} x3vc_ppe;

static void
ppedit_viewclient_draw(x3viewclient *self, x3dc *dc)
{
    plate_edit *pe = ((x3vc_ppe *)self)->pe;

#ifdef VERBOSE
    printf("ppedit draw\n");
#endif
#if 1
    x3setrgba(dc, 0xffffffff);
#else
    x3setrgba(dc, rand() << 8 | 0xff);
#endif
    x3rectangle(dc, dc->x, dc->y, dc->width, dc->height);
    x3fill(dc);

    draw_plate(dc, pe);
    draw_selection(dc, pe);
}

static void
ppedit_viewclient_mouse(x3viewclient *self,
			int button, int mods,
			double x, double y)
{
    x3vc_ppe *z = (x3vc_ppe *)self;
    plate_edit *pe = z->pe;
    plate *p = pe->p;

#ifdef VERBOSE
    printf("ppedit mouse: %d %d %g %g\n", button, mods, x, y);
#endif
    if (button == 1) {
	press_mod pm = 0;

	if (mods & GDK_SHIFT_MASK) pm |= PRESS_MOD_SHIFT;
	if (mods & GDK_CONTROL_MASK) pm |= PRESS_MOD_CTRL;
	if (mods == GDK_2BUTTON_PRESS) pm |= PRESS_MOD_DOUBLE;
	if (mods == GDK_3BUTTON_PRESS) pm |= PRESS_MOD_TRIPLE;

	begin_undo_xn(pe);
	p->description = NULL;
	plate_press(p, x, y, pm);
	if (p->description) dirty_undo_xn(pe, NULL);
	x3view_dirty(pe->view);
    } else if (button == -1) {
	int need_redraw = (pe->p->motmode == MOTION_MODE_SELECT);

	plate_unpress(pe->p);
    
	if (need_redraw) x3view_dirty(pe->view);
    } else if (button == 0 && (mods & GDK_BUTTON1_MASK)) {
	if (p->motmode == MOTION_MODE_MOVE) {
	    plate_motion_move(p, x, y);
	    dirty_undo_xn(pe, NULL);
	} else if (p->motmode == MOTION_MODE_SELECT) {
	    plate_motion_select(p, x, y);
	}
	x3view_dirty(pe->view);
    }
}

static int
ppedit_viewclient_key(x3viewclient *self, char *keyname, int mods, int key)
{
    x3vc_ppe *z = (x3vc_ppe *)self;
    plate_edit *pe = z->pe;
    double dx = 0, dy = 0;
    int did_something = 0;

    if (!strcmp(keyname, "Left"))
	dx = -1;
    else if (!strcmp(keyname, "Right"))
	dx = 1;
    else if (!strcmp(keyname, "Up"))
	dy = -1;
    else if (!strcmp(keyname, "Down"))
	dy = 1;
    if (mods & X3_SHIFT_MASK) {
	dx *= 10;
	dy *= 10;
    } else if (mods & X3_CONTROL_MASK) {
	dx *= .1;
	dy *= .1;
    }
    if (dx != 0 || dy != 0) {
	begindirty_undo_xn(pe, "Keyboard move");
	plate_motion_move(pe->p, pe->p->x0 + dx, pe->p->y0 + dy);
	end_undo_xn(pe);
	did_something = TRUE;
    }
    if (did_something) {
	x3view_dirty(pe->view);
	return 1;
    } else
	return 0;
}

x3viewclient *ppedit_viewclient(plate_edit *pe)
{
    x3vc_ppe *result = (x3vc_ppe *)malloc(sizeof(x3vc_ppe));

    x3viewclient_init(&result->base);
    result->base.draw = ppedit_viewclient_draw;
    result->base.mouse = ppedit_viewclient_mouse;
    result->base.key = ppedit_viewclient_key;
    result->pe = pe;

    return &result->base;
}

int
print_func(plate_edit *pe)
{
    plate *p = pe->p;
    int i;
    FILE *f = fopen("/tmp/foo.ps", "w");
    bezctx *bc = new_bezctx_ps(f);

    fputs(ps_prolog, f);
    for (i = 0; i < p->n_sp; i++) {
	subpath *sp = &p->sp[i];
	free_spiro(draw_subpath(sp, bc));
    }
    bezctx_ps_close(bc);
    fputs(ps_postlog, f);
    fclose(f);
    return TRUE;
}

int
ppedit_callback(x3widget *w, void *data,
	   char *cmd, char *what, char *arg, void *more)
{
    plate_edit *pe = (plate_edit *)data;
    printf("my callback: cmd=\"%s\", what=\"%s\", arg=\"%s\"\n",
	   cmd, what ? what : "(null)", arg ? arg : "(null)");

    if (!strcmp(cmd, "quit")) {
	gtk_main_quit();
    } else if (!strcmp(cmd, "save")) {
	file_write_plate("plate", pe->p);
    } else if (!strcmp(cmd, "khid")) {
	pe->show_knots = !pe->show_knots;
	x3view_dirty(pe->view);
    } else if (!strcmp(cmd, "bghd")) {
	pe->show_bg = !pe->show_bg;
	x3view_dirty(pe->view);
    } else if (!strcmp(cmd, "prin")) {
	return print_func(pe);
    } else if (!strcmp(cmd, "undo")) {
	undo(pe);
	x3view_dirty(pe->view);
    } else if (!strcmp(cmd, "redo")) {
	redo(pe);
	x3view_dirty(pe->view);
    } else if (!strcmp(cmd, "togc")) {
	begindirty_undo_xn(pe, "Toggle Corner");
	plate_toggle_corner(pe->p);
	end_undo_xn(pe);
	x3view_dirty(pe->view);
    } else if (!strcmp(cmd, "delp")) {
	begindirty_undo_xn(pe, "Delete Point");
	plate_delete_pt(pe->p);
	end_undo_xn(pe);
	x3view_dirty(pe->view);
    } else if (!strcmp(cmd, "mods")) {
	pe->p->mmode = MOUSE_MODE_SELECT;
    } else if (!strcmp(cmd, "modo")) {
	pe->p->mmode = MOUSE_MODE_ADD_CURVE;
    } else if (!strcmp(cmd, "modv")) {
	pe->p->mmode = MOUSE_MODE_ADD_CORNER;
    } else if (!strcmp(cmd, "modl")) {
	pe->p->mmode = MOUSE_MODE_ADD_LEFT;
    } else if (!strcmp(cmd, "modr")) {
	pe->p->mmode = MOUSE_MODE_ADD_RIGHT;
    } else if (!strcmp(cmd, "modc")) {
	pe->p->mmode = MOUSE_MODE_ADD_CORNU;
    }
    return 1;
}

static void
create_mainwin(plate_edit *pe)
{
    x3widget *mainwin;
    x3widget *view;
    x3widget *menu;
    void *data = pe;
    x3viewflags viewflags = x3view_click | x3view_hover | x3view_key |
	x3view_2d | x3view_scroll;

    mainwin = x3window(x3window_main, "ppedit", ppedit_callback, data);

    menu = x3menu(mainwin, "File");

    x3menuitem(menu, "Save", "save", "<cmd>s");
    x3menuitem(menu, "Print", "prin", "<cmd>p");
    x3menuitem(menu, "Quit", "quit", "<cmd>q");

    menu = x3menu(mainwin, "Edit");

    pe->undo_me = x3menuitem(menu, "Undo", "undo", "<cmd>z");
    pe->redo_me = x3menuitem(menu, "Redo", "redo", "<cmd>y");

    //set_undo_state(p, NULL, NULL);
    x3menuitem(menu, "Toggle Corner", "togc", "<cmd>t");
    x3menuitem(menu, "Delete Point", "delp", "<cmd>d");
    x3menuitem(menu, "Selection Mode", "mods", "1");
    x3menuitem(menu, "Add Curve Mode", "modo", "2");
    x3menuitem(menu, "Add Corner Mode", "modv", "3");
    x3menuitem(menu, "Add Left Mode", "modl", "4");
    x3menuitem(menu, "Add Right Mode", "modr", "5");
    x3menuitem(menu, "Add G2 point Mode", "modc", "6");

    menu = x3menu(mainwin, "View");

    pe->show_knots_me = x3menuitem(menu, "Hide Knots", "khid", "<cmd>k");
    pe->show_bg_me = x3menuitem(menu, "Hide BG", "bghd", "<cmd>b");

    pe->view = x3view(mainwin, viewflags, ppedit_viewclient(pe));

#ifdef X3_GTK
    gtk_window_set_default_size(GTK_WINDOW(mainwin->widget), 512, 512);
#endif

    x3_window_show(mainwin);
}

int main(int argc, char **argv)
{
    plate_edit pe;
    plate *p = NULL;
    x3init(&argc, &argv);
    char *reason;

    if (argc > 1)
	p = file_read_plate(argv[1]);
    if (p == NULL)
	p = new_plate();
    pe.p = p;
    pe.undo_n = 0;
    pe.undo_i = 0;
    pe.undo_xn_state = 0;
    pe.show_knots = 1;
    pe.show_bg = 1;
    pe.bg_image = load_image_file("/tmp/foo.ppm", &reason);
    create_mainwin(&pe);
    x3main();
    return 0;
}
