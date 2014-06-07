from AppKit import *
from vanillaBase import VanillaBaseControl

class PathControl(VanillaBaseControl):

    """
    A path control.

    **posSize** Tuple of form *(left, top, width, height)* representing the position
    and size of the control. The size of the control sould match the appropriate value
    for the given *sizeStyle*.

    +-------------------------+
    | **Standard Dimensions** |
    +=========+===+===========+
    | Regular | H | 22        |
    +---------+---+-----------+
    | Small   | H | 20        |
    +---------+---+-----------+
    | Mini    | H | 18        |
    +---------+---+-----------+

    **url** The url to be displayed in the control. This should be a NSURL object.

    **editable** A boolean indicating if this control is editable or not.

    **callback** The method to be called when the user presses the control.

    **sizeStyle** A string representing the desired size style of the button. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsPathControlClass = NSPathControl
    nspathStyle = NSPathStyleStandard

    def __init__(self, posSize, url, editable=False, callback=None, sizeStyle="regular"):
        self._setupView(self.nsPathControlClass, posSize, callback=callback)
        self._nsObject.setPathStyle_(self.nspathStyle)
        self._setSizeStyle(sizeStyle)
        self._nsObject.setURL_(url)
        self._nsObject.setBackgroundColor_(NSColor.clearColor())
        self._nsObject.setFocusRingType_(NSFocusRingTypeNone)


#class PathControlBar(VanillaBaseControl):
#
#    nsPathControlClass = NSPathControl
#    nspathStyle = NSPathStyleNavigationBar
#
#    frameAdjustments = {
#        "mini": (-1, -2, 2, 2),
#        "small": (-5, -7, 10, 11),
#        "regular": (-6, -8, 12, 12),
#        }
#
#    def __init__(self, posSize, title, callback=None, sizeStyle="regular"):
#
#
#class PathControlPopUp(VanillaBaseControl):
#
#    nsPathControlClass = NSPathControl
#    nspathStyle = NSPathStylePopUp
#
#    frameAdjustments = {
#        "mini": (-1, -2, 2, 2),
#        "small": (-5, -7, 10, 11),
#        "regular": (-6, -8, 12, 12),
#        }
#
#    def __init__(self, posSize, title, callback=None, sizeStyle="regular"):
