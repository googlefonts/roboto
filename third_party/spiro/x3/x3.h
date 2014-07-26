/* X3 is a lightweight toolset for building cross-platform applications. */

typedef struct _x3widget x3widget;

typedef struct _x3viewclient x3viewclient;

typedef enum {
    x3window_main = 1,
    x3window_dialog = 2,
} x3windowflags;

typedef enum {
    x3center = 0,
    x3left = 1,
    x3right = 2,
    x3hfill = 3,
    x3top = 4,
    x3bottom = 8,
    x3vfill = 12,

    x3topleft = 5,
    x3topright = 6,
    x3bottomleft = 9,
    x3bottomright = 10,
} x3alignment;

typedef enum {
    x3view_click = 1,
    x3view_hover = 2,
    x3view_key = 4,
    x3view_2d = 0x100,
    x3view_rgb = 0x200,
    x3view_scroll = 0x10000
} x3viewflags;

typedef struct _x3dc x3dc;

struct _x3viewclient {
    void (*destroy)(x3viewclient *self);
    void (*mouse)(x3viewclient *self, int buttons, int mods,
		  double x, double y);
    int (*key)(x3viewclient *self, char *keyname, int mods, int key);
    void (*draw)(x3viewclient *self, x3dc *dc);
};

/* Windows and Carbon both use left/top/right/bottom nomenclature,
   at least for int rects, while gtk+ uses x/y/width/height. */
typedef struct {
    double x0;
    double y0;
    double x1;
    double y1;
} x3rect;

#ifdef X3_GTK

#include <gtk/gtk.h>

#define X3_GMW(g, m, w) g

struct _x3dc {
    /* move to x3rect structure? */
    int x;
    int y;
    int width;
    int height;

    cairo_t *cr;

    /* for rgb drawing */
    unsigned char *buf;
    int rowstride;
};

struct _x3widget {
    char *name;
    x3widget *parent;
    GtkWidget *widget;
};

typedef cairo_text_extents_t x3extents;

#define X3_SHIFT_MASK GDK_SHIFT_MASK
#define X3_CONTROL_MASK GDK_CONTROL_MASK
#define X3_ALT_MASK GDK_MOD1_MASK
/* there is no X3_CMD_MASK in gtk */

#define X3_USEMAIN

#endif

#ifdef X3_CARBON

#define X3_GMW(g, m, w) m

#include <Carbon/Carbon.h>

struct _x3dc {
    /* move to x3rect structure? */
    int x;
    int y;
    int width;
    int height;

    CGContextRef ctx;
    CGMutablePathRef path;

    /* for rgb drawing */
    char *buf;
    int rowstride;
};

typedef struct _x3type x3type;

struct _x3type {
    void (*sizereq)(x3widget *w);
    void (*sizealloc)(x3widget *w, x3rect *r);
    void (*add)(x3widget *w, x3widget *child);
};

typedef enum {
    x3carbonnone,
    x3carbonhiview,
    x3carbonwindow,
    x3carbonmenu,
    x3carbonmenuitem,
} x3carbonvar;

typedef enum {
    x3flag_needsizereq = 1,
    x3flag_needsizealloc = 2
} x3widgetflags;

struct _x3widget {
    const x3type *type;
    x3widgetflags flags;
    x3rect sizerequest;
    char *name;
    x3widget *parent;
    x3carbonvar var;
    union {
	HIViewRef hiview;
	WindowRef window;
	MenuRef menu;
	int menuitem;
    } u;
    int n_children;
    x3widget **children;
};

typedef struct {
    double x_bearing;
    double y_bearing;
    double width;
    double height;
    double x_advance;
    double y_advance;
} x3extents;

#define X3_SHIFT_MASK shiftKey
#define X3_CONTROL_MASK controlKey
#define X3_CMD_MASK cmdKey
#define X3_ALT_MASK optionKey

/* todo: figure out how to plumb mouse event */
#define X3_BUTTON1_MASK 0
#define X3_2BUTTON_PRESS 0
#define X3_3BUTTON_PRESS 0

#define X3_USEMAIN

#endif

#ifdef X3_WIN32

#include <windows.h>

#define X3_GMW(g, m, w) w

typedef struct _x3type x3type;

struct _x3type {
    void (*sizereq)(x3widget *w);
    void (*sizealloc)(x3widget *w, x3rect *r);
    void (*add)(x3widget *w, x3widget *child);
};

typedef enum {
    x3winnone,
    x3winhwnd,
} x3winvar;

typedef enum {
    x3flag_needsizereq = 1,
    x3flag_needsizealloc = 2
} x3widgetflags;

typedef struct {
    double x_bearing;
    double y_bearing;
    double width;
    double height;
    double x_advance;
    double y_advance;
} x3extents;

struct _x3widget {
    const x3type *type;
    char *name;
    x3widget *parent;
    x3widgetflags flags;
    x3rect sizerequest;
    x3winvar var; // should this be in the type?
    union {
	HWND hwnd;
    } u;
    int n_children;
    x3widget **children;
};

#define X3_USEWINMAIN

void x3init_win32(HINSTANCE hInstance);

#endif

typedef int (*x3window_callback)(x3widget *window, void *data,
				 char *cmd, char *what, char *arg,
				 void *more);

/* Main loop */
void x3init(int *pargc, char ***pargv);
void x3main(void);

x3widget *x3window(x3windowflags flags, char *label,
		   x3window_callback callback, void *callback_data);
x3widget *x3menu(x3widget *parent, char *name);
x3widget *x3menuitem(x3widget *parent, char *name, char *cmd, char *shortcut);
x3widget *x3menusep(x3widget *parent);
x3widget *x3align(x3widget *parent, x3alignment alignment);
x3widget *x3pad(x3widget *parent, int t, int b, int l, int r);
x3widget *x3vbox(x3widget *parent, int homogeneous, int spacing);
x3widget *x3hpane(x3widget *parent);
x3widget *x3vpane(x3widget *parent);
x3widget *x3button(x3widget *parent, char *name, char *label);
x3widget *x3label(x3widget *parent, char *label);
x3widget *x3edittext(x3widget *parent, char *cmd);
x3widget *x3view(x3widget *parent, x3viewflags flags, x3viewclient *vc);
void x3view_dirty(x3widget *w);
void x3view_scrollto(x3widget *w, int x, int y, int width, int height);

void x3viewclient_init(x3viewclient *vc);

void x3window_setdefaultsize(x3widget *w, int width, int height);

void x3pane_setsizing(x3widget *w, int child1_resize, int child1_shrink,
		      int child2_resize, int child2_shrink);

void x3setactive(x3widget *w, int active);
int x3hasfocus(x3widget *w);
void x3setpacking(x3widget *w, int fill, int expand, int padding);

extern int x3n_winopen;

/* 2d drawing functions */

void x3moveto(x3dc *dc, double x, double y);
void x3lineto(x3dc *dc, double x, double y);
void x3curveto(x3dc *dc,
	       double x1, double y1,
	       double x2, double y2,
	       double x3, double y3);
void x3closepath(x3dc *dc);
void x3rectangle(x3dc *dc, double x, double y, double width, double height);
void x3getcurrentpoint(x3dc *dc, double *px, double *py);
void x3setrgba(x3dc *dc, unsigned int rgba);
void x3setlinewidth(x3dc *dc, double w);
void x3fill(x3dc *dc);
void x3stroke(x3dc *dc);

/* This is an overly simple text api, based on cairo's. It may be phased
   out in favor of a more capable one. */
void x3selectfont(x3dc *dc, char *fontname, int slant, int weight);
void x3setfontsize(x3dc *dc, double size);
void x3showtext(x3dc *dc, char *text);
void x3textextents(x3dc *dc, char *text, x3extents *extents);

#if defined(X3_CARBON) || defined(X3_WIN32)
/* Internals for carbon/win32 */
void x3widget_init(x3widget *w, const x3type *type);
void x3add_default(x3widget *parent, x3widget *child);
void x3add(x3widget *parent, x3widget *child);
#endif
