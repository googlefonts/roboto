from AppKit import *
from vanillaBase import VanillaBaseControl, VanillaError

_tickPositionMap = {
    "left": NSTickMarkLeft,
    "right": NSTickMarkRight,
    "top": NSTickMarkAbove,
    "bottom": NSTickMarkBelow,
}


class Slider(VanillaBaseControl):

    """
    A standard slider control. Sliders can be vertical or horizontal and
    they can show tick marks or not show tick marks.::

        from vanilla import *

        class SliderDemo(object):

             def __init__(self):
                 self.w = Window((200, 43))
                 self.w.slider = Slider((10, 10, -10, 23),
                                    tickMarkCount=10,
                                    callback=self.sliderCallback)
                 self.w.open()

             def sliderCallback(self, sender):
                 print "slider edit!", sender.get()

        SliderDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and
    size of the slider. The size of the slider sould match the appropriate value for
    the given *sizeStyle*.

    +---------------------------+
    | **Standard Dimensions**   |
    +---------------------------+
    | *without ticks*           |
    +---------+---+----+---+----+
    | Regular | W | 15 | H | 15 |
    +---------+---+----+---+----+
    | Small   | W | 12 | H | 11 |
    +---------+---+----+---+----+
    | Mini    | W | 10 | H | 10 |
    +---------+---+----+---+----+
    | *with ticks*              |
    +---------+---+----+---+----+
    | Regular | W | 24 | H | 23 |
    +---------+---+----+---+----+
    | Small   | W | 17 | H | 17 |
    +---------+---+----+---+----+
    | Mini    | W | 16 | H | 16 |
    +---------+---+----+---+----+

    **minValue** The minimum value allowed by the slider.

    **maxValue** The maximum value allowed by the slider.

    **value** The initial value of the slider.

    **tickMarkCount** The number of tick marcks to be displayed on the slider.
    If *None* is given, no tick marks will be displayed.

    **stopOnTickMarks** Boolean representing if the slider knob should only
    stop on the tick marks.

    **continuous** Boolean representing if the assigned callback should be
    called during slider editing. If *False* is given, the callback will be
    called after the editing has finished.

    **callback** The method to be called when the slider has been edited.

    **sizeStyle** A string representing the desired size style of the slider.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsSliderClass = NSSlider

    allFrameAdjustments = {
        "H-Slider-Above": {
            "mini": (0, 0, 0, 0),
            "small": (0, -1, 0, -1),
            "regular": (-2, -2, 4, 2),
        },
        "H-Slider-Below": {
            "mini": (0, 0, 0, 0),
            "small": (0, 0, 0, 0),
            "regular": (-2, 0, 4, 1),
        },
        "H-Slider-None": {
            "mini": (0, -1, 0, 2),
            "small": (0, -2, 0, 3),
            "regular": (-2, -4, 4, 6),
        },
        "V-Slider-Left": {
            "mini": (0, -1, 1, 1),
            "small": (0, -1, 1, 1),
            "regular": (0, -3, 2, 5),
        },
        "V-Slider-Right": {
            "mini": (0, -1, 1, 1),
            "small": (-1, -1, 2, 1),
            "regular": (-2, -3, 2, 5),
        },
        "V-Slider-None": {
            "mini": (0, -1, 1, 1),
            "small": (-2, -1, 4, 1),
            "regular": (-3, -3, 6, 5),
        },
    }

    def __init__(self, posSize, minValue=0, maxValue=100, value=50,
            tickMarkCount=None, stopOnTickMarks=False, continuous=True,
            callback=None, sizeStyle="regular"):
        self._setupView(self.nsSliderClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.setMinValue_(minValue)
        self._nsObject.setMaxValue_(maxValue)
        self._nsObject.setFloatValue_(value)
        if tickMarkCount:
            self._nsObject.setNumberOfTickMarks_(tickMarkCount)
            if stopOnTickMarks:
                self._nsObject.setAllowsTickMarkValuesOnly_(True)
        if continuous:
            self._nsObject.setContinuous_(True)
        else:
            self._nsObject.setContinuous_(False)

    def getNSSlider(self):
        """
        Return the *NSSlider* that this object wraps.
        """
        return self._nsObject

    def _adjustPosSize(self, frame):
        # temporarily store the some data for positioning reference
        w, h = self._posSize[2:]
        if w > h:
            prefix = "H-"
            isVertical = False
        else:
            isVertical = True
            prefix = "V-"
        tickPos = "None"
        tickMarkCount = self._nsObject.numberOfTickMarks()
        if tickMarkCount:
            tickPos = self._nsObject.tickMarkPosition()
            if isVertical:
                if tickPos == NSTickMarkLeft:
                    tickPos = "Left"
                elif tickPos == NSTickMarkRight:
                    tickPos = "Right"
                # during __init__, the _nsObject will be unable
                # to determine if the slider is horizontal or
                # vertical, so it will return the position for
                # horizontal sliders. override that and default
                # to right here.
                else:
                    tickPos = "Right"
            else:
                if tickPos == NSTickMarkBelow:
                    tickPos = "Below"
                elif tickPos == NSTickMarkAbove:
                    tickPos = "Above"
        sliderType = prefix + "Slider-" + tickPos
        self.frameAdjustments = self.allFrameAdjustments[sliderType]
        # now let the super class do the work
        return super(Slider, self)._adjustPosSize(frame)

    def get(self):
        """
        Get the value of the slider.
        """
        return self._nsObject.floatValue()

    def set(self, value):
        """
        Set the value of the slider.
        """
        self._nsObject.setFloatValue_(value)

    def setMinValue(self, value):
        """
        Set the minimum value allowed by the slider.
        """
        self._nsObject.setMinValue_(value)

    def setMaxValue(self, value):
        """
        Set the maximum value allowed by the slider.
        """
        self._nsObject.setMaxValue_(value)

    def setTickMarkCount(self, value):
        """
        Set the number of tick marks on the slider.
        """
        self._nsObject.setNumberOfTickMarks_(value)

    def setTickMarkPosition(self, value):
        """
        Set the position of the tick marks on the slider.

        For vertical sliders, the options are:

        +---------+
        | "left"  |
        +---------+
        | "right" |
        +---------+

        For horizontal sliders, the options are:

        +----------+
        | "top"    |
        +----------+
        | "bottom" |
        +----------+
        """
        # don't rely on self._nsObject.isVertical here
        # because if this is called before the object
        # has been added to an open window, the isVertical
        # method is unable to determine horizontal or vertical
        w, h = self._posSize[2:]
        if w > h:
            isVertical = False
        else:
            isVertical = True
        if isVertical:
            if value == "top" or value == "bottom":
                raise VanillaError("vertical sliders can only position tick marks at 'left' or 'right'")
        else:
            if value == "left" or value == "right":
                raise VanillaError("horizontal sliders can only position tick marks at 'top' or 'bottom'")
        position = _tickPositionMap[value]
        self._nsObject.setTickMarkPosition_(position)
