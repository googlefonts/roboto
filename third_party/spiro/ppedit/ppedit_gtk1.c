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
#include <gdk/gdkkeysyms.h>
#include <gtk/gtk.h>
#include <libart_lgpl/libart.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

#include "zmisc.h"
#include "bezctx.h"
#include "bezctx_libart.h"
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
    GtkWidget *da;
    const char *description;
    plate *p;
    int undo_n;
    int undo_i;
    undo_record undo_buf[16];
    int undo_xn_state;

    GtkWidget *undo_me;
    GtkWidget *redo_me;

    GtkWidget *show_knots_me;
    GtkWidget *show_bg_me;
    int show_knots;
    int show_bg;

    image *bg_image;
} plate_edit;

int
quit_func(GtkWidget *widget, gpointer dummy)
{
    gtk_main_quit();
    return TRUE;
}

#define C1 0.55228
static void
draw_dot(art_u8 *buf, int x0, int y0, int x1, int y1, int rowstride,
	 double x, double y, double r, guint32 rgba)
{
    ArtBpath bp[6];
    ArtVpath *vp;
    ArtSVP *svp;

    bp[0].code = ART_MOVETO;
    bp[0].x3 = x + r;
    bp[0].y3 = y;
    bp[1].code = ART_CURVETO;
    bp[1].x1 = x + r;
    bp[1].y1 = y - C1 * r;
    bp[1].x2 = x + C1 * r;
    bp[1].y2 = y - r;
    bp[1].x3 = x;
    bp[1].y3 = y - r;
    bp[2].code = ART_CURVETO;
    bp[2].x1 = x - C1 * r;
    bp[2].y1 = y - r;
    bp[2].x2 = x - r;
    bp[2].y2 = y - C1 * r;
    bp[2].x3 = x - r;
    bp[2].y3 = y;
    bp[3].code = ART_CURVETO;
    bp[3].x1 = x - r;
    bp[3].y1 = y + C1 * r;
    bp[3].x2 = x - C1 * r;
    bp[3].y2 = y + r;
    bp[3].x3 = x;
    bp[3].y3 = y + r;
    bp[4].code = ART_CURVETO;
    bp[4].x1 = x + C1 * r;
    bp[4].y1 = y + r;
    bp[4].x2 = x + r;
    bp[4].y2 = y + C1 * r;
    bp[4].x3 = x + r;
    bp[4].y3 = y;
    bp[5].code = ART_END;

    vp = art_bez_path_to_vec(bp, 0.25);
    svp = art_svp_from_vpath(vp);
    art_free(vp);

    art_rgb_svp_alpha(svp, x0, y0, x1, y1, rgba, buf, rowstride, NULL);
    art_svp_free(svp);
}

static void
draw_raw_rect(art_u8 *buf, int x0, int y0, int x1, int y1, int rowstride,
	      double rx0, double ry0, double rx1, double ry1, guint32 rgba)
{
    ArtVpath vp[6];
    ArtSVP *svp;

    vp[0].code = ART_MOVETO;
    vp[0].x = rx0;
    vp[0].y = ry1;
    vp[1].code = ART_LINETO;
    vp[1].x = rx1;
    vp[1].y = ry1;
    vp[2].code = ART_LINETO;
    vp[2].x = rx1;
    vp[2].y = ry0;
    vp[3].code = ART_LINETO;
    vp[3].x = rx0;
    vp[3].y = ry0;
    vp[4].code = ART_LINETO;
    vp[4].x = rx0;
    vp[4].y = ry1;
    vp[5].code = ART_END;

    svp = art_svp_from_vpath(vp);

    art_rgb_svp_alpha(svp, x0, y0, x1, y1, rgba, buf, rowstride, NULL);
    art_svp_free(svp);
}

static void
draw_rect(art_u8 *buf, int x0, int y0, int x1, int y1, int rowstride,
	 double x, double y, double r, guint32 rgba)
{
    draw_raw_rect(buf, x0, y0, x1, y1, rowstride,
		  x - r, y - r, x + r, y + r, rgba);
}

static void
draw_half(art_u8 *buf, int x0, int y0, int x1, int y1, int rowstride,
	 double x, double y, double r, double th, guint32 rgba)
{
    ArtBpath bp[6];
    ArtVpath *vp;
    ArtSVP *svp;
    double c = cos(th);
    double s = sin(th);

    bp[0].code = ART_MOVETO;
    bp[0].x3 = x + c * r;
    bp[0].y3 = y + s * r;
    bp[1].code = ART_CURVETO;
    bp[1].x1 = x + c * r + C1 * s * r;
    bp[1].y1 = y + s * r - C1 * c * r;
    bp[1].x2 = x + s * r + C1 * c * r;
    bp[1].y2 = y - c * r + C1 * s * r;
    bp[1].x3 = x + s * r;
    bp[1].y3 = y - c * r;
    bp[2].code = ART_CURVETO;
    bp[2].x1 = x + s * r - C1 * c * r;
    bp[2].y1 = y - c * r - C1 * s * r;
    bp[2].x2 = x - c * r + C1 * s * r;
    bp[2].y2 = y - s * r - C1 * c * r;
    bp[2].x3 = x - c * r;
    bp[2].y3 = y - s * r;
    bp[3].code = ART_LINETO;
    bp[3].x3 = x + c * r;
    bp[3].y3 = y + s * r;
    bp[4].code = ART_END;

    vp = art_bez_path_to_vec(bp, 0.25);
    svp = art_svp_from_vpath(vp);
    art_free(vp);

    art_rgb_svp_alpha(svp, x0, y0, x1, y1, rgba, buf, rowstride, NULL);
    art_svp_free(svp);
}

static ArtVpath *
bezctx_to_vpath(bezctx *bc)
{
    ArtBpath *bp = bezctx_to_bpath(bc);
    ArtVpath *vp = art_bez_path_to_vec(bp, .25);

    g_free(bp);
    if (vp[0].code == ART_END || vp[1].code == ART_END) {
	g_free(vp);
	vp = NULL;
    }
    return vp;
}

static void
draw_plate(art_u8 *buf, int x0, int y0, int x1, int y1, int rowstride,
	   plate_edit *pe)
{
    plate *p = pe->p;
    int i, j;

    /* find an existing point to select, if any */
    for (i = 0; i < p->n_sp; i++) {
	bezctx *bc = new_bezctx_libart();
	subpath *sp = &p->sp[i];
	spiro_seg *s = draw_subpath(sp, bc);
	ArtVpath *vp = bezctx_to_vpath(bc);

	if (vp != NULL) {
	    ArtSVP *svp = art_svp_vpath_stroke(vp, ART_PATH_STROKE_JOIN_MITER,
					       ART_PATH_STROKE_CAP_BUTT,
					       1.5, 4.0, 0.25);

	    art_free(vp);
	    art_rgb_svp_alpha(svp, x0, y0, x1, y1, 0x000000ff, buf, rowstride,
			      NULL);
	    art_svp_free(svp);
	}

	for (j = 0; j < sp->n_kt; j++) {
	    if (pe->show_knots) {
		knot *kt = &sp->kt[j];
		kt_flags kf = kt->flags;
		if ((kf & KT_SELECTED) && (kf & KT_OPEN)) {
		    draw_dot(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			     3, 0x000000ff);
		    draw_dot(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			     1.5, 0xffffffff);
		} else if ((kf & KT_SELECTED) && (kf & KT_CORNER)) {
		    draw_rect(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			      3, 0x000000ff);
		    draw_rect(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			      1.5, 0xffffffff);
		} else if (!(kf & KT_SELECTED) && (kf & KT_CORNER)) {
		    draw_rect(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			      2.5, 0x000080ff);
		} else if ((kf & KT_SELECTED) && (kf & KT_CORNU)) {
		    draw_rect(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			      3, 0xc000c0ff);
		    draw_rect(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			      1.5, 0xffffffff);
		} else if (!(kf & KT_SELECTED) && (kf & KT_CORNU)) {
		    draw_rect(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			      2.5, 0x800080ff);
		} else if ((kf & KT_LEFT) || (kf & KT_RIGHT)) {
		    double th = 1.5708 + (s ? get_knot_th(s, j) : 0);
		    if (kf & KT_LEFT)
			th += 3.1415926;
		    if (kf & KT_SELECTED) {
			draw_half(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
				 4, th, 0x000000ff);
			draw_half(buf, x0, y0, x1, y1, rowstride,
				  kt->x + sin(th), kt->y - cos(th),
				  2, th, 0xffffffff);
		    } else {
			draw_half(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
				  3, th, 0x000080ff);
		    }
		} else {
		    draw_dot(buf, x0, y0, x1, y1, rowstride, kt->x, kt->y,
			     2, 0x000080ff);
		}
	    }
	}
	free_spiro(s);
    }
}

static void
draw_selection(art_u8 *buf, int x0, int y0, int x1, int y1, int rowstride,
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
	    draw_raw_rect(buf, x0, y0, x1, y1, rowstride,
			  rx0, ry0, rx1, ry1, 0x0000ff20);
    }
}

static void
render_bg_layer(guchar *buf, int rowstride, int x0, int y0, int x1, int y1,
		plate_edit *pe)
{
    const double affine[6] = { 1, 0, 0, 1, 0, 0 };

    if (pe->show_bg && pe->bg_image)
	render_image(pe->bg_image, affine,
		     buf, rowstride, x0, y0, x1, y1);
    else
	memset(buf, 255, (y1 - y0) * rowstride);
}

static gint
data_expose (GtkWidget *widget, GdkEventExpose *event, void *data)
{
    plate_edit *pe = (plate_edit *)data;
    int x0 = event->area.x;
    int y0 = event->area.y;
    int width = event->area.width;
    int height = event->area.height;
    guchar *rgb;
    int rowstride = (width * 3 + 3) & -4;

    rgb = g_new (guchar, event->area.height * rowstride);

    render_bg_layer(rgb, rowstride, x0, y0, x0 + width, y0 + height, pe);

    draw_plate(rgb, x0, y0, x0 + width, y0 + height, rowstride, pe);

    draw_selection(rgb, x0, y0, x0 + width, y0 + height, rowstride, pe);

    gdk_draw_rgb_image(widget->window,
		       widget->style->black_gc,
		       x0, y0, width, height,
		       GDK_RGB_DITHER_NONE, rgb,
		       rowstride);
    g_free(rgb);
    return FALSE;
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
set_undo_menuitem(GtkWidget *me, const char *name, const char *desc)
{
    char str[256];

    if (desc) {
	sprintf(str, "%s %s", name, desc);
    } else {
	strcpy(str, name);
    }
    gtk_container_foreach(GTK_CONTAINER(me),
			  (GtkCallback)gtk_label_set_text,
			  str);
    gtk_widget_set_sensitive(me, desc != NULL);
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

static gint
data_button_press (GtkWidget *widget, GdkEventButton *event, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;
    plate *p = pe->p;
    double x, y;
    press_mod mods = 0;

#define noVERBOSE
#ifdef VERBOSE
    g_print ("button press %f %f %f %d\n",
	     event->x, event->y, event->pressure, event->type);

#endif
    x = event->x;
    y = event->y;
    if (event->state & GDK_SHIFT_MASK) mods |= PRESS_MOD_SHIFT;
    if (event->state & GDK_CONTROL_MASK) mods |= PRESS_MOD_CTRL;
    if (event->type == GDK_2BUTTON_PRESS) mods |= PRESS_MOD_DOUBLE;
    if (event->type == GDK_3BUTTON_PRESS) mods |= PRESS_MOD_TRIPLE;

    begin_undo_xn(pe);
    p->description = NULL;
    plate_press(p, x, y, mods);
    if (p->description) dirty_undo_xn(pe, NULL);
    gtk_widget_queue_draw(widget);

    return TRUE;
}

static gint
data_motion_move (GtkWidget *widget, GdkEventMotion *event, plate_edit *pe)
{
    double x, y;
    x = event->x;
    y = event->y;

    plate_motion_move(pe->p, x, y);
    dirty_undo_xn(pe, NULL);
    
    gtk_widget_queue_draw(widget);

    return TRUE;
}

static gint
data_motion_select (GtkWidget *widget, GdkEventMotion *event, plate_edit *pe)
{
    double x, y;

    x = event->x;
    y = event->y;
    
    plate_motion_select(pe->p, x, y);
    gtk_widget_queue_draw(widget);

    return TRUE;
}

static gint
data_motion (GtkWidget *widget, GdkEventMotion *event, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

#ifdef VERBOSE
    g_print ("motion %f %f %f\n", event->x, event->y, event->pressure);

#endif
    if (pe->p->motmode == MOTION_MODE_MOVE)
	return data_motion_move(widget, event, pe);
    else if (pe->p->motmode == MOTION_MODE_SELECT)
	return data_motion_select(widget, event, pe);
    return TRUE;
}

static gint
data_button_release (GtkWidget *widget, GdkEventMotion *event, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;
    int need_redraw;
    
    need_redraw = (pe->p->motmode == MOTION_MODE_SELECT);

    plate_unpress(pe->p);
    
    gtk_widget_queue_draw(widget);

    return TRUE;
}

static gboolean
key_press(GtkWidget *widget, GdkEventKey *event, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;
    int delta = event->state & 4 ? 10 : 1;
    int old_n_iter = n_iter;
    double dx = 0, dy = 0;
    gboolean did_something = FALSE;

    g_print("key press %d %s %d\n", event->keyval, event->string, event->state);

    if (event->keyval == '<') {
	did_something = TRUE;
	n_iter -= delta;
    } else if (event->keyval == '>') {
	n_iter += delta;
    }
    if (n_iter < 0) n_iter = 0;
    if (n_iter != old_n_iter)
	g_print("n_iter = %d\n", n_iter);

    if (event->keyval == GDK_Left)
	dx = -1;
    else if (event->keyval == GDK_Right)
	dx = 1;
    else if (event->keyval == GDK_Up)
	dy = -1;
    else if (event->keyval == GDK_Down)
	dy = 1;
    if (event->state & GDK_SHIFT_MASK) {
	dx *= 10;
	dy *= 10;
    } else if (event->state & GDK_CONTROL_MASK) {
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
	gtk_signal_emit_stop_by_name(GTK_OBJECT(widget), "key-press-event");
	gtk_widget_queue_draw(widget);
    }

    return did_something;
}

static gint
toggle_corner_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    begindirty_undo_xn(pe, "Toggle Corner");
    plate_toggle_corner(pe->p);
    end_undo_xn(pe);
    gtk_widget_queue_draw(pe->da);

    return TRUE;
}

static gint
delete_pt_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    begindirty_undo_xn(pe, "Delete Point");
    plate_delete_pt(pe->p);
    end_undo_xn(pe);
    gtk_widget_queue_draw(pe->da);

    return TRUE;
}

static gint
set_select_mode_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->p->mmode = MOUSE_MODE_SELECT;
    return TRUE;
}

static gint
set_curve_mode_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->p->mmode = MOUSE_MODE_ADD_CURVE;
    pe->p->last_curve_mmode = pe->p->mmode;
    return TRUE;
}

static gint
set_corner_mode_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->p->mmode = MOUSE_MODE_ADD_CORNER;
    return TRUE;
}

static gint
set_left_mode_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->p->mmode = MOUSE_MODE_ADD_LEFT;
    return TRUE;
}

static gint
set_right_mode_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->p->mmode = MOUSE_MODE_ADD_RIGHT;
    return TRUE;
}

static gint
set_cornu_mode_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->p->mmode = MOUSE_MODE_ADD_CORNU;
    pe->p->last_curve_mmode = pe->p->mmode;
    return TRUE;
}

static gint
undo_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    undo(pe);
    gtk_widget_queue_draw(pe->da);

    return TRUE;
}

static gint
redo_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    redo(pe);
    gtk_widget_queue_draw(pe->da);

    return TRUE;
}

static gint
save_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    file_write_plate("plate", pe->p);

    return TRUE;
}

static gint
toggle_show_knots_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->show_knots = !pe->show_knots;
    gtk_container_foreach(GTK_CONTAINER(pe->show_knots_me),
			  (GtkCallback)gtk_label_set_text,
			  pe->show_knots ? "Hide Knots" : "Show Knots");
    gtk_widget_queue_draw(pe->da);
    return TRUE;
}

static gint
toggle_show_bg_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;

    pe->show_bg = !pe->show_bg;
    gtk_container_foreach(GTK_CONTAINER(pe->show_bg_me),
			  (GtkCallback)gtk_label_set_text,
			  pe->show_bg ? "Hide BG" : "Show BG");
    gtk_widget_queue_draw(pe->da);
    return TRUE;
}

static gint
print_func(GtkWidget *widget, gpointer data)
{
    plate_edit *pe = (plate_edit *)data;
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

static GtkWidget *
add_menuitem(GtkWidget *menu, const char *name, GtkSignalFunc callback,
	     gpointer callback_data, GtkAccelGroup *ag, const char *accel)
{
    GtkWidget *menuitem;

    menuitem = gtk_menu_item_new_with_label(name);
    gtk_menu_append(GTK_MENU(menu), menuitem);
    gtk_widget_show(menuitem);
    if (accel != NULL) {
	guint accel_key, accel_mods;

	gtk_accelerator_parse(accel, &accel_key, &accel_mods);
	gtk_widget_add_accelerator(menuitem, "activate", ag,
				   accel_key, accel_mods, GTK_ACCEL_VISIBLE);
    }
    gtk_signal_connect(GTK_OBJECT(menuitem), "activate",
		       (GtkSignalFunc)callback, callback_data);
    return (menuitem);
}

static void
create_mainwin(plate_edit *p)
{
    GtkWidget *mainwin;
    GtkWidget *eb;
    GtkWidget *da;
    GtkWidget *vbox;
    GtkWidget *menubar;
    GtkWidget *menu;
    GtkWidget *menuitem;
    GtkAccelGroup *ag;
    void *data = p;

    mainwin = gtk_widget_new(gtk_window_get_type(),
			  "GtkWindow::type", GTK_WINDOW_TOPLEVEL,
			  "GtkWindow::title", "pattern plate editor",
			  NULL);
    gtk_signal_connect(GTK_OBJECT(mainwin), "destroy",
		       (GtkSignalFunc)quit_func, NULL);

    vbox = gtk_vbox_new(FALSE, 0);
    gtk_container_add(GTK_CONTAINER(mainwin), vbox);

    menubar = gtk_menu_bar_new();
    ag = gtk_accel_group_new();
    gtk_window_add_accel_group(GTK_WINDOW(mainwin), ag);
    gtk_box_pack_start(GTK_BOX(vbox), menubar, FALSE, FALSE, 0);

    menu = gtk_menu_new();
    menuitem = gtk_menu_item_new_with_label("File");
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(menuitem), menu);
    gtk_menu_bar_append(GTK_MENU_BAR(menubar), menuitem);
    gtk_widget_show(menuitem);
    gtk_menu_set_accel_group(GTK_MENU(menu), ag);
    add_menuitem(menu, "Save", (GtkSignalFunc)save_func, data, ag, "<ctrl>S");
    add_menuitem(menu, "Quit", (GtkSignalFunc)quit_func, data, ag, "<ctrl>Q");
    add_menuitem(menu, "Print", (GtkSignalFunc)print_func, data, ag, "<ctrl>P");

    menu = gtk_menu_new();
    menuitem = gtk_menu_item_new_with_label("Edit");
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(menuitem), menu);
    gtk_menu_bar_append(GTK_MENU_BAR(menubar), menuitem);
    gtk_widget_show(menuitem);
    gtk_menu_set_accel_group(GTK_MENU(menu), ag);
    p->undo_me = add_menuitem(menu, "Undo", (GtkSignalFunc)undo_func, data, ag, "<ctrl>Z");
    p->redo_me = add_menuitem(menu, "Redo", (GtkSignalFunc)redo_func, data, ag, "<ctrl>Y");
    set_undo_state(p, NULL, NULL);
    add_menuitem(menu, "Toggle Corner", (GtkSignalFunc)toggle_corner_func, data, ag, "<ctrl>T");
    add_menuitem(menu, "Delete Point", (GtkSignalFunc)delete_pt_func, data, ag, "<ctrl>D");
    add_menuitem(menu, "Selection Mode", (GtkSignalFunc)set_select_mode_func, data, ag, "1");
    add_menuitem(menu, "Add Curve Mode", (GtkSignalFunc)set_curve_mode_func, data, ag, "2");
    add_menuitem(menu, "Add Corner Mode", (GtkSignalFunc)set_corner_mode_func, data, ag, "3");
    add_menuitem(menu, "Add Left Mode", (GtkSignalFunc)set_left_mode_func, data, ag, "4");
    add_menuitem(menu, "Add Right Mode", (GtkSignalFunc)set_right_mode_func, data, ag, "5");
    add_menuitem(menu, "Add Cornu Mode", (GtkSignalFunc)set_cornu_mode_func, data, ag, "6");


    menu = gtk_menu_new();
    menuitem = gtk_menu_item_new_with_label("View");
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(menuitem), menu);
    gtk_menu_bar_append(GTK_MENU_BAR(menubar), menuitem);
    gtk_widget_show(menuitem);
    gtk_menu_set_accel_group(GTK_MENU(menu), ag);
    p->show_knots_me = add_menuitem(menu, "Hide Knots",
				    (GtkSignalFunc)toggle_show_knots_func,
				    data, ag, "<ctrl>K");
    p->show_bg_me = add_menuitem(menu, "Hide BG",
				 (GtkSignalFunc)toggle_show_bg_func,
				 data, ag, "<ctrl>B");

    eb = gtk_event_box_new ();
    GTK_WIDGET_SET_FLAGS(eb, GTK_CAN_FOCUS);
    gtk_box_pack_start(GTK_BOX(vbox), eb, TRUE, TRUE, 0);
    gtk_widget_set_extension_events (eb, GDK_EXTENSION_EVENTS_ALL);
    gtk_signal_connect(GTK_OBJECT (eb), "button-press-event",
		       (GtkSignalFunc) data_button_press, data);
    gtk_signal_connect(GTK_OBJECT (eb), "motion-notify-event",
		       (GtkSignalFunc) data_motion, data);
    gtk_signal_connect(GTK_OBJECT (eb), "button-release-event",
		       (GtkSignalFunc) data_button_release, data);
    gtk_signal_connect(GTK_OBJECT(eb), "key-press-event",
		       (GtkSignalFunc)key_press, data);

    da = gtk_drawing_area_new();
    p->da = da;
    gtk_window_set_default_size(GTK_WINDOW(mainwin), 512, 512);
    gtk_container_add(GTK_CONTAINER(eb), da);
    gtk_signal_connect(GTK_OBJECT (da), "expose-event",
		       (GtkSignalFunc) data_expose, data);
#if 0
    gtk_widget_set_double_buffered(da, FALSE);
#endif

    gtk_widget_grab_focus(eb);
    gtk_widget_show(da);
    gtk_widget_show(eb);
    gtk_widget_show(menubar);
    gtk_widget_show(vbox);
    gtk_widget_show(mainwin);
}

int main(int argc, char **argv)
{
    plate_edit pe;
    plate *p = NULL;
    gtk_init(&argc, &argv);
    gtk_widget_set_default_colormap(gdk_rgb_get_cmap());
    gtk_widget_set_default_visual(gdk_rgb_get_visual());
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
    gtk_main();
    return 0;
}
