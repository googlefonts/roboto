from AppKit import *
from vanillaBase import VanillaBaseControl

# This control is available in OS 10.4+.
# Cause a NameError if in an earlier OS.
NSLevelIndicator


_tickPositionMap = {
    "above": NSTickMarkAbove,
    "below": NSTickMarkBelow,
}

_levelIndicatorStyleMap = {
    "discrete":   NSDiscreteCapacityLevelIndicatorStyle,
    "continuous": NSContinuousCapacityLevelIndicatorStyle,
    "rating":     NSRatingLevelIndicatorStyle,
    "relevancy":  NSRelevancyLevelIndicatorStyle,
}


class LevelIndicator(VanillaBaseControl):

    """
    A control which shows a value on a linear scale.::

        from vanilla import *

        class LevelIndicatorDemo(object):

             def __init__(self):
                 self.w = Window((200, 68))
                 self.w.discreteIndicator = LevelIndicator(
                            (10, 10, -10, 18), callback=self.levelIndicatorCallback)
                 self.w.continuousIndicator = LevelIndicator(
                            (10, 40, -10, 18), style="continuous",
                            callback=self.levelIndicatorCallback)
                 self.w.open()

             def levelIndicatorCallback(self, sender):
                 print "level indicator edit!", sender.get()

        LevelIndicatorDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position
    and size of the level indicator.

    +-------------------------------+
    | **Standard Dimensions()**     |
    +-------------------------------+
    | *discrete without ticks*      |
    +-------------------------------+
    | H | 18                        |
    +-------------------------------+
    | *discrete with minor ticks*   |
    +-------------------------------+
    | H | 22                        |
    +-------------------------------+
    | *discrete with major ticks*   |
    +-------------------------------+
    | H | 25                        |
    +-------------------------------+
    | *continuous without ticks*    |
    +-------------------------------+
    | H | 16                        |
    +-------------------------------+
    | *continuous with minor ticks* |
    +-------------------------------+
    | H | 20                        |
    +-------------------------------+
    | *continuous with major ticks* |
    +-------------------------------+
    | H | 23                        |
    +-------------------------------+

    **style** The style of the level indicator. The options are:

    +--------------+-------------------+
    | "continuous" | A continuous bar. |
    +--------------+-------------------+
    | "discrete"   | A segmented bar.  |
    +--------------+-------------------+

    **value** The initial value of the level indicator.

    **minValue** The minimum value allowed by the level indicator.

    **maxValue** The maximum value allowed by the level indicator.

    **warningValue** The value at which the filled portions of the
    level indicator should display the warning color.

    **criticalValue** The value at which the filled portions of the
    level indicator should display the critical color.

    **tickMarkPosition** The position of the tick marks in relation
    to the level indicator. The options are:

    +---------+
    | "above" |
    +---------+
    | "below" |
    +---------+

    **minorTickMarkCount** The number of minor tick marcks to be displayed
    on the level indicator. If *None* is given, no minor tick marks will be displayed.

    **majorTickMarkCount** The number of major tick marcks to be displayed on the level
    indicator. If *None* is given, no major tick marks will be displayed.

    **callback** The method to be called when the level indicator has been edited.
    If no callback is given, the level indicator will not be editable.
    """

    nsLevelIndicatorClass = NSLevelIndicator

    def __init__(self, posSize, style="discrete",
                    value=5, minValue=0, maxValue=10, warningValue=None, criticalValue=None,
                    tickMarkPosition=None, minorTickMarkCount=None, majorTickMarkCount=None,
                    callback=None):
        self._setupView(self.nsLevelIndicatorClass, posSize, callback=callback)
        self._nsObject.cell().setLevelIndicatorStyle_(_levelIndicatorStyleMap[style])
        self._nsObject.setMinValue_(minValue)
        self._nsObject.setMaxValue_(maxValue)
        self._nsObject.setFloatValue_(value)
        if warningValue is not None:
            self._nsObject.setWarningValue_(warningValue)
        if criticalValue is not None:
            self._nsObject.setCriticalValue_(criticalValue)
        if tickMarkPosition is not None:
            self._nsObject.setTickMarkPosition_(_tickPositionMap[tickMarkPosition])
        if minorTickMarkCount is not None:
            self._nsObject.setNumberOfTickMarks_(minorTickMarkCount)
        if majorTickMarkCount is not None:
            self._nsObject.setNumberOfMajorTickMarks_(majorTickMarkCount)
        if callback is None:
            self._nsObject.cell().setEnabled_(False)

    def getNSLevelIndicator(self):
        """
        Return the *NSLevelIndicator* that this object wraps.
        """
        return self._nsObject

    def set(self, value):
        """
        Set the value of the level indicator.
        """
        self._nsObject.setFloatValue_(value)

    def get(self):
        """
        Get the value of the level indicator.
        """
        return self._nsObject.floatValue()

    def setMinValue(self, value):
        """
        Set the minimum value of the level indicator.
        """
        self._nsObject.setMinValue_(value)

    def getMinValue(self):
        """
        Get the minimum value of the level indicator.
        """
        return self._nsObject.minValue()

    def setMaxValue(self, value):
        """
        Set the maximum of the level indicator.
        """
        self._nsObject.setMaxValue_(value)

    def getMaxValue(self):
        """
        Get the maximum of the level indicator.
        """
        return self._nsObject.maxValue()

    def setWarningValue(self, value):
        """
        Set the warning value of the level indicator.
        """
        self._nsObject.setWarningValue_(value)

    def getWarningValue(self, value):
        """
        Get the warning value of the level indicator.
        """
        return self._nsObject.warningValue()

    def setCriticalValue(self, value):
        """
        Set the critical value of the level indicator.
        """
        self._nsObject.setCriticalValue_(value)

    def getCriticalValue(self, value):
        """
        Get the critical value of the level indicator.
        """
        return self._nsObject.criticalValue()


def LevelIndicatorListCell(style="discrete",
        minValue=0, maxValue=10, warningValue=None, criticalValue=None,
        imagePath=None, imageNamed=None, imageObject=None):

    """
    An object that displays a level indicator in a List column.

    **This object should only be used in the *columnDescriptions* argument
    during the construction of a List.**::

        from vanilla import *

        class LevelIndicatorListCellDemo(object):

             def __init__(self):
                 self.w = Window((340, 140))
                 items = [
                     {"discrete": 3, "continuous": 4, "rating": 1, "relevancy": 9},
                     {"discrete": 8, "continuous": 3, "rating": 5, "relevancy": 5},
                     {"discrete": 3, "continuous": 7, "rating": 3, "relevancy": 4},
                     {"discrete": 2, "continuous": 5, "rating": 4, "relevancy": 7},
                     {"discrete": 6, "continuous": 9, "rating": 3, "relevancy": 2},
                     {"discrete": 4, "continuous": 0, "rating": 6, "relevancy": 8},
                 ]
                 columnDescriptions = [
                     {"title": "discrete",
                     "cell": LevelIndicatorListCell(style="discrete", warningValue=7, criticalValue=9)},
                     {"title": "continuous", 
                     "cell": LevelIndicatorListCell(style="continuous", warningValue=7, criticalValue=9)},
                     {"title": "rating",
                     "cell": LevelIndicatorListCell(style="rating", maxValue=6)},
                     {"title": "relevancy",
                     "cell": LevelIndicatorListCell(style="relevancy")},
                 ]
                 self.w.list = List((0, 0, -0, -0), items=items,
                                columnDescriptions=columnDescriptions)
                 self.w.open()

        LevelIndicatorListCellDemo()

    **style** The style of the level indicator. The options are:

    +--------------+-----------------------------------------+
    | "continuous" | A continuous bar.                       |
    +--------------+-----------------------------------------+
    | "discrete"   | A segmented bar.                        |
    +--------------+-----------------------------------------+
    | "rating"     | A row of stars. Similar to the rating   |
    |              | indicator in iTunes.                    |
    +--------------+-----------------------------------------+
    | "relevancy"  | A row of lines. Similar to the search   |
    |              | result relevancy indicator in Mail.     |
    +--------------+-----------------------------------------+

    **minValue** The minimum value allowed by the level indicator.

    **maxValue** The maximum value allowed by the level indicator.

    **warningValue** The value at which the filled portions of the
    level indicator should display the warning color. Applies only to
    discrete and continuous level indicators.

    **criticalValue** The value at which the filled portions of the
    level indicator should display the critical color. Applies only to
    discrete and continuous level indicators.
    """
    cell = NSLevelIndicatorCell.alloc().init()
    cell.setLevelIndicatorStyle_(_levelIndicatorStyleMap[style])
    cell.setMinValue_(minValue)
    cell.setMaxValue_(maxValue)
    if warningValue is not None:
        cell.setWarningValue_(warningValue)
    if criticalValue is not None:
        cell.setCriticalValue_(criticalValue)
    if imagePath is not None:
        image = NSImage.alloc().initWithContentsOfFile_(imagePath)
    elif imageNamed is not None:
        image = NSImage.imageNamed_(imageNamed)
    elif imageObject is not None:
        image = imageObject
    if imageObject is not None:
        cell.setImage_(image)
    return cell
