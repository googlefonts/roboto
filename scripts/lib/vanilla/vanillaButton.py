from AppKit import *
from vanillaBase import VanillaBaseControl


_modifierMap = {
    "command": NSCommandKeyMask,
    "control": NSAlternateKeyMask,
    "option": NSAlternateKeyMask,
    "shift": NSShiftKeyMask,
    "capslock": NSAlphaShiftKeyMask,
}

_keyMap = {
    "help": NSHelpFunctionKey,
    "home": NSHomeFunctionKey,
    "end": NSEndFunctionKey,
    "pageup": NSPageUpFunctionKey,
    "pagedown": NSPageDownFunctionKey,
    "forwarddelete": NSDeleteFunctionKey,
    "leftarrow": NSLeftArrowFunctionKey,
    "rightarrow": NSRightArrowFunctionKey,
    "uparrow": NSUpArrowFunctionKey,
    "downarrow": NSDownArrowFunctionKey,
}


class Button(VanillaBaseControl):

    """
    A standard button.::

        from vanilla import *

        class ButtonDemo(object):

             def __init__(self):
                 self.w = Window((100, 40))
                 self.w.button = Button((10, 10, -10, 20), "A Button",
                                    callback=self.buttonCallback)
                 self.w.open()

             def buttonCallback(self, sender):
                 print "button hit!"

        ButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position
    and size of the button. The size of the button sould match the appropriate value
    for the given *sizeStyle*.

    +-------------------------+
    | **Standard Dimensions** |
    +=========+===+===========+
    | Regular | H | 20        |
    +---------+---+-----------+
    | Small   | H | 17        |
    +---------+---+-----------+
    | Mini    | H | 14        |
    +---------+---+-----------+

    **title** The text to be displayed on the button. Pass *None* is no title is desired.

    **callback** The method to be called when the user presses the button.

    **sizeStyle** A string representing the desired size style of the button. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsButtonClass = NSButton
    nsBezelStyle = NSRoundedBezelStyle
    nsButtonType = NSMomentaryPushInButton

    frameAdjustments = {
        "mini": (-1, -2, 2, 2),
        "small": (-5, -7, 10, 11),
        "regular": (-6, -8, 12, 12),
        }

    def __init__(self, posSize, title, callback=None, sizeStyle="regular"):
        self._setupView(self.nsButtonClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.setTitle_(title)
        self._nsObject.setBezelStyle_(self.nsBezelStyle)
        self._nsObject.setButtonType_(self.nsButtonType)

    def _testForDeprecatedAttributes(self):
        super(Button, self)._testForDeprecatedAttributes()
        from warnings import warn
        if hasattr(self, "_nsBezelStyle"):
            warn(DeprecationWarning("The _nsBezelStyle attribute is deprecated. Use the nsBezelStyle attribute."))
            self.nsBezelStyle = self._nsBezelStyle
        if hasattr(self, "_nsButtonType"):
            warn(DeprecationWarning("The _nsButtonType attribute is deprecated. Use the nsButtonType attribute."))
            self.nsButtonType = self._nsButtonType

    def getNSButton(self):
        """
        Return the *NSButton* that this object wraps.
        """
        return self._nsObject

    def bind(self, key, modifiers):
        """
        Bind a key to the button.

        **key** A single character or one of the following:

        +-----------------+
        | "help"          |
        +-----------------+
        | "home"          |
        +-----------------+
        | "end"           |
        +-----------------+
        | "pageup"        |
        +-----------------+
        | "pagedown"      |
        +-----------------+
        | "forwarddelete" |
        +-----------------+
        | "leftarrow"     |
        +-----------------+
        | "rightarrow"    |
        +-----------------+
        | "uparrow"       |
        +-----------------+
        | "downarrow"     |
        +-----------------+

        **modifiers** A list containing nothing or as many of the following as desired:

        +------------+
        | "command"  |
        +------------+
        | "control"  |
        +------------+
        | "option"   |
        +------------+
        | "shift"    |
        +------------+
        | "capslock" |
        +------------+
        """
        modifiers = sum([_modifierMap[i] for i in modifiers])
        key = _keyMap.get(key, key)
        self._nsObject.setKeyEquivalent_(key)
        self._nsObject.setKeyEquivalentModifierMask_(modifiers)


class SquareButton(Button):

    """
    A standard square button.::

        from vanilla import *

        class SquareButtonDemo(object):

             def __init__(self):
                 self.w = Window((200, 100))
                 self.w.button = SquareButton((10, 10, -10, -10), "A Button",
                                    callback=self.buttonCallback)
                 self.w.open()

             def buttonCallback(self, sender):
                 print "button hit!"

        SquareButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the button.

    **title** The text to be displayed on the button. Pass _None_ is no title is desired.

    **callback** The method to be called when the user presses the button.

    **sizeStyle** A string representing the desired size style of the button. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsBezelStyle = NSShadowlessSquareBezelStyle
    frameAdjustments = None

    def __init__(self, posSize, title, callback=None, sizeStyle="regular"):
        super(SquareButton, self).__init__(posSize=posSize, title=title, callback=callback, sizeStyle=sizeStyle)


_imagePositionMap = {
        "left": NSImageLeft,
        "right": NSImageRight,
        "top": NSImageAbove,
        "bottom": NSImageBelow,
        }

class ImageButton(SquareButton):

    """
    A button with an image.::

        from vanilla import *

        class ImageButtonDemo(object):

             def __init__(self):
                 path = "/path/to/an/image"
                 self.w = Window((50, 50))
                 self.w.button = ImageButton((10, 10, 30, 30), imagePath=path,
                                    callback=self.buttonCallback)
                 self.w.open()

             def buttonCallback(self, sender):
                 print "button hit!"

        ImageButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the button.

    **title** The text to be displayed on the button. Pass *None* is no title is desired.

    **bordered** Boolean representing if the button should be bordered.

    **imagePath** A file path to an image.

    **imageNamed** The name of an image already load as a *NSImage* by the application.

    **imageObject** A *NSImage* object.

    *Only one of imagePath, imageNamed, imageObject should be set.*

    **imagePosition** The position of the image relative to the title. The options are:

    +----------+
    | "top"    |
    +----------+
    | "bottom" |
    +----------+
    | "left"   |
    +----------+
    | "right"  |
    +----------+

    **callback** The method to be called when the user presses the button.

    **sizeStyle** A string representing the desired size style of the button. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    frameAdjustments = None

    def __init__(self, posSize,
                imagePath=None, imageNamed=None, imageObject=None,
                title=None, bordered=True, imagePosition="top", callback=None, sizeStyle="regular"):
        super(ImageButton,  self).__init__(posSize, title=title, callback=callback, sizeStyle=sizeStyle)
        image = None
        if imagePath is not None:
            image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        if image is not None:
            self._nsObject.setImage_(image)
        self._nsObject.setBordered_(bordered)
        if title is None:
            position = NSImageOnly
        else:
            position= _imagePositionMap[imagePosition]
            if imagePosition == "left":
                self._nsObject.setAlignment_(NSRightTextAlignment)
            elif imagePosition == "right":
                self._nsObject.setAlignment_(NSLeftTextAlignment)
        if not bordered:
            self._nsObject.cell().setHighlightsBy_(NSNoCellMask)
        self._nsObject.setImagePosition_(position)

    def setImage(self, imagePath=None, imageNamed=None, imageObject=None):
        """
        Set the image in the button.

        **imagePath** A file path to an image.

        **imageNamed** The name of an image already load as a *NSImage* by the application.

        **imageObject** A *NSImage* object.

        *Only one of imagePath, imageNamed, imageObject should be set.*
        """
        if imagePath is not None:
            image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        else:
            raise ValueError, "no image source defined"
        self._nsObject.setImage_(image)


class HelpButton(Button):

    """
    A standard help button.::

        from vanilla import *

        class HelpButtonDemo(object):

             def __init__(self):
                 self.w = Window((90, 40))
                 self.w.button = HelpButton((10, 10, 21, 20),
                                    callback=self.buttonCallback)
                 self.w.open()

             def buttonCallback(self, sender):
                 print "help button hit!"

        HelpButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and
    size of the button. The size of the button sould match the standard dimensions.

    +-------------------------+
    | **Standard Dimensions** |
    +--------+----------------+
    | Width  | 21             |
    +--------+----------------+
    | Height | 20             |
    +--------+----------------+

    **callback** The method to be called when the user presses the button.
    """

    nsBezelStyle = NSHelpButtonBezelStyle
    frameAdjustments = {
        "regular": (0, -3, 0, 3),
        }

    def __init__(self, posSize, callback=None, page=None, anchor=None):
        # XXX perhaps this should choke if more than one arg is present.
        # callback, page and anchor are all mutually exclusive.
        self._page = page
        self._anchor = anchor
        if callback is None:
            if page is not None or anchor is not None:
                callback = self._helpBookCallback
        super(HelpButton, self).__init__(posSize, title="", callback=callback)

    def _helpBookCallback(self, sender):
        from Carbon import AH
        bundle = NSBundle.mainBundle()
        if bundle is None:
            return
        info = bundle.infoDictionary()
        helpBookName = info.get("CFBundleHelpBookName")
        if self._page is not None:
            AH.AHGoToPage(helpBookName, self._page, self._anchor)
        elif self._anchor is not None:
            AH.AHLookupAnchor(helpBookName, self._anchor)

