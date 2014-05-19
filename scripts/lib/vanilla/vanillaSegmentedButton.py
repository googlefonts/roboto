from AppKit import *
from vanillaBase import VanillaBaseControl


_trackingModeMap = {
    "one": NSSegmentSwitchTrackingSelectOne,
    "any": NSSegmentSwitchTrackingSelectAny,
    "momentary": NSSegmentSwitchTrackingMomentary,
}


class SegmentedButton(VanillaBaseControl):

    nsSegmentedControlClass = NSSegmentedControl
    nsSegmentedCellClass = NSSegmentedCell

    frameAdjustments = {
        "mini": (0, -1, 0, 1), #15
        "small": (-2, -4, 2, 5), #20
        "regular": (0, -4, 0, 5), #24
        }

    def __init__(self, posSize, segmentDescriptions, callback=None, selectionStyle="one", sizeStyle="small"):
        self._setupView(self.nsSegmentedControlClass, posSize)
        if self.nsSegmentedCellClass != NSSegmentedCell:
            self._nsObject.setCell_(self.nsSegmentedCellClass.alloc().init())
        if callback is not None:
            self._setCallback(callback)
        self._setSizeStyle(sizeStyle)
        nsObject = self._nsObject
        nsObject.setSegmentCount_(len(segmentDescriptions))
        nsObject.cell().setTrackingMode_(_trackingModeMap[selectionStyle])
        for segmentIndex, segmentDescription in enumerate(segmentDescriptions):
            width = segmentDescription.get("width", 0)
            title = segmentDescription.get("title", "")
            enabled = segmentDescription.get("enabled", True)
            imagePath = segmentDescription.get("imagePath")
            imageNamed = segmentDescription.get("imageNamed")
            imageObject = segmentDescription.get("imageObject")
            # create the NSImage if needed
            if imagePath is not None:
                image = NSImage.alloc().initWithContentsOfFile_(imagePath)
            elif imageNamed is not None:
                image = NSImage.imageNamed_(imageNamed)
            elif imageObject is not None:
                image = imageObject
            else:
                image = None
            nsObject.setWidth_forSegment_(width, segmentIndex)
            nsObject.setLabel_forSegment_(title, segmentIndex)
            nsObject.setEnabled_forSegment_(enabled, segmentIndex)
            if image is not None:
                nsObject.setImage_forSegment_(image, segmentIndex)

    def getNSSegmentedButton(self):
        return self._nsObject

    def enable(self, value):
        for index in xrange(self._nsObject.segmentCount()):
            self._nsObject.setEnabled_forSegment_(value, index)

    def set(self, value):
        # value should be an int unless we are in "any" mode
        if self._nsObject.cell().trackingMode() != _trackingModeMap["any"]:
            value = [value]
        for index in xrange(self._nsObject.segmentCount()):
            state = index in value
            self._nsObject.setSelected_forSegment_(state, index)

    def get(self):
        states = []
        for index in xrange(self._nsObject.segmentCount()):
            state = self._nsObject.isSelectedForSegment_(index)
            if state:
                states.append(index)
        if self._nsObject.cell().trackingMode() != _trackingModeMap["any"]:
            return states[0]
        return states
