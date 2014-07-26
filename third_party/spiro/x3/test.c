/* A test app for X3. */

#include "x3.h"
#include <stdlib.h>

int
mycallback(x3widget *w, void *data,
	   char *cmd, char *what, char *arg, void *more)
{
    printf("my callback: cmd=\"%s\", what=\"%s\", arg=\"%s\"\n",
	   cmd, what ? what : "(null)", arg ? arg : "(null)");
    return 1;
}

#if defined(X3_GTK) || defined(X3_CARBON)
static void test_viewclient_draw(x3viewclient *self, x3dc *dc)
{
    if (dc->buf) {
	int i, j;

	for (i = 0; i < dc->height; i++) {
	    for (j = 0; j < dc->width; j++) {
		dc->buf[i * dc->rowstride + j * 3] = i;
		dc->buf[i * dc->rowstride + j * 3 + 1] = 0x80;
		dc->buf[i * dc->rowstride + j * 3 + 2] = j;
	    }
	}
    } else {
	x3extents ext;

	x3moveto(dc, 10, 10);
	x3curveto(dc, 200, 10, 100, 100, 490, 100);
	x3stroke(dc);
	x3selectfont(dc, "Nimbus Roman No9 L", 0, 0);
	x3moveto(dc, 10, 50);
	x3setfontsize(dc, 16);
	x3showtext(dc, "hello, world!");
	x3textextents(dc, "hello, world!", &ext);
	printf("text extents: %g %g %g %g %g %g\n",
	       ext.x_bearing, ext.y_bearing,
	       ext.width, ext.height,
	       ext.x_advance, ext.y_advance);
    }
}

static int test_viewclient_key(x3viewclient *self,
				char *keyname, int mods, int key)
{
    printf("view key: %s %d %d\n", keyname, mods, key);
    return 1;
}

static void test_viewclient_mouse(x3viewclient *self,
				  int button, int mods,
				  double x, double y)
{
    printf("view button: %d %d %g %g\n", button, mods, x, y);
}

x3viewclient *test_viewclient(void)
{
    x3viewclient *result = (x3viewclient *)malloc(sizeof(x3viewclient));
    x3viewclient_init(result);
    result->draw = test_viewclient_draw;
    result->key = test_viewclient_key;
    result->mouse = test_viewclient_mouse;

    return result;
}

#ifdef X3_USEMAIN
int
main(int argc, char **argv)
{
    x3widget *mainwin;
    x3widget *pane;
    x3widget *vbox;
    x3widget *m;
    x3viewflags viewflags = x3view_click | x3view_hover | x3view_key;

    x3init(&argc, &argv);
    mainwin = x3window(x3window_main, "untitled", mycallback, NULL);
#if 1
    m = x3menu(mainwin, "F\xc2\xa1le");
    x3menuitem(m, "Save", "save", "<cmd>s");
    x3setactive(x3menuitem(m, "Save As...", "sava", "<cmd>S"), 0);
    x3menusep(m);
    x3menuitem(m, "Preferences...", "pref", "<cmd>,");

    m = x3menu(mainwin, "Edit");

    x3menuitem(m, "ctrl-delete", "cdel", "<ctl>Delete");
    x3menuitem(m, "ctrl-f1", "cf1", "<ctl>F1");
    if (0) {
	int i, j;

	for (j = 0; j < 3; j++) {
	    char mname[16];
	    mname[0] = '0' + j;
	    mname[1] = 0;
	    m = x3menu(mainwin, mname);
	    for (i = 0x20 + 0x20 * j; i < 0x40 + 0x20 * j; i++) {
		char name[16];

		name[0] = i;
		name[1] = 0;
		x3menuitem(m, name, name, name);
	    }
	}
    }
#endif

#if 1
    pane = x3vpane(mainwin);
    vbox = x3vbox(x3pad(pane, 10, 10, 10, 10), 0, 5);

    x3setpacking(vbox, FALSE, FALSE, 0);
    x3button(x3align(vbox, x3center), "foo", "Click me!");
    x3button(vbox, "bar", "Click me too!");
    x3setactive(x3button(vbox, "bar", "But not me"), 0);
    x3label(vbox, "I am a label.");
    x3edittext(vbox, "etxt");
#endif

    x3setpacking(vbox, TRUE, TRUE, 0);
    viewflags |= x3view_2d;
    viewflags |= x3view_scroll;
    x3view(pane, viewflags, test_viewclient());

#if 0
    x3_window_show(mainwin);
#endif

    x3main();
    return 0;
}
#endif
#endif

#ifdef X3_USEWINMAIN
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PSTR szCmdLine,
		   int iCmdShow)
{
    //printf("winmain\n");
    x3widget *mainwin;
    x3widget *vbox;

    x3init_win32(hInstance);

    mainwin = x3window(x3window_main, "untitled", mycallback, NULL);
    x3_window_show(mainwin);
    vbox = x3vbox(mainwin, 0, 5);
    x3button(vbox, "foo", "Click me!");
    x3button(vbox, "bar", "And me too!");
    x3main();
    return 0;
}
#endif
