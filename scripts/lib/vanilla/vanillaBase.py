from AppKit import *
from nsSubclasses import getNSSubclass


class VanillaError(Exception): pass


class VanillaBaseObject(object):

    frameAdjustments = None

    def __setattr__(self, attr, value):
        _setAttr(VanillaBaseObject, self, attr, value)

    def __delattr__(self, attr):
        _delAttr(VanillaBaseObject, self, attr)

    def _setupView(self, classOrName, posSize, callback=None):
        self._testForDeprecatedAttributes()
        cls = getNSSubclass(classOrName)
        self._nsObject = cls(self)
        self._posSize = posSize
        self._setCallback(callback)
        self._setAutosizingFromPosSize(posSize)

    def _breakCycles(self):
        if hasattr(self, "_target"):
            self._target.callback = None

    def _testForDeprecatedAttributes(self):
        from warnings import warn
        if hasattr(self, "_frameAdjustments"):
            warn(DeprecationWarning("The _frameAdjustments attribute is deprecated. Use the frameAdjustments attribute."))
            self.frameAdjustments = self._frameAdjustments
        if hasattr(self, "_allFrameAdjustments"):
            warn(DeprecationWarning("The _allFrameAdjustments attribute is deprecated. Use the allFrameAdjustments attribute."))
            self.allFrameAdjustments = self._allFrameAdjustments

    def _setCallback(self, callback):
        if callback is not None:
            self._target = VanillaCallbackWrapper(callback)
            self._nsObject.setTarget_(self._target)
            self._nsObject.setAction_("action:")

    def _setAutosizingFromPosSize(self, posSize):
        l, t, w, h = posSize
        mask = 0

        if l < 0:
            mask |= NSViewMinXMargin
        if w <= 0 and (w > 0 or l >= 0):
            mask |= NSViewWidthSizable
        if w > 0 and l >= 0:
            mask |= NSViewMaxXMargin

        if t < 0:
            mask |= NSViewMaxYMargin
        if h <= 0 and (h > 0 or t >= 0):
            mask |= NSViewHeightSizable
        if h > 0 and t >= 0:
            mask |= NSViewMinYMargin

        self._nsObject.setAutoresizingMask_(mask)

    def _setFrame(self, parentFrame):
        l, t, w, h = self._posSize
        frame  = _calcFrame(parentFrame, ((l, t), (w, h)))
        frame = self._adjustPosSize(frame)
        self._nsObject.setFrame_(frame)

    def _adjustPosSize(self, frame):
        if hasattr(self._nsObject, "cell") and self._nsObject.cell() is not None:
            sizeStyle = _reverseSizeStyleMap[self._nsObject.cell().controlSize()]
        else:
            sizeStyle = None
        #
        adjustments = self.frameAdjustments
        if adjustments:
            if sizeStyle is None:
                aL, aB, aW, aH = adjustments
            else:
                aL, aB, aW, aH = adjustments.get(sizeStyle, (0, 0, 0, 0))
            (fL, fB), (fW, fH) = frame
            fL = fL + aL
            fB = fB + aB
            fW = fW + aW
            fH = fH + aH
            frame = ((fL, fB), (fW, fH))
        return frame

    def _getContentView(self):
        return self._nsObject

    def enable(self, onOff):
        """
        Enable or disable the object. **onOff** should be a boolean.
        """
        self._nsObject.setEnabled_(onOff)

    def isVisible(self):
        """
        Return a bool indicting if the object is visible or not.
        """
        return not self._nsObject.isHidden()

    def show(self, onOff):
        """
        Show or hide the object.

        **onOff** A boolean value representing if the object should be shown or not.
        """
        self._nsObject.setHidden_(not onOff)

    def getPosSize(self):
        """
        The position and size of the object as a tuple of form *(left, top, width, height)*.
        """
        return self._posSize

    def setPosSize(self, posSize):
        """
        Set the postion and size of the object.

        **posSize** A tuple of form *(left, top, width, height)*.
        """
        self._posSize = posSize
        self._setAutosizingFromPosSize(posSize)
        superview = self._nsObject.superview()
        if superview is not None:
            self._setFrame(superview.frame())
            superview.setNeedsDisplay_(True)

    def move(self, x, y):
        """
        Move the object by **x** units and **y** units.
        """
        l, t, w, h = self.getPosSize()
        l = l + x
        t = t + y
        self.setPosSize((l, t, w, h))

    def resize(self, width, height):
        """
        Change the size of the object to **width** and **height**.
        """
        l, t, w, h = self.getPosSize()
        self.setPosSize((l, t, width, height))


class VanillaBaseControl(VanillaBaseObject):

    def _setSizeStyle(self, value):
        value = _sizeStyleMap[value]
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(value))
        self._nsObject.setFont_(font)

    def setTitle(self, title):
        """
        Set the control title.

        **title** A string representing the title.
        """
        self._nsObject.setTitle_(title)

    def getTitle(self):
        """
        Get the control title.
        """
        return self._nsObject.title()

    def set(self, value):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def bind(self, key, callback):
        raise NotImplementedError


class VanillaCallbackWrapper(NSObject):

    def __new__(cls, callback):
        return cls.alloc().initWithCallback_(callback)

    def initWithCallback_(self, callback):
        self = self.init()
        self.callback = callback
        return self

    def action_(self, sender):
        if hasattr(sender, "vanillaWrapper"):
            sender = sender.vanillaWrapper()
        if self.callback is not None:
            self.callback(sender)


_sizeStyleMap = {
    "regular": NSRegularControlSize,
    "small": NSSmallControlSize,
    "mini": NSMiniControlSize
}

_reverseSizeStyleMap = {
    NSRegularControlSize: "regular",
    NSSmallControlSize: "small",
    NSMiniControlSize: "mini"
}


def _calcFrame(parentFrame, posSize, absolutePositioning=False):
    """Convert a vanilla posSize rect to a Cocoa frame."""
    (pL, pB), (pW, pH) = parentFrame
    (l, t), (w, h) = posSize
    if not absolutePositioning:
        if l < 0:
            l = pW + l
        if w <= 0:
            w = pW + w - l
        if t < 0:
            t = pH + t
        if h <= 0:
            h = pH + h - t
    b = pH - t - h  # flip it upside down
    return (l, b), (w, h)


def _flipFrame(parentFrame, objFrame):
    """Translate a Cocoa frame to vanilla coordinates"""
    (pL, pB), (pW, pH) = parentFrame
    (oL, oB), (oW, oH) =  objFrame
    oT = pH - oB - oH
    return oL, oT, oW, oH


def _breakCycles(view):
    """Break cyclic references by deleting _target attributes."""
    if hasattr(view, "vanillaWrapper"):
        obj = view.vanillaWrapper()
        if hasattr(obj, "_breakCycles"):
            obj._breakCycles()
    for view in view.subviews():
        _breakCycles(view)


def _setAttr(cls, obj, attr, value):
    if isinstance(value, VanillaBaseObject):
        assert not hasattr(obj, attr), "can't replace vanilla attribute"
        view = obj._getContentView()
        frame = view.frame()
        value._setFrame(frame)
        view.addSubview_(value._nsObject)
    #elif isinstance(value, NSView) and not attr.startswith("_"):
    #    assert not hasattr(obj, attr), "can't replace vanilla attribute"
    #    view = obj._getContentView()
    #    view.addSubview_(value)
    super(cls, obj).__setattr__(attr, value)

def _delAttr(cls, obj, attr):
    value = getattr(obj, attr)
    if isinstance(value, VanillaBaseObject):
        value._nsObject.removeFromSuperview()
    #elif isinstance(value, NSView):
    #    value.removeFromSuperview()
    super(cls, obj).__delattr__(attr)
