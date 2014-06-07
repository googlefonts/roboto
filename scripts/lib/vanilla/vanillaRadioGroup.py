from AppKit import *
from vanillaBase import VanillaBaseControl, _sizeStyleMap


class RadioGroup(VanillaBaseControl):

    """
    A collection of radio buttons.::

        from vanilla import *

        class RadioGroupDemo(object):

            def __init__(self):
                self.w = Window((100, 60))
                self.w.radioGroup = RadioGroup((10, 10, -10, 40),
                                        ["Option 1", "Option 2"],
                                        callback=self.radioGroupCallback)
                self.w.open()

            def radioGroupCallback(self, sender):
                print "radio group edit!", sender.get()

        RadioGroupDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing
    the position and size of the radio group.

    **titles** A list of titles to be shown next to the radio buttons.

    **isVertical** Boolean representing if the radio group is
    vertical or horizontal.

    **callback** The method to be caled when a radio button is selected.

    **sizeStyle** A string representing the desired size style of the radio group.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsMatrixClass = NSMatrix
    nsCellClass = NSButtonCell

    def __init__(self, posSize, titles, isVertical=True, callback=None, sizeStyle="regular"):
        self._setupView(self.nsMatrixClass, posSize, callback=callback)
        self._isVertical = isVertical
        matrix = self._nsObject
        matrix.setMode_(NSRadioModeMatrix)
        matrix.setCellClass_(self.nsCellClass)
        # XXX! this does not work for vertical radio groups!
        matrix.setAutosizesCells_(True)
        # we handle the control size setting here
        # since the actual NS object is a NSMatrix
        cellSizeStyle = _sizeStyleMap[sizeStyle]
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(cellSizeStyle))
        # intercell spacing and cell spacing are based on the sizeStyle
        if sizeStyle == "regular":
            matrix.setIntercellSpacing_((4.0, 2.0))
            matrix.setCellSize_((posSize[2], 18))
        elif sizeStyle == "small":
            matrix.setIntercellSpacing_((3.5, 2.0))
            matrix.setCellSize_((posSize[2], 15))
        elif sizeStyle == "mini":
            matrix.setIntercellSpacing_((3.0, 2.0))
            matrix.setCellSize_((posSize[2], 12))
        else:
            raise ValueError("sizeStyle must be 'regular', 'small' or 'mini'")
        for x in range(len(titles)):
            if isVertical:
                matrix.addRow()
            else:
                matrix.addColumn()
        for title, cell in zip(titles, matrix.cells()):
            cell.setButtonType_(NSRadioButton)
            cell.setTitle_(title)
            cell.setControlSize_(cellSizeStyle)
            cell.setFont_(font)

    def _testForDeprecatedAttributes(self):
        super(RadioGroup, self)._testForDeprecatedAttributes()
        from warnings import warn
        if hasattr(self, "_cellClass"):
            warn(DeprecationWarning("The _cellClass attribute is deprecated. Use the nsCellClass attribute."))
            self.nsCellClass = self._cellClass

    def getNSMatrix(self):
        """
        Return the *NSMatrix* that this object wraps.
        """
        return self._nsObject

    def get(self):
        """
        Get the index of the selected radio button.
        """
        if self._isVertical:
            return self._nsObject.selectedRow()
        else:
            return self._nsObject.selectedColumn()

    def set(self, index):
        """
        Set the index of the seleced radio button.
        """
        if self._isVertical:
            row = index
            column = 0
        else:
            row = 0
            column = index
        self._nsObject.selectCellAtRow_column_(row, column)
