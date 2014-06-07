from Foundation import NSMaxXEdge, NSMaxYEdge, NSMinXEdge, NSMinYEdge
from AppKit import *
from vanillaBase import VanillaBaseObject, _breakCycles


_drawerEdgeMap = {
    "left": NSMinXEdge,
    "right": NSMaxXEdge,
    "top": NSMaxYEdge,
    "bottom": NSMinYEdge,
}


class Drawer(VanillaBaseObject):

    """
    A drawer attached to a window. Drawers are capable of containing controls.

    To add a control to a drawer, simply set it as an attribute of the drawer.::

        from vanilla import *

        class DrawerDemo(object):

            def __init__(self):
                self.w = Window((200, 200))
                self.w.button = Button((10, 10, -10, 20), "Toggle Drawer",
                                    callback=self.toggleDrawer)
                self.d = Drawer((100, 150), self.w)
                self.d.textBox = TextBox((10, 10, -10, -10),
                                    "This is a drawer.")
                self.w.open()
                self.d.open()

            def toggleDrawer(self, sender):
                self.d.toggle()

        DrawerDemo()

    No special naming is required for the attributes. However, each attribute must have a unique name.

    **size** Tuple of form *(width, height)* representing the size of the drawer.

    **parentWindow** The window that the drawer should be attached to.

    **minSize** Tuple of form *(width, height)* representing the minimum size of the drawer.

    **maxSize** Tuple of form *(width, height)* representing the maximum size of the drawer.

    **preferredEdge** The preferred edge of the window that the drawe should be attached to. If the
    drawer cannot be opened on the preferred edge, it will be opened on the opposite edge. The options are:

    +----------+
    | "left"   |
    +----------+
    | "right"  |
    +----------+
    | "top"    |
    +----------+
    | "bottom" |
    +----------+

    **forceEdge** Boolean representing if the drawer should *always* be opened on the preferred edge.

    **leadingOffset** Distance between the top or left edge of the drawer and the parent window.

    **trailingOffset** Distance between the bottom or right edge of the drawer and the parent window.
    """

    nsDrawerClass = NSDrawer

    def __init__(self, size, parentWindow, minSize=None, maxSize=None,
            preferredEdge="left", forceEdge=False, leadingOffset=20, trailingOffset=20):
        from vanillaWindows import Window
        self._preferredEdge = preferredEdge
        self._forceEdge = forceEdge
        drawer = self._nsObject = self.nsDrawerClass.alloc().initWithContentSize_preferredEdge_(
                size, _drawerEdgeMap[preferredEdge])
        drawer.setLeadingOffset_(leadingOffset)
        drawer.setTrailingOffset_(trailingOffset)
        if minSize:
            drawer.setMinContentSize_(minSize)
        if maxSize:
            drawer.setMaxContentSize_(maxSize)
        if isinstance(parentWindow, Window):
            parentWindow = parentWindow._window
        drawer.setParentWindow_(parentWindow)

    def getNSDrawer(self):
        """
        Return the *NSDrawer* that this object wraps.
        """
        return self._nsObject

    def _getContentView(self):
        return self._nsObject.contentView()

    def _breakCycles(self):
        super(Drawer, self)._breakCycles()
        view = self._getContentView()
        if view is not None:
            _breakCycles(view)

    def open(self):
        """
        Open the drawer.
        """
        if self._forceEdge:
            self._nsObject.openOnEdge_(_drawerEdgeMap[self._preferredEdge])
        else:
            self._nsObject.open()

    def close(self):
        """
        Close the drawer.
        """
        self._nsObject.close()

    def toggle(self):
        """
        Open the drawer if it is closed. Close it if it is open.
        """
        self._nsObject.toggle_(self)

    def isOpen(self):
        """
        Return True if the drawer is open, False if it is closed.
        """
        return self._nsObject.isOpen()
