from Foundation import *
from AppKit import *
from vanillaBase import VanillaBaseControl


_modeMap = {
    "graphical": NSClockAndCalendarDatePickerStyle,
    "text": 2, #NSTextFieldDatePickerStyle raises an error
    "textStepper": NSTextFieldAndStepperDatePickerStyle,
}

_timeDisplayFlagMap = {
    None : 0,
    "hourMinute" : NSHourMinuteDatePickerElementFlag,
    "hourMinuteSecond" : NSHourMinuteSecondDatePickerElementFlag,
}

_dateDisplayFlagMap = {
    None : 0,
    "yearMonth" : NSYearMonthDatePickerElementFlag,
    "yearMonthDay" : NSYearMonthDayDatePickerElementFlag,
}

class DatePicker(VanillaBaseControl):

    """
    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the date picker control.

    +-------------------------------------+
    | **Standard Dimensions - Text Mode** |
    +---------+---+-----------------------+
    | Regular | H | 22                    |
    +---------+---+-----------------------+
    | Small   | H | 19                    |
    +---------+---+-----------------------+
    | Mini    | H | 16                    |
    +---------+---+-----------------------+

    +------------------------------------------+
    | **Standard Dimensions - Graphical Mode** |
    +--------------------+---------------------+
    | Calendar and Clock | 227w 148h           |
    +--------------------+---------------------+
    | Calendar           | 139w 148h           |
    +--------------------+---------------------+
    | Clock              | 122w 123h           |
    +--------------------+---------------------+

    **date** A *NSDate* object representing the date and time that should be set in the control.

    **minDate** A *NSDate* object representing the lowest date and time that can be set in the control.

    **maxDate** A *NSDate* object representing the highest date and time that can be set in the control.

    **showStepper** A boolean indicating if the thumb stepper should be shown in text mode.

    **mode** A string representing the desired mode for the date picker control. The options are:

    +-------------+
    | "text"      |
    +-------------+
    | "graphical" |
    +-------------+

    **timeDisplay** A string representing the desired time units that should be displayed in the
    date picker control. The options are:

    +--------------------+-------------------------------+
    | None               | Do not display time.          |
    +--------------------+-------------------------------+
    | "hourMinute"       | Display hour and minute.      |
    +--------------------+-------------------------------+
    | "hourMinuteSecond" | Display hour, minute, second. |
    +--------------------+-------------------------------+

    **dateDisplay** A string representing the desired date units that should be displayed in the
    date picker control. The options are:

    +----------------+------------------------------+
    | None           | Do not display date.         |
    +----------------+------------------------------+
    | "yearMonth"    | Display year and month.      |
    +----------------+------------------------------+
    | "yearMonthDay" | Display year, month and day. |
    +----------------+------------------------------+

    **sizeStyle** A string representing the desired size style of the date picker control. This only
    applies in text mode. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsDatePickerClass = NSDatePicker

    def __init__(self, posSize, date=None, minDate=None, maxDate=None, showStepper=True, mode="text",
        timeDisplay="hourMinuteSecond", dateDisplay="yearMonthDay", callback=None, sizeStyle="regular"):
        self._setupView(self.nsDatePickerClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.setDrawsBackground_(True)
        self._nsObject.setBezeled_(True)
        if mode == "text" and showStepper:
            mode += "Stepper"
        style = _modeMap[mode]
        self._nsObject.setDatePickerStyle_(style)
        flag = _timeDisplayFlagMap[timeDisplay]
        flag = flag | _dateDisplayFlagMap[dateDisplay]
        self._nsObject.setDatePickerElements_(flag)
        if date is None:
            date = NSDate.date()
        self._nsObject.setDateValue_(date)
        if minDate is not None:
            self._nsObject.setMinDate_(minDate)
        if maxDate is not None:
            self._nsObject.setMaxDate_(maxDate)

    def getNSDatePicker(self):
        """
        Return the *NSDatePicker* that this object wraps.
        """
        return self._nsObject

    def get(self):
        """
        Get the contents of the date picker control.
        """
        return self._nsObject.dateValue()

    def set(self, value):
        """
        Set the contents of the date picker control.

        **value** A *NSDate* object.
        """
        self._nsObject.setDateValue_(value)
