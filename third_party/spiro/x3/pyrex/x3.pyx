cdef extern from "Python.h":
    void *PyMem_Malloc(int size) except NULL
    void Py_INCREF(object)
    int PyUnicode_Check(object str)
    object PyUnicode_AsUTF8String(object str)

cdef extern from "x3.h":
    ctypedef struct x3widget
    ctypedef struct x3dc:
        int x
        int y
        int width
        int height
    cdef enum x3windowflags:
        x3window_main = 1
        x3window_dialog = 2
    ctypedef struct x3viewclient:
        void (*destroy)(x3viewclient *self)
        void (*mouse)(x3viewclient *self, int buttons, int mods,
                      double x, double y)
        int (*key)(x3viewclient *self, char *keyname, int mods, int key)
        void (*draw)(x3viewclient *self, x3dc *dc)

        # client extension
        void *py_client
    ctypedef struct x3extents:
        double x_bearing
        double y_bearing
        double width
        double height
        double x_advance
        double y_advance
    void x3init(int argc, char **argv)
    void x3main()
    x3widget *x3window(x3windowflags flags, char *name,
                       int (callback)(x3widget *w, void *data, char *cmd, char *what, char *arg, void *more),
                       void *data)
    x3widget *x3menu(x3widget *parent, char *name)
    x3widget *x3menuitem(x3widget *parent, char *name, char *cmd, char *shortcut)
    x3widget *x3menusep(x3widget *parent)
    x3widget *x3align(x3widget *parent, int alignment)
    x3widget *x3pad(x3widget *parent, int t, int b, int l, int r)
    x3widget *x3vbox(x3widget *parent, int homogeneous, int spacing)
    x3widget *x3hpane(x3widget *parent)
    x3widget *x3vpane(x3widget *parent)
    x3widget *x3button(x3widget *parent, char *name, char *label)
    x3widget *x3label(x3widget *parent, char *text)
    x3widget *x3edittext(x3widget *parent, char *cmd)
    x3widget *x3view(x3widget *parent, int flags, x3viewclient *vc)
    void x3viewclient_init(x3viewclient *vc)
    void x3view_dirty(x3widget *w)
    void x3view_scrollto(x3widget *w, int x, int y, int width, int height)

    void x3window_setdefaultsize(x3widget *w, int x, int y)
    void x3setactive(x3widget *w, int active)
    void x3setpacking(x3widget *w, int fill, int expand, int padding)
    void x3pane_setsizing(x3widget *w, int c1r, int c1s, int c2r, int c2s)
    int x3hasfocus(x3widget *w)

    void x3moveto(x3dc *dc, double x, double y)
    void x3lineto(x3dc *dc, double x, double y)
    void x3curveto(x3dc *dc,
                   double x1, double y1,
                   double x2, double y2,
                   double x3, double y3)
    void x3closepath(x3dc *dc)
    void x3rectangle(x3dc *dc, double x, double y, double width, double height)
    void x3getcurrentpoint(x3dc *dc, double *px, double *py)
    void x3setrgba(x3dc *dc, unsigned int rgba)
    void x3setlinewidth(x3dc *dc, double w)
    void x3fill(x3dc *dc)
    void x3stroke(x3dc *dc)
    void x3selectfont(x3dc *dc, char *fontname, int slant, int weight)
    void x3setfontsize(x3dc *dc, double size)
    void x3showtext(x3dc *dc, char *text)
    void x3textextents(x3dc *dc, char *text, x3extents *extents)
    X3_GMW(g, m, w)

cdef object strmaybenull(char *str):
    if str == NULL:
        return None
    else:
        return str

cdef object utf8(object ustr):
    if PyUnicode_Check(ustr):
        return PyUnicode_AsUTF8String(ustr)
    else:
        return ustr

ctypedef struct x3viewclient_py:
    x3viewclient base
    # client extension
    void *py_client

cdef class widget:
    cdef x3widget *w
    def hasfocus(self):
        return x3hasfocus(self.w)

cdef int x3py_callback(x3widget *window, void *data, char *cmd, char *what,
                       char *arg, void *more):
    callback = <object>data
    callback(cmd, strmaybenull(what), strmaybenull(arg), None)

cdef class window(widget):
    def __new__(self, int flags, char *name, callback):
        self.w = x3window(flags, name, x3py_callback, <void *>callback)
    def setdefaultsize(self, int width, int height):
        x3window_setdefaultsize(self.w, width, height)

cdef class menu(widget):
    def __new__(self, widget parent, name):
        uname = utf8(name)
        self.w = x3menu(parent.w, uname)

cdef class menuitem(widget):
    def __new__(self, widget parent, name, char *cmd, char *shortcut = NULL):
        uname = utf8(name)
        self.w = x3menuitem(parent.w, uname, cmd, shortcut)

cdef class menusep(widget):
    def __new__(self, widget parent):
        self.w = x3menusep(parent.w)

cdef class align(widget):
    def __new__(self, widget parent, int alignment):
        self.w = x3align(parent.w, alignment)

cdef class pad(widget):
    def __new__(self, widget parent, int t, int b, int l, int r):
        self.w = x3pad(parent.w, t, b, l, r)

cdef class vbox(widget):
    def __new__(self, widget parent, homogeneous, int spacing):
        self.w = x3vbox(parent.w, not not homogeneous, spacing)
    def setpacking(self, fill, expand, int padding):
        x3setpacking(self.w, not not fill, not not expand, padding)

cdef class hpane(widget):
    def __new__(self, widget parent):
        self.w = x3hpane(parent.w)
    def setsizing(self, c1r, c1s, c2r, c2s):
        x3pane_setsizing(self.w, not not c1r, not not c1s, not not c2r, not not c2s)

cdef class vpane(widget):
    def __new__(self, widget parent):
        self.w = x3vpane(parent.w)
    def setsizing(self, c1r, c1s, c2r, c2s):
        x3pane_setsizing(self.w, not not c1r, not not c1s, not not c2r, not not c2s)

cdef class button(widget):
    def __new__(self, widget parent, char *name, label):
        ulabel = utf8(label)
        self.w = x3button(parent.w, name, ulabel)

cdef class label(widget):
    def __new__(self, widget parent, text):
        ulabel = utf8(text)
        self.w = x3label(parent.w, ulabel)

cdef class edittext(widget):
    def __new__(self, widget parent, char *cmd):
        self.w = x3edittext(parent.w, cmd)

cdef int x3py_key(x3viewclient *self, char *keyname, int mods, int key):
    py_client = <object>(<x3viewclient_py *>self).py_client
    return py_client.key(keyname, mods, key)

cdef void x3py_mouse(x3viewclient *self, int button, int mods, double x, double y):
    py_client = <object>(<x3viewclient_py *>self).py_client
    py_client.mouse(button, mods, x, y)

cdef int dbl_to_byte(double x):
    if x <= 0: return 0
    if x >= 1: return 255
    return x * 255 + 0.5

cdef class x3dc_wrap:
    cdef x3dc *dc

    property rect:
        def __get__(self):
            return (self.dc.x, self.dc.y, self.dc.width, self.dc.height)

    def moveto(self, double x, double y):
        x3moveto(self.dc, x, y)
    def lineto(self, double x, double y):
        x3lineto(self.dc, x, y)
    def curveto(self, double x1, double y1, double x2, double y2, double x3, double y3):
        x3curveto(self.dc, x1, y1, x2, y2, x3, y3)
    def closepath(self):
        x3closepath(self.dc)
    def rectangle(self, double x, double y, double width, double height):
        x3rectangle(self.dc, x, y, width, height)
    def currentpoint(self):
        cdef double x
        cdef double y
        x3getcurrentpoint(self.dc, &x, &y)
        return (x, y)
    def setrgba(self, double r, double g, double b, double a):
        x3setrgba(self.dc, (dbl_to_byte(r) << 24) |
                  (dbl_to_byte(g) << 16) |
                  (dbl_to_byte(b) << 8) |
                  dbl_to_byte(a))
    def setlinewidth(self, double w):
        x3setlinewidth(self.dc, w)
    def fill(self):
        x3fill(self.dc)
    def stroke(self):
        x3stroke(self.dc)
    def selectfont(self, char *name, int slant, int weight):
        x3selectfont(self.dc, name, slant, weight)
    def setfontsize(self, double size):
        x3setfontsize(self.dc, size)
    def showtext(self, text):
        utext = utf8(text)
        x3showtext(self.dc, utext)
    def textextents(self, text):
        cdef x3extents ext
        utext = utf8(text)
        x3textextents(self.dc, utext, &ext)
        return (ext.x_bearing, ext.y_bearing,
                ext.width, ext.height,
                ext.x_advance, ext.y_advance)


cdef void x3py_draw(x3viewclient *self, x3dc *dc):
    cdef x3dc_wrap dc_wrap
    py_client = <object>(<x3viewclient_py *>self).py_client
    dc_wrap = x3dc_wrap()
    dc_wrap.dc = dc
    py_client.draw(dc_wrap)

cdef class view(widget):
    def __new__(self, widget parent, int flags, viewclient):
        cdef x3viewclient_py *vc
        vc = <x3viewclient_py *>PyMem_Malloc(sizeof(x3viewclient_py))
        x3viewclient_init(&vc.base)
        vc.py_client = <void *>viewclient
        Py_INCREF(viewclient)
        vc.base.key = x3py_key
        vc.base.mouse = x3py_mouse
        vc.base.draw = x3py_draw
        self.w = x3view(parent.w, flags, &vc.base)
        viewclient.view = self
    def dirty(self):
        x3view_dirty(self.w)
    def scrollto(self, int x, int y, int width, int height):
        x3view_scrollto(self.w, x, y, width, height)

def main():
    x3main()

def gmw(g, m, w):
    return X3_GMW(g, m, w)
platform = gmw("gtk", "mac", "win32")

x3init(0, NULL)
