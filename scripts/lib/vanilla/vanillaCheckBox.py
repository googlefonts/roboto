from AppKit import *
from vanilla import Button, VanillaBaseObject


# In OS 10.0-10.X (tested up to OS 10.4) the small and mini check box
# buttons created in InterfaceBuilder can not be replicated programmatically.
# The text is not properly aligned with the check box button. To get around
# this we manually position the text next to the check box. Once Apple
# fixes this problem, we can revert back to the standard method for
# creating the control.


class _CheckBoxStandardBuild(Button):

    nsButtonType = NSSwitchButton
    frameAdjustments = {
        "mini": (-4, -4, 6, 8),
        "small": (-3, -2, 5, 4),
        "regular": (-2, -2, 4, 4),
    }

    def __init__(self, posSize, title, callback=None, value=False, sizeStyle="regular"):
        super(_CheckBoxStandardBuild, self).__init__(posSize, title, callback=callback, sizeStyle=sizeStyle)
        self.set(value)

    def set(self, value):
        """
        Set the state of the check box.

        **value** A boolean representing the state of the check box.
        """
        self._nsObject.setState_(value)

    def get(self):
        """
        Get the state of the check box.
        """
        return self._nsObject.state()

    def toggle(self):
        """
        Toggle the state of the check box.

        If the check box is on, turn it off. If the check box is off, turn it on.
        """
        state = self.get()
        self.set(not state)


class _CheckBoxManualBuildButton(Button):

    nsButtonType = NSSwitchButton
    frameAdjustments = {
        "regular": (-2, -3, 4, 4),
        "small": (-3, -7, 5, 4),
        "mini": (-3, -11, 6, 8),
        }

    def set(self, value):
        self._nsObject.setState_(value)

    def get(self):
        return self._nsObject.state()

    def toggle(self):
        state = self.get()
        self.set(not state)


class _CheckBoxManualBuildTextButton(Button):

    nsBezelStyle = NSShadowlessSquareBezelStyle
    frameAdjustments = None

    def __init__(self, posSize, title, callback, sizeStyle):
        super(_CheckBoxManualBuildTextButton, self).__init__(posSize, title=title, callback=callback)
        self._nsObject.setBordered_(False)
        self._setSizeStyle(sizeStyle)
        self._nsObject.setAlignment_(NSLeftTextAlignment)
        self._nsObject.cell().setHighlightsBy_(NSNoCellMask)


class _CheckBoxManualBuild(VanillaBaseObject):

    # both the container view and the check box will be adjusted.
    # this is necessary to create the appropriate buffer
    # and to handle the alignment.

    allFrameAdjustments = {
        "mini": (0, -4, 0, 8),
        "small": (0, -2, 0, 4),
        "regular": (0, -2, 0, 4),
        }

    def __init__(self, posSize, title, callback=None, value=False, sizeStyle="regular"):
        # This control is created by making a NSView that will contain
        # a NSButton set to check box mode and another NSButton set
        # to borderless mode to show the text. These buttons have their
        # callback set to this class, which then calls the callback
        # assigned to this class.
        self._setupView("NSView", posSize)

        self._callback = callback

        buttonSizes = {
                "mini": (10, 10),
                "small": (18, 18),
                "regular": (22, 22)
                }
        left, top, width, height = posSize

        self.frameAdjustments = self.allFrameAdjustments[sizeStyle]

        buttonWidth, buttonHeight = buttonSizes[sizeStyle]
        buttonLeft, buttonTop = self.frameAdjustments[:2]
        buttonLeft= abs(buttonLeft)
        buttonTop = abs(buttonTop)

        # adjust the position of the text button in relation to the check box
        textBoxPosSize = {
                # left, top, height
                "mini": (10, 4, 12),
                "small": (14, 4, 14),
                "regular": (16, 3, 17)
                }
        textBoxLeft, textBoxTop, textBoxHeight = textBoxPosSize[sizeStyle]
        textBoxWidth = 0

        self._checkBox = _CheckBoxManualBuildButton((0, 0, buttonWidth, buttonHeight), "", callback=self._buttonHit, sizeStyle=sizeStyle)
        self._checkBox.set(value)

        self._textButton = _CheckBoxManualBuildTextButton((textBoxLeft, textBoxTop, textBoxWidth, textBoxHeight), title=title, callback=self._buttonHit, sizeStyle=sizeStyle)

    def getNSButton(self):
        """
        Return the *NSButton* that this object wraps.

        *This is currently not implemented for CheckBox.*
        """
        # this is not possible since the control is built from parts
        raise NotImplementedError

    def _buttonHit(self, sender):
        # if the text box is the sender,
        # flip the state of the check box
        if sender == self._textButton:
            self._checkBox.toggle()
        if self._callback is not None:
            self._callback(self)

    def _breakCycles(self):
        self._callback = None
        self._checkBox._breakCycles()
        self._textButton._breakCycles()

    def enable(self, onOff):
        """
        Enable or disable the object. **onOff** should be a boolean.
        """
        self._checkBox.enable(onOff)
        self._textButton.enable(onOff)

    def setTitle(self, title):
        """
        Set the control title.

        **title** A string representing the title.
        """
        self._textButton.setTitle(title)

    def getTitle(self):
        """
        Get the control title.
        """
        return self._textButton.getTitle()

    def get(self):
        """
        Get the state of the check box.
        """
        return self._checkBox.get()

    def set(self, value):
        """
        Set the state of the check box.

        **value** A boolean representing the state of the check box.
        """
        self._checkBox.set(value)

    def toggle(self):
        """
        Toggle the state of the check box.

        If the check box is on, turn it off. If the check box is off, turn it on.
        """
        self._checkBox.toggle()


class CheckBox(_CheckBoxManualBuild):

    """
    A standard check box.::

        from vanilla import *

        class CheckBoxDemo(object):

            def __init__(self):
                self.w = Window((100, 40))
                self.w.checkBox = CheckBox((10, 10, -10, 20), "A CheckBox",
                                   callback=self.checkBoxCallback, value=True)
                self.w.open()

            def checkBoxCallback(self, sender):
                print "check box state change!", sender.get()

        CheckBoxDemo()

    **posSize** Tuple of form (left, top, width, height) representing the position and size of
    the check box. The size of the check box should match the appropriate value for the given *sizeStyle*.

    +-------------------------+
    | **Standard Dimensions** |
    +---------+---+-----------+
    | Regular | H | 22        |
    +---------+---+-----------+
    | Small   | H | 18        |
    +---------+---+-----------+
    | Mini    | H | 10        |
    +---------+---+-----------+

    **title** The text to be displayed next to the check box. Pass *None* is no title is desired.

    **callback** The method to be called when the user changes the state of the check box.

    **value** A boolean representing the state of the check box.

    **sizeStyle** A string representing the desired size style of the check box. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    def __init__(self, posSize, title, callback=None, value=False, sizeStyle="regular"):
        super(CheckBox, self).__init__(posSize=posSize, title=title, callback=callback, value=value, sizeStyle=sizeStyle)

