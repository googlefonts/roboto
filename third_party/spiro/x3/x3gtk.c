#include <stdlib.h>
#include <string.h>

#include "x3.h"
#include "x3common.h"

void x3init(int *pargc, char ***pargv)
{
    gtk_init(pargc, pargv);
    x3initqs();
}

static void
x3_getfirst_callback(GtkWidget *widget, gpointer data)
{
    GtkWidget **pwidget = (GtkWidget **)data;

    if (*pwidget == NULL)
	*pwidget = widget;
}

static GtkWidget *x3_gtkwidget_getchild(GtkWidget *w)
{
    GtkWidget *child = NULL;
    gtk_container_foreach(GTK_CONTAINER(w),
			  x3_getfirst_callback,
			  (gpointer)&child);
    return child;
}

typedef struct {
    x3widget base;
    gboolean expand;
    gboolean fill;
    guint padding;
} x3widget_box;

static void x3widget_init(x3widget *w, x3widget *parent, char *name,
			  GtkWidget *widget)
{
    w->name = g_strdup(name);
    w->widget = widget;
    w->parent = parent;
    if (parent) {
	if (GTK_IS_WINDOW(parent->widget)) {
	    GtkWidget *vbox = x3_gtkwidget_getchild(parent->widget);

	    if (GTK_IS_MENU_ITEM(widget)) {
		GtkWidget *first_child = x3_gtkwidget_getchild(vbox);
		GtkWidget *menubar;

		if (first_child == NULL || !GTK_IS_MENU_BAR(first_child)) {
		    menubar = gtk_menu_bar_new();
		    gtk_box_pack_start(GTK_BOX(vbox), menubar,
				       FALSE, FALSE, 0);
		    gtk_widget_show(menubar);
		} else
		    menubar = first_child;
		gtk_menu_bar_append(GTK_MENU_BAR(menubar), widget);
	    } else {
		gtk_container_add(GTK_CONTAINER(vbox), widget);
	    }
	} else if (GTK_IS_MENU_ITEM(parent->widget)) {
	    GtkWidget *menu = gtk_menu_item_get_submenu(GTK_MENU_ITEM(parent->widget));

	    gtk_menu_shell_append(GTK_MENU_SHELL(menu), widget);
	} else if (GTK_IS_BOX(parent->widget)) {
	    x3widget_box *pwb = (x3widget_box *)parent;
	    gtk_box_pack_start(GTK_BOX(parent->widget), widget,
			       pwb->expand, pwb->fill, pwb->padding);
	} else {
	    gtk_container_add(GTK_CONTAINER(parent->widget), widget);
	}
    }
}

static x3widget *x3widget_new(x3widget *parent, char *name, GtkWidget *widget)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));

    x3widget_init(result, parent, name, widget);
    return result;
}

static x3widget *x3box_new(x3widget *parent, GtkWidget *widget)
{
    x3widget_box *result = (x3widget_box *)malloc(sizeof(x3widget_box));

    x3widget_init(&result->base, parent, NULL, widget);
    result->expand = TRUE;
    result->fill = TRUE;
    result->padding = 0;
    return &result->base;
}

void x3_window_show(x3widget *w)
{
    gtk_widget_show(w->widget);
}

void x3window_setdefaultsize(x3widget *w, int width, int height)
{
    gtk_window_set_default_size(GTK_WINDOW(w->widget), width, height);
}

void x3main(void)
{
    x3sync();
    gtk_main();
}

/* some constructors */

typedef struct {
    x3widget base;
    x3window_callback callback;
    void *callback_data;

    GtkAccelGroup *accel_group;
} x3widget_window;

gboolean x3window_delete(GtkWidget *window, GdkEvent *event, gpointer data)
{
    /* todo: pass this as a command callback */
    if (--x3n_winopen <= 0)
	gtk_main_quit();
    return FALSE;
}

x3widget *x3window(x3windowflags flags, char *label,
		   x3window_callback callback, void *callback_data)
{
    GtkWidget *window;
    GtkWidget *vbox;
    x3widget_window *result;

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), label);
    vbox = gtk_vbox_new(FALSE, 0);
    gtk_widget_show(vbox);
    gtk_container_add(GTK_CONTAINER(window), vbox);
    result = (x3widget_window *)malloc(sizeof(x3widget_window));
    x3widget_init(&result->base, NULL, "mainwin", window);
    result->callback = callback;
    result->callback_data = callback_data;
    result->accel_group = gtk_accel_group_new();
    gtk_window_add_accel_group(GTK_WINDOW(window), result->accel_group);
    g_signal_connect(G_OBJECT(window), "delete-event",
		     G_CALLBACK(x3window_delete), result);
    x3qshow(&result->base);
    x3n_winopen++;
    return &result->base;
}

x3widget *x3menu(x3widget *parent, char *name)
{
    GtkWidget *item;
    GtkWidget *menu;

    menu = gtk_menu_new();

    item = gtk_menu_item_new_with_label(name);
    gtk_widget_show(item);

    gtk_menu_item_set_submenu(GTK_MENU_ITEM(item), menu);
    return x3widget_new(parent, NULL, item);
}

typedef struct {
    x3widget base;
    char *cmd;
} x3widget_cmdable;

static void x3doevent(x3widget_cmdable *wc, char *str)
{
    char *cmd = wc->cmd;
    x3widget *w = &wc->base;
    x3widget_window *ww;

    while (w->parent) w = w->parent;
    ww = (x3widget_window *)w;
    ww->callback(w, ww->callback_data, cmd, str, NULL, NULL);
    x3sync();
}

static void x3cmdable_clicked(GtkWidget *widget, gpointer data)
{
    x3widget_cmdable *wc = (x3widget_cmdable *)data;

    x3doevent(wc, "command");
}

static const char *asciinames[] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    "space",
    "exclam",
    "quotedbl",
    "numbersign",
    "dollar",
    "percent",
    "ampersand",
    "apostrophe",
    "parenleft",
    "parenright",
    "asterisk",
    "plus",
    "comma",
    "minus",
    "period",
    "slash",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "colon",
    "semicolon",
    "less",
    "equal",
    "greater",
    "question",
    "at",
    "<shift>a",
    "<shift>b",
    "<shift>c",
    "<shift>d",
    "<shift>e",
    "<shift>f",
    "<shift>g",
    "<shift>h",
    "<shift>i",
    "<shift>j",
    "<shift>k",
    "<shift>l",
    "<shift>m",
    "<shift>n",
    "<shift>o",
    "<shift>p",
    "<shift>q",
    "<shift>r",
    "<shift>s",
    "<shift>t",
    "<shift>u",
    "<shift>v",
    "<shift>w",
    "<shift>x",
    "<shift>y",
    "<shift>z",
    "bracketleft",
    "backslash",
    "bracketright",
    "asciicircum",
    "underscore",
    "grave",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "braceleft",
    "bar",
    "braceright",
    "asciitilde"
};

/* return 1 on success */
static int
x3parseshortcut(const char *shortcut,
		guint *accelerator_key, GdkModifierType *accelerator_mods)
{
    int len;
    char tmp[256];
    int i;

    if (shortcut == NULL) return 0;
    len = strlen(shortcut);
    if (len >= sizeof(tmp) - 1) return 0;
    strcpy(tmp, shortcut);
    for (i = 0; i < len - 5; i++)
	if (!memcmp(tmp + i, "<cmd>", 5))
	    memcpy(tmp + i, "<ctl>", 5);
    if (len == 1 || tmp[len - 2] == '>') {
	unsigned char c = (unsigned char)tmp[len-1];
	if (c < sizeof(asciinames) / sizeof(asciinames[0]) && asciinames[c] &&
	    len + strlen(asciinames[c]) < sizeof(tmp))
	    strcpy(tmp + len - 1, asciinames[c]);
    }
    gtk_accelerator_parse(tmp, accelerator_key, accelerator_mods);
    return *accelerator_key != 0 || *accelerator_mods != 0;
}

static GtkAccelGroup *
x3getaccelgroup(x3widget *w)
{
    while (w->parent) w = w->parent;
    if (!GTK_IS_WINDOW(w->widget)) return NULL;
    return ((x3widget_window *)w)->accel_group;
}

x3widget *x3menuitem(x3widget *parent, char *name, char *cmd, char *shortcut)
{
    GtkWidget *item;
    x3widget_cmdable *result = (x3widget_cmdable *)malloc(sizeof(x3widget_cmdable));
    guint accel_key;
    GdkModifierType accel_mods;

    item = gtk_menu_item_new_with_label(name);
    x3widget_init(&result->base, parent, cmd, item);
    result->cmd = g_strdup(cmd);
    g_signal_connect(G_OBJECT(item), "activate",
		     G_CALLBACK(x3cmdable_clicked), result);

    if (x3parseshortcut(shortcut, &accel_key, &accel_mods)) {
	gtk_widget_add_accelerator(item, "activate", x3getaccelgroup(parent),
				   accel_key, accel_mods, GTK_ACCEL_VISIBLE);
    }

    gtk_widget_show(item);
    return &result->base;
}

x3widget *x3menusep(x3widget *parent)
{
    GtkWidget *item;

    item = gtk_separator_menu_item_new();
    gtk_widget_show(item);
    return x3widget_new(parent, NULL, item);
}

x3widget *x3vbox(x3widget *parent, int homogeneous, int spacing)
{
    GtkWidget *vbox = gtk_vbox_new(homogeneous, spacing);

    gtk_widget_show(vbox);
    return x3box_new(parent, vbox);
}

x3widget *x3hpane(x3widget *parent)
{
    GtkWidget *hpane = gtk_hpaned_new();

    gtk_widget_show(hpane);
    return x3widget_new(parent, NULL, hpane);
}

x3widget *x3vpane(x3widget *parent)
{
    GtkWidget *vpane = gtk_vpaned_new();

    gtk_widget_show(vpane);
    return x3widget_new(parent, NULL, vpane);
}

x3widget *x3align(x3widget *parent, x3alignment alignment)
{
    int xa = alignment & 3;
    int ya = (alignment >> 2) & 3;
    float xalign = .5 * (1 + (xa >> 1) - (xa & 1));
    float yalign = .5 * (1 + (ya >> 1) - (ya & 1));
    float xscale = (xa == 3);
    float yscale = (ya == 3);
    GtkWidget *align = gtk_alignment_new(xalign, yalign, xscale, yscale);

    gtk_widget_show(align);
    return x3widget_new(parent, NULL, align);
}

x3widget *x3pad(x3widget *parent, int t, int b, int l, int r)
{
    GtkWidget *align = gtk_alignment_new(0, 0, 1, 1);

    gtk_alignment_set_padding(GTK_ALIGNMENT(align), t, b, l, r);
    gtk_widget_show(align);
    return x3widget_new(parent, NULL, align);
}

x3widget *x3button(x3widget *parent, char *cmd, char *label)
{
    GtkWidget *button = gtk_button_new_with_label(label);
    x3widget_cmdable *result = (x3widget_cmdable *)malloc(sizeof(x3widget_cmdable));

    x3widget_init(&result->base, parent, cmd, button);
    result->cmd = g_strdup(cmd);
    g_signal_connect(G_OBJECT(button), "clicked",
		     G_CALLBACK(x3cmdable_clicked), result);

    gtk_widget_show(button);
    return &result->base;
}

x3widget *x3label(x3widget *parent, char *text)
{
    GtkWidget *label = gtk_label_new(text);

    gtk_widget_show(label);
    return x3widget_new(parent, NULL, label);
}

x3widget *x3edittext(x3widget *parent, char *cmd)
{
    GtkWidget *entry = gtk_entry_new();

    gtk_widget_show(entry);
    return x3widget_new(parent, cmd, entry);
}

typedef struct {
    x3widget base;
    x3viewflags flags;
    x3viewclient *vc;
} x3widget_view;

static gboolean x3view_expose(GtkWidget *widget, GdkEventExpose *event,
			      gpointer data)
{
    x3widget_view *w = (x3widget_view *)data;
    GdkWindow *window = GTK_IS_LAYOUT(widget) ?
	GTK_LAYOUT(widget)->bin_window :
	widget->window;

    if (w->vc && w->vc->draw) {
	x3dc dc;

	dc.x = event->area.x;
	dc.y = event->area.y;
	dc.width = event->area.width;
	dc.height = event->area.height;
	if (w->flags & x3view_rgb) {
	    dc.rowstride = (event->area.width * 3 + 3) & -4;
	    dc.buf = (guchar *)malloc(event->area.height * dc.rowstride);
	    dc.cr = NULL;

	    w->vc->draw(w->vc, &dc);
	    gdk_draw_rgb_image(window, widget->style->black_gc,
			       event->area.x, event->area.y,
			       event->area.width, event->area.height,
			       GDK_RGB_DITHER_NORMAL,
			       dc.buf, dc.rowstride);
	    free(dc.buf);
	} else if (w->flags & x3view_2d) {
	    dc.cr = gdk_cairo_create(window);
	    dc.buf = NULL;

	    w->vc->draw(w->vc, &dc);
	    cairo_destroy(dc.cr);
	}
    }

#if 1
    /* experimental code for managing cairo dynamics */
    if (event->count == 0)
	gdk_flush();
#endif

    return TRUE;
}

static gboolean x3view_button_press(GtkWidget *widget, GdkEventButton *event,
				    gpointer data)
{
    x3widget_view *w = (x3widget_view *)data;
    guint button = event->button;

    if (event->type == GDK_BUTTON_RELEASE) button = -button;

    if (w->vc && w->vc->mouse) {
	w->vc->mouse(w->vc, button, event->state, event->x, event->y);
	return TRUE;
    }
    x3sync();
    return FALSE;
}

static gboolean x3view_pointer_motion(GtkWidget *widget, GdkEventButton *event,
				    gpointer data)
{
    x3widget_view *w = (x3widget_view *)data;

    if (w->vc && w->vc->mouse) {
	w->vc->mouse(w->vc, 0, event->state,
		     event->x, event->y);
	return TRUE;
    }
    x3sync();
    return FALSE;
}

static gboolean x3view_key_press(GtkWidget *widget, GdkEventKey *event,
				 gpointer data)
{
    x3widget_view *w = (x3widget_view *)data;

    if (w->vc && w->vc->key)
	return w->vc->key(w->vc, gdk_keyval_name(event->keyval),
			  event->state, event->keyval);
    x3sync();
    return FALSE;
}

x3widget *x3view(x3widget *parent, x3viewflags flags, x3viewclient *vc)
{
    GtkWidget *container;
    GtkWidget *event_target;
    GtkWidget *drawing_area;
    x3widget_view *result = (x3widget_view *)malloc(sizeof(x3widget_view));
    GdkEventMask eventmask = 0;

    if (flags & x3view_scroll) {
	container = gtk_scrolled_window_new(NULL, NULL);
	drawing_area = gtk_layout_new(NULL, NULL);
	event_target = drawing_area;
	/* todo: more intelligent size requesting of view */
	gtk_widget_set_size_request(drawing_area, 1500, 1500);
	gtk_scrolled_window_add_with_viewport(GTK_SCROLLED_WINDOW(container),
					      drawing_area);
    } else {
	container = gtk_event_box_new();
	drawing_area = gtk_drawing_area_new();
	event_target = container;
	gtk_container_add(GTK_CONTAINER(container), drawing_area);
    }
    gtk_widget_show(container);

    if (flags & x3view_key) {
	g_object_set(GTK_OBJECT(event_target), "can-focus", TRUE, NULL);
	eventmask |= GDK_KEY_PRESS_MASK;
	g_signal_connect(G_OBJECT(event_target), "key_press_event",
			 G_CALLBACK(x3view_key_press), result);
    }
    if (flags & x3view_click) {
	eventmask |= GDK_BUTTON_PRESS_MASK | GDK_BUTTON_RELEASE_MASK;
	g_signal_connect(G_OBJECT(event_target), "button_press_event",
			 G_CALLBACK(x3view_button_press), result);
	g_signal_connect(G_OBJECT(event_target), "button_release_event",
			 G_CALLBACK(x3view_button_press), result);
    }
    if (flags & x3view_hover) {
	eventmask |= GDK_POINTER_MOTION_MASK;
	g_signal_connect(G_OBJECT(event_target), "motion_notify_event",
			 G_CALLBACK(x3view_pointer_motion), result);
    }
    gtk_widget_add_events(event_target, eventmask);

    g_signal_connect(G_OBJECT(drawing_area), "expose_event",
		     G_CALLBACK(x3view_expose), result);
    gtk_widget_show(drawing_area);
    if (flags & x3view_rgb)
	gtk_widget_set_double_buffered(drawing_area, FALSE);

    x3widget_init(&result->base, parent, NULL, container);
    result->flags = flags;
    result->vc = vc;
    return &result->base;
}

void x3view_dirty(x3widget *w)
{
    gtk_widget_queue_draw(w->widget);
}

static void
x3scrollto_adj(GtkAdjustment *adj, int v, int size)
{
    if (adj && v != -1) {
	if (size >= adj->page_size) {
	    /* target is bigger than adj; center as best as possible */
	    gtk_adjustment_set_value(adj, v - 0.5 * (size - adj->page_size));
	} else if (adj->value > v) {
	    gtk_adjustment_set_value(adj, v);
	} else if (adj->value + adj->page_size < v + size) {
	    gtk_adjustment_set_value(adj, v + size - adj->page_size);
	}
    }
}

void x3view_scrollto(x3widget *w, int x, int y, int width, int height)
{
    if (GTK_IS_SCROLLED_WINDOW(w->widget)) {
	GtkScrolledWindow *sw = GTK_SCROLLED_WINDOW(w->widget);
	x3scrollto_adj(gtk_scrolled_window_get_hadjustment(sw), x, width);
	x3scrollto_adj(gtk_scrolled_window_get_vadjustment(sw), y, height);
    }
}

void x3viewclient_init(x3viewclient *vc)
{
    vc->destroy = NULL;
    vc->mouse = NULL;
    vc->key = NULL;
    vc->draw = NULL;
}

/* An argument can be made against the "fill" flag, because the same effect
   as turning off fill can be achieved with the align widget. */
void x3setpacking(x3widget *w, int fill, int expand, int padding)
{
    if (GTK_IS_BOX(w->widget)) {
	x3widget_box *wb= (x3widget_box *)w;
	wb->fill = fill;
	wb->expand = expand;
	wb->padding = padding;
    }
}

typedef struct {
    GtkWidget *parent;
    int resize[2];
    int shrink[2];
    int i;
} x3pane_setsizing_ctx;

static void
x3pane_setsizing_callback(GtkWidget *child, gpointer data)
{
    x3pane_setsizing_ctx *ctx = (x3pane_setsizing_ctx *)data;
    gtk_container_child_set(GTK_CONTAINER(ctx->parent),
			    child,
			    "resize", ctx->resize[ctx->i],
			    "shrink", ctx->shrink[ctx->i],
			    NULL);
    ctx->i++;
}

/* This implementation only works if the sizing is set _after_ the
 * children are added. It wouldn't be too hard to fix, by putting the
 * info in the pane's x3widget struct. */
void x3pane_setsizing(x3widget *w, int child1_resize, int child1_shrink,
		      int child2_resize, int child2_shrink)
{
    x3pane_setsizing_ctx ctx;

    ctx.parent = w->widget;
    ctx.resize[0] = child1_resize;
    ctx.shrink[0] = child1_shrink;
    ctx.resize[1] = child2_resize;
    ctx.shrink[1] = child2_shrink;
    ctx.i = 0;
    if (GTK_IS_PANED(w->widget)) {
	gtk_container_foreach(GTK_CONTAINER(w->widget),
			      x3pane_setsizing_callback,
			      (gpointer)&ctx);
    }
}


void x3setactive(x3widget *w, int active)
{
    gtk_widget_set_sensitive(w->widget, active != 0);
}

int x3hasfocus(x3widget *w)
{
    GtkWidget *widget = w->widget;
    while (GTK_IS_CONTAINER(widget) && !GTK_IS_LAYOUT(widget))
	widget = x3_gtkwidget_getchild(widget);
    return GTK_WIDGET_HAS_FOCUS(widget);
}

/* 2d drawing functions, implemented using cairo */

void
x3moveto(x3dc *dc, double x, double y)
{
    cairo_move_to(dc->cr, x, y);
}

void 
x3lineto(x3dc *dc, double x, double y)
{
    cairo_line_to(dc->cr, x, y);
}

void 
x3curveto(x3dc *dc,
	  double x1, double y1,
	  double x2, double y2,
	  double x3, double y3)
{
    cairo_curve_to(dc->cr, x1, y1, x2, y2, x3, y3);
}

void 
x3closepath(x3dc *dc)
{
    cairo_close_path(dc->cr);
}

void 
x3rectangle(x3dc *dc, double x, double y, double width, double height)
{
    cairo_rectangle(dc->cr, x, y, width, height);
}

void
x3getcurrentpoint(x3dc *dc, double *px, double *py)
{
    cairo_get_current_point(dc->cr, px, py);
}

void
x3setrgba(x3dc *dc, unsigned int rgba)
{
    cairo_set_source_rgba(dc->cr,
			  ((rgba >> 24) & 0xff) * (1.0/255),
			  ((rgba >> 16) & 0xff) * (1.0/255),
			  ((rgba >> 8) & 0xff) * (1.0/255),
			  (rgba & 0xff) * (1.0/255));
}

void
x3setlinewidth(x3dc *dc, double w)
{
    cairo_set_line_width(dc->cr, w);
}

void
x3fill(x3dc *dc)
{
    cairo_fill(dc->cr);
}

void
x3stroke(x3dc *dc)
{
    cairo_stroke(dc->cr);
}

void
x3selectfont(x3dc *dc, char *fontname, int slant, int weight)
{
    cairo_select_font_face(dc->cr, fontname, slant, weight);
}

void
x3setfontsize(x3dc *dc, double size)
{
    cairo_set_font_size(dc->cr, size);
}

void
x3showtext(x3dc *dc, char *text)
{
    cairo_show_text(dc->cr, text);
}

void
x3textextents(x3dc *dc, char *text, x3extents *extents)
{
    cairo_text_extents(dc->cr, text, extents);
}
