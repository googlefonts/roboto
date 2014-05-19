from AppKit import *
from vanillaBase import VanillaBaseObject, _sizeStyleMap


class ProgressSpinner(VanillaBaseObject):

    """
    An animated, spinning progress indicator.::

        from vanilla import *

        class ProgressSpinnerDemo(object):

            def __init__(self):
                self.w = Window((80, 52))
                self.w.spinner = ProgressSpinner((24, 10, 32, 32),
                                        displayWhenStopped=True)
                self.w.spinner.start()
                self.w.open()

        ProgressSpinnerDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing the
    position and size of the spinner. The size of the spinner sould match the
    appropriate value for the given *sizeStyle*.

    +---------------------------+
    | **Standard Dimensions**   |
    +---------+---+----+---+----+
    | Regular | W | 32 | H | 32 |
    +---------+---+----+---+----+
    | Small   | W | 16 | H | 16 |
    +---------+---+----+---+----+

    **displayWhenStopped** Boolean representing if the spiiner should be
    displayed when it is not spinning.

    **sizeStyle** A string representing the desired size style of the spinner.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    """

    nsProgressIndicatorClass = NSProgressIndicator

    def __init__(self, posSize, displayWhenStopped=False, sizeStyle="regular"):
        self._setupView(self.nsProgressIndicatorClass, posSize)
        sizeStyle = _sizeStyleMap[sizeStyle]
        self._nsObject.setControlSize_(sizeStyle)
        self._nsObject.setStyle_(NSProgressIndicatorSpinningStyle)
        self._nsObject.setDisplayedWhenStopped_(displayWhenStopped)

    def getNSProgressIndicator(self):
        """
        Return the *NSProgressIndicator* that this object wraps.
        """
        return self._nsObject

    def start(self):
        """
        Start the animation.
        """
        self._nsObject.startAnimation_(None)

    def stop(self):
        """
        Stop the animation.
        """
        self._nsObject.stopAnimation_(None)
