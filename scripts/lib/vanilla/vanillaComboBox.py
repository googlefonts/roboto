from AppKit import NSComboBox
from vanillaBase import VanillaBaseControl


class ComboBox(VanillaBaseControl):

    """
    A text entry control that allows direct text entry or selection for a list of options.::

        from vanilla import *

        class ComboBoxDemo(object):

            def __init__(self):
                self.w = Window((100, 41))
                self.w.comboBox = ComboBox((10, 10, -10, 21),
                                    ["AA", "BB", "CC", "DD"],
                                    callback=self.comboBoxCallback)
                self.w.open()

            def comboBoxCallback(self, sender):
                print "combo box entry!", sender.get()

        ComboBoxDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the
    combo box control. The size of the combo box sould match the appropriate value for the given *sizeStyle*.

    +-------------------------+
    | **Standard Dimensions** |
    +---------+---+-----------+
    | Regular | H | 21        |
    +---------+---+-----------+
    | Small   | H | 17        |
    +---------+---+-----------+
    | Mini    | H | 14        |
    +---------+---+-----------+

    **items** The items to be displayed in the combo box.

    **completes** Boolean representing if the combo box auto completes entered text.

    **callback** The method to be called when the user enters text.

    **formatter** An `NSFormatter <http://developer.apple.com/documentation/Cocoa/Reference/Foundation/Classes/NSFormatter_Class/index.html>`_
    for controlling the display and input of the combo box.

    **sizeStyle** A string representing the desired size style of the combo box. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsComboBoxClass = NSComboBox

    frameAdjustments = {
        "mini": (0, -4, 1, 5),
        "small": (0, -4, 3, 5),
        "regular": (0, -3, 3, 5),
    }

    def __init__(self, posSize, items, completes=True, callback=None,
            formatter=None, sizeStyle="regular"):
        self._setupView(self.nsComboBoxClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.addItemsWithObjectValues_(items)
        self._nsObject.setCompletes_(completes)
        if formatter is not None:
            self._nsObject.cell().setFormatter_(formatter)

    def getNSComboBox(self):
        """
        Return the *NSComboBox* that this object wraps.
        """
        return self._nsObject

    def get(self):
        """
        Get the text entered in the combo box.
        """
        return self._nsObject.objectValue()

    def set(self, value):
        """
        Set the text in the text field of the combo box.

        **value** A string to set in the combo box.
        """
        self._nsObject.setObjectValue_(value)

    def setItems(self, items):
        """
        Set the items in the combo box list.

        **items** A list of strings to set in the combo box list.
        """
        self._nsObject.removeAllItems()
        self._nsObject.addItemsWithObjectValues_(items)
