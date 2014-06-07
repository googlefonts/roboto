from AppKit import NSView, NSColor, NSBezierPath
from vanilla import VanillaBaseObject, Window, Button


class SimpleRectView(NSView):

    def isOpaque(self):
        return False

    def drawRect_(self, rect):
        NSColor.colorWithCalibratedWhite_alpha_(0.5, 0.5).set()
        p = NSBezierPath.bezierPathWithRect_(self.bounds())
        p.fill()


class SimpleRect(VanillaBaseObject):

    def __init__(self, posSize):
        self._nsObject = SimpleRectView.alloc().init()
        self._posSize = posSize
        self._setAutosizingFromPosSize(posSize)


class TestGeometry(object):

    def __init__(self):
        self.window = w = Window((400, 400), "Test Geometry", minSize=(100, 100))
        w.button = Button((10, 10, 120, 20), "call SetPosSize", callback=self.setFrameCallback)
        w.x = SimpleRect((10, 40, -120, -120))
        w.x.top = SimpleRect((20, 20, -20, 40))
        w.x.left = SimpleRect((40, 40, 40, -40))
        w.x.right = SimpleRect((-80, 40, 40, -40))
        w.x.lefttop = SimpleRect((10, 10, 50, 20))
        w.x.righttop = SimpleRect((-60, 10, 50, 20))
        w.x.bottom = SimpleRect((20, -60, -20, 40))
        w.x.leftbottom = SimpleRect((10, -30, 50, 20))
        w.x.rightbottom = SimpleRect((-60, -30, 50, 20))
        w.x.middle = SimpleRect((70, 70, -70, -70))
        w.x.middle.deep = SimpleRect((20, 10, -20, -10))
        w.extra = SimpleRect((-110, 10, -10, -120))
        w.y = SimpleRect((10, -110, -10, -20))
        w.y.z = SimpleRect((10, 10, -10, -10))
        w.y.z.q = SimpleRect((10, 10, -10, -10))
        w.open()

    def setFrameCallback(self, sender):
        l, t, r, b = self.window.x.getPosSize()
        l += 10
        t += 10
        r -= 10
        b -= 10
        self.window.x.setPosSize((l, t, r, b))
