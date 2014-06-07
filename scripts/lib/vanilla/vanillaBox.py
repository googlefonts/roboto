from AppKit import *
from vanillaBase import VanillaBaseObject, _breakCycles


class Box(VanillaBaseObject):

    """
    A bordered container for other controls.

    To add a control to a box, simply set it as an attribute of the box.::

        from vanilla import *

        class BoxDemo(object):

            def __init__(self):
                self.w = Window((150, 70))
                self.w.box = Box((10, 10, -10, -10))
                self.w.box.text = TextBox((10, 10, -10, -10), "This is a box")
                self.w.open()

        BoxDemo()

    No special naming is required for the attributes. However, each attribute must have a unique name.

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the box.

    **title** The title to be displayed dabove the box. Pass *None* if no title is desired.
    """

    allFrameAdjustments = {
        # Box does not have sizeStyle, but the
        # adjustment is differeent based on the
        # presence of a title.
        "Box-Titled": (-3, -4, 6, 4),
        "Box-None": (-3, -4, 6, 6)
    }

    nsBoxClass = NSBox

    def __init__(self, posSize, title=None):
        self._setupView(self.nsBoxClass, posSize)
        if title:
            self._nsObject.setTitle_(title)
            self._nsObject.titleCell().setTextColor_(NSColor.blackColor())
            font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(NSSmallControlSize))
            self._nsObject.setTitleFont_(font)
        else:
            self._nsObject.setTitlePosition_(NSNoTitle)

    def getNSBox(self):
        """
        Return the *NSBox* that this object wraps.
        """
        return self._nsObject

    def _adjustPosSize(self, frame):
        # skip subclasses
        if self.__class__.__name__ == "Box":
            pos = self._nsObject.titlePosition()
            if pos != NSNoTitle:
                title = "Titled"
            else:
                title = "None"
            boxType = "Box-" + title
            self.frameAdjustments = self.allFrameAdjustments[boxType]
        return super(Box, self)._adjustPosSize(frame)

    def _getContentView(self):
        return self._nsObject.contentView()

    def _breakCycles(self):
        super(Box, self)._breakCycles()
        view = self._getContentView()
        if view is not None:
            _breakCycles(view)

    def setTitle(self, title):
        """
        Set the title of the box.
        """
        self._nsObject.setTitle_(title)

    def getTitle(self):
        """
        Get the title of the box.
        """
        return self._nsObject.title()


class _Line(Box):

    nsBoxClass = NSBox

    def __init__(self, posSize):
        self._setupView(self.nsBoxClass, posSize)
        self._nsObject.setBorderType_(NSLineBorder)
        self._nsObject.setBoxType_(NSBoxSeparator)
        self._nsObject.setTitlePosition_(NSNoTitle)


class HorizontalLine(_Line):
    
    """
    A horizontal line.::

        from vanilla import *

        class HorizontalLineDemo(object):

            def __init__(self):
                self.w = Window((100, 20))
                self.w.line = HorizontalLine((10, 10, -10, 1))
                self.w.open()

        HorizontalLineDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the line.

    +-------------------------+
    | **Standard Dimensions** |
    +---+---------------------+
    | H | 1                   |
    +---+---------------------+
    """

    def __init__(self, posSize):
        super(HorizontalLine, self).__init__(posSize)


class VerticalLine(_Line):

    """
    A vertical line.::

        from vanilla import *

        class VerticalLineDemo(object):

            def __init__(self):
                self.w = Window((80, 100))
                self.w.line = VerticalLine((40, 10, 1, -10))
                self.w.open()

        VerticalLineDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the line.

    +-------------------------+
    | **Standard Dimensions** |
    +---+---------------------+
    | V | 1                   |
    +---+---------------------+
    """

    def __init__(self, posSize):
        super(VerticalLine, self).__init__(posSize)
