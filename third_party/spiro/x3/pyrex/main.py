import x3

def my_callback(cmd, what, arg, more):
    print cmd, what, arg

class my_viewclient:
    def key(self, name, mods, code):
        print name, mods, code
        return 1
    def mouse(self, buttons, mods, x, y):
        print buttons, mods, x, y
    def draw(self, dc):
        print 'rect:', dc.rect
        dc.moveto(0, 0)
        dc.lineto(100, 100)
        print dc.currentpoint()
        dc.stroke()
        dc.selectfont("Nimbus Sans L", 0, 0)
        dc.setfontsize(12)
        dc.moveto(50, 10)
        dc.showtext(u"\u00a1hello, world!")
        print dc.textextents(u"\u00a1hello, world!")

win = x3.window(0, "foo", my_callback)

m = x3.menu(win, "bar")

x3.menuitem(m, "baz", "bazz", "<ctrl>b")
x3.menusep(m)
x3.menuitem(m, "Quit", "quit", "<ctrl>q")

v = x3.vbox(win, 0, 12)

v.setpacking(True, False, 0)
x3.button(v, "butt", u"\u00a1hello!")
x3.edittext(v, "quux")
v.setpacking(True, True, 0)
x3.view(v, 263, my_viewclient())

x3.main()
