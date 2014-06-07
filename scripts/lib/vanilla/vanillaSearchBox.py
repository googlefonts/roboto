from AppKit import NSSearchField
from vanillaBase import VanillaBaseControl


class SearchBox(VanillaBaseControl):

    """
    A text entry field similar to the search field in Safari.::

        from vanilla import *

        class SearchBoxDemo(object):

            def __init__(self):
                self.w = Window((100, 42))
                self.w.searchBox = SearchBox((10, 10, -10, 22),
                                        callback=self.searchBoxCallback)
                self.w.open()

            def searchBoxCallback(self, sender):
                print "search box entry!", sender.get()

        SearchBoxDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing
    the position and size of the search box.

    +-------------------------+
    | **Standard Dimensions** |
    +---------+---+-----------+
    | Regular | H | 22        |
    +---------+---+-----------+
    | Small   | H | 19        |
    +---------+---+-----------+
    | Mini    | H | 15        |
    +---------+---+-----------+

    **text** The text to be displayed in the search box.

    **callback** The method to be called when the user presses the search box.

    **formatter** A `NSFormatter <http://developer.apple.com/documentation/Cocoa/Reference/Foundation/Classes/NSFormatter_Class/index.html>`_
    for controlling the display and input of the text entry.

    **placeholder** A placeholder string to be shown when the text entry
    control is empty.

    **sizeStyle** A string representing the desired size style of the search box.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsSearchFieldClass = NSSearchField

    def __init__(self, posSize, text="", callback=None, formatter=None, placeholder=None, sizeStyle="regular"):
        self._setupView(self.nsSearchFieldClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.setStringValue_(text)
        cell = self._nsObject.cell()
        cell.setScrollable_(True)
        if formatter is not None:
            cell.setFormatter_(formatter)
        if placeholder:
            cell.setPlaceholderString_(placeholder)

    def getNSSearchField(self):
        """
        Return the *NSSearchField* that this object wraps.
        """
        return self._nsObject

    def get(self):
        """
        Get the contents of the search box.
        """
        return self._nsObject.stringValue()

    def set(self, value):
        """
        Set the contents of the search box.

        **value** A string representing the contents of the search box.
        """
        self._nsObject.setStringValue_(value)
