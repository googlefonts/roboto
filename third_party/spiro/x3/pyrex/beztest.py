import x3
from math import *

def my_callback(cmd, what, arg, more):
    print cmd, what, arg

class bez:
    def __init__(self):
        self.coords = [(10, 10), (200, 10), (300, 200), (400, 100)]
        self.hit = None
    def draw(self, dc):
        coords = self.coords
        dc.setrgba(0, 0, 0.5, 1)
        dc.moveto(coords[0][0], coords[0][1])
        dc.curveto(coords[1][0], coords[1][1], coords[2][0], coords[2][1],
                   coords[3][0], coords[3][1])
        dc.stroke()
        dc.setrgba(0, 0.5, 0, 0.5)
        dc.moveto(coords[0][0], coords[0][1])
        dc.lineto(coords[1][0], coords[1][1])
        dc.stroke()
        dc.moveto(coords[2][0], coords[2][1])
        dc.lineto(coords[3][0], coords[3][1])
        dc.stroke()
        dc.setrgba(1, 0, 0, .5)
        for x, y in coords:
            dc.rectangle(x - 3, y - 3, 6, 6)
            dc.fill()
    def mouse(self, button, mods, x, y):
        if button == 1:
            for i in range(4):
                if hypot(x - self.coords[i][0], y - self.coords[i][1]) < 4:
                    self.hit = i
        elif button == -1:
            self.hit = None
        elif self.hit != None:
            self.coords[self.hit] = (x, y)
            self.view.dirty()

win = x3.window(0, "beztest", my_callback)

x3.view(win, 259, bez())

x3.main()
