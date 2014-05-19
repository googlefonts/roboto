import time
import os
import sys
from AppKit import *
import vanilla
reload(vanilla)
from vanilla import *
#from RBSplitView.vanillaRBSplitView import VRBSplitView as SplitView

import objc
objc.setVerbose(True)

vanillaPath = os.path.dirname(os.path.dirname(os.path.dirname(vanilla.__file__)))
iconPath = os.path.join(vanillaPath, "Data", "testIcon.tif")

sizeStyles = ["regular", "small", "mini"]

listOptions = sys.modules.keys()
sortedListOptions = list(listOptions)
sortedListOptions.sort()

class BaseTest(object):

    def drawGrid(self):
        w, h = self.w.getPosSize()[2:]
        increment = 10
        for i in xrange(int(w/increment)):
            if i == 0:
                continue
            attrName = "vline%d" % i
            line = VerticalLine((increment*i, 0, 1, h))
            setattr(self.w, attrName, line)
        for i in xrange(int(h/increment)):
            if i == 0:
                continue
            attrName = "hline%d" % i
            line = HorizontalLine((0, increment*i, w, 1))
            setattr(self.w, attrName, line)

    def basicCallback(self, sender):
        print sender

    def titleCallback(self, sender):
        print sender, sender.getTitle()

    def getCallback(self, sender):
        print sender, sender.get()


class WindowTest(BaseTest):

    def __init__(self, textured=False):
        self.textured = textured
        self.w = Window((200, 130), "Window Test", textured=textured)
        self.w.windowButton = Button((10, 10, -10, 20), "Window", callback=self.windowCallback)
        self.w.sheetButton = Button((10, 40, -10, 20), "Sheet", callback=self.sheetCallback)
        self.w.drawerButton = Button((10, 70, -10, 20), "Drawer", callback=self.drawerCallback)
        self.w.floatButton = Button((10, 100, -10, 20), "Floating Window", callback=self.floatCallback)
        self.w.open()

    def windowCallback(self, sender):
        WindowTest(not self.textured)

    def sheetCallback(self, sender):
        self.sheet = Sheet((300, 100), self.w)
        self.sheet.closeButton = Button((10, -30, -10, 20), "Close", callback=self._closeSheet)
        self.sheet.open()

    def _closeSheet(self, sender):
        self.sheet.close()
        del self.sheet

    def drawerCallback(self, sender):
        if not hasattr(self, "drawer1"):
            self.drawer1 = Drawer((50, 50), self.w, preferredEdge="left")
            self.drawer2 = Drawer((50, 50), self.w, preferredEdge="top")
            self.drawer3 = Drawer((50, 50), self.w, preferredEdge="right")
            self.drawer4 = Drawer((50, 50), self.w, preferredEdge="bottom")
        self.drawer1.toggle()
        self.drawer2.toggle()
        self.drawer3.toggle()
        self.drawer4.toggle()

    def floatCallback(self, sender):
        floater = FloatingWindow((100, 100))
        floater.open()


class TextTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((440, 190), "Text Test")

        _top = 10
        top = _top

        textSizeStyles = [("regular", 17), ("small", 14), ("mini", 11)]
        for sizeStyle, height in textSizeStyles:
            attrName = "TextBox_%s" % sizeStyle
            button = TextBox((10, top, 100, height), attrName, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        textSizeStyles = [("regular", 22), ("small", 19), ("mini", 15)]
        for sizeStyle, height in textSizeStyles:
            attrName = "SearchBox_%s" % sizeStyle
            button = SearchBox((10, top, 100, height), attrName, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        top = _top
        textSizeStyles = [("regular", 22), ("small", 19), ("mini", 16)]
        for sizeStyle, height in textSizeStyles:
            attrName = "EditText_%s" % sizeStyle
            button = EditText((120, top, 100, height), attrName, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        textSizeStyles = [("regular", 21), ("small", 17), ("mini", 14)]
        for sizeStyle, height in textSizeStyles:
            attrName = "ComboBox_%s" % sizeStyle
            button = ComboBox((120, top, 100, height), items=listOptions, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        self.w.TextEditor = TextEditor((240, 10, 190, 170), sys.copyright, callback=self.getCallback)

        if drawGrid:
            self.drawGrid()

        self.w.open()


class ButtonTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((440, 800), "Button Test")

        _top = 10
        top = _top

        buttonSizeStyles = [("regular", 20), ("small", 17), ("mini", 14)]
        for sizeStyle, height in buttonSizeStyles:
            attrName = "Button_%s" % sizeStyle
            button = Button((10, top, 150, height), attrName, callback=self.titleCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        height = 20
        for sizeStyle in sizeStyles:
            attrName = "SquareButton_%s" % sizeStyle
            button = SquareButton((10, top, 150, height), attrName, callback=self.titleCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        settings = [(None, False, "top"),
                    (None, True, "top"),
                    ("bop", True, "top"),
                    ("bop", True, "bottom"),
                    ("bop", True, "left"),
                    ("bop", True, "right"),]
        for title, bordered, imagePosition in settings:
            attrName = "ImageButton_%s_%s_%s" % (title, bordered, imagePosition)
            button = ImageButton((10, top, 150, 50), title=title, imagePath=iconPath, bordered=bordered, imagePosition=imagePosition, callback=self.basicCallback)
            setattr(self.w, attrName, button)
            top += 60

        segmentedControlSizeStyles = [("regular", 20), ("small", 17), ("mini", 14)]
        descriptions = [{"title":"One"}, {"title":"Two"}, {"title":"3", "enabled":False}]
        for sizeStyle, height in segmentedControlSizeStyles:
            attrName = "SegmentedButton_%s" % sizeStyle
            button = SegmentedButton((10, top, 150, height), descriptions, callback=None, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        top = _top
        _left = 170
        left = _left
        height = 100

        sliderSizeStyles = [("regular", 15), ("small", 11), ("mini", 10)]
        for sizeStyle, width in sliderSizeStyles:
            attrName = "VSlider_noTicks_%s" % sizeStyle
            button = Slider((left, top, width, height), 0, 100, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            left += 30
        sliderSizeStyles = [("regular", 23), ("small", 17), ("mini", 16)]
        for sizeStyle, width in sliderSizeStyles:
            attrName = "VSlider_rightTicks_%s" % sizeStyle
            button = Slider((left, top, width, height), 0, 100, tickMarkCount=10, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            left += 30
        for sizeStyle, width in sliderSizeStyles:
            attrName = "VSlider_leftTicks_%s" % sizeStyle
            button = Slider((left, top, width, height), 0, 100, tickMarkCount=10, callback=self.getCallback, sizeStyle=sizeStyle)
            button.setTickMarkPosition("left")
            setattr(self.w, attrName, button)
            left += 30

        left = _left
        width = 260
        top = 130
        sliderSizeStyles = [("regular", 15), ("small", 12), ("mini", 10)]
        for sizeStyle, height in sliderSizeStyles:
            attrName = "HSlider_noTicks_%s" % sizeStyle
            button = Slider((left, top, width, height), 0, 100, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30
        sliderSizeStyles = [("regular", 24), ("small", 17), ("mini", 16)]
        for sizeStyle, height in sliderSizeStyles:
            attrName = "HSlider_belowTicks_%s" % sizeStyle
            button = Slider((left, top, width, height), 0, 100, tickMarkCount=30, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30
        for sizeStyle, height in sliderSizeStyles:
            attrName = "HSlider_aboveTicks_%s" % sizeStyle
            button = Slider((left, top, width, height), 0, 100, tickMarkCount=30, callback=self.getCallback, sizeStyle=sizeStyle)
            button.setTickMarkPosition("top")
            setattr(self.w, attrName, button)
            top += 30

        _top = top

        popupSizeStyles = [("regular", 20), ("small", 17), ("mini", 15)]
        width = 120
        for sizeStyle, height in popupSizeStyles:
            attrName = "PopUpButton_%s" % sizeStyle
            button = PopUpButton((left, top, width, height), listOptions, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        top = _top
        checkboxSizeStyles = [("regular", 22), ("small", 18), ("mini", 11)]
        width = 125
        left = 300
        for sizeStyle, height in popupSizeStyles:
            attrName = "CheckBox_%s" % sizeStyle
            button = CheckBox((left, top, width, height), attrName, callback=self.getCallback, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        _top = top

        left = _left
        width = 120
        self.w.DLevelIndicator = LevelIndicator((left, top, width, 18), style="discrete",
                    value=5, warningValue=7, criticalValue=9,
                    callback=self.getCallback)
        top += 30
        self.w.DLevelIndicator_ticksAbove = LevelIndicator((left, top, width, 25), style="discrete",
                    value=5, warningValue=7, criticalValue=9,
                    tickMarkPosition="above", minorTickMarkCount=5, majorTickMarkCount=3, callback=self.getCallback)
        top += 30
        self.w.DLevelIndicator_ticksBelow = LevelIndicator((left, top, width, 25), style="discrete",
                    value=5, warningValue=7, criticalValue=9,
                    tickMarkPosition="below", minorTickMarkCount=5, majorTickMarkCount=3, callback=self.getCallback)

        left = 300
        top = _top
        width = 120
        self.w.CLevelIndicator = LevelIndicator((left, top, width, 16), style="continuous",
                    value=5, warningValue=7, criticalValue=9,
                    callback=self.getCallback)
        top += 30
        self.w.CLevelIndicator_ticksAbove = LevelIndicator((left, top, width, 23), style="continuous",
                    value=5, warningValue=7, criticalValue=9,
                    tickMarkPosition="above", minorTickMarkCount=5, majorTickMarkCount=3, callback=self.getCallback)
        top += 30
        self.w.CLevelIndicator_ticksBelow = LevelIndicator((left, top, width, 23), style="continuous",
                    value=5, warningValue=7, criticalValue=9,
                    tickMarkPosition="below", minorTickMarkCount=5, majorTickMarkCount=3, callback=self.getCallback)

        _top = 660
        top = _top
        pathControlSizeStyles = [("regular", 22), ("small", 20), ("mini", 18)]
        left = 10
        width = -10
        url = NSURL.fileURLWithPath_(__file__)
        for sizeStyle, height in pathControlSizeStyles:
            attrName = "PathControl_%s" % sizeStyle
            button = PathControl((left, top, width, height), url, callback=None, sizeStyle=sizeStyle)
            setattr(self.w, attrName, button)
            top += 30

        if drawGrid:
            self.drawGrid()

        self.w.open()


class ListTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((440, 500), "List Test", minSize=(400, 400))

        simpleList = List((0, 0, 0, 0), listOptions, enableTypingSensitivity=True)

        multiItems = [
            {"name": name, "path": os.path.basename(getattr(module, "__file__", "Unknown"))}
            for name, module in sys.modules.items()
        ]
        columnDescriptions = [
            {"title": "Module Name", "key": "name"},
            {"title": "File Name", "key": "path"}
        ]
        multiList = List((0, 0, 0, 0), multiItems, columnDescriptions=columnDescriptions, enableTypingSensitivity=True)

        miscItems = [
            {"slider": 50, "checkBox": False},
            {"slider": 20, "checkBox": True},
            {"slider": 70, "checkBox": False},
            {"slider": 20, "checkBox": True},
            {"slider": 10, "checkBox": True},
            {"slider": 90, "checkBox": False},
        ]
        columnDescriptions = [
            {"title": "SliderListCell", "key": "slider",
            "cell": SliderListCell()},
            {"title": "CheckBoxListCell", "key": "checkBox",
            "cell": CheckBoxListCell()},
        ]
        miscCellList = List((0, 0, 0, 0), items=miscItems, columnDescriptions=columnDescriptions)

        paneDescriptions = [
            dict(view=simpleList, identifier="simpleList"),
            dict(view=multiList, identifier="multiList"),
            dict(view=miscCellList, identifier="miscCellList"),
        ]

        # only add the ListIndicator tests if the controls are available
        try:
            listIndicatorItems = [
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
            levelIndicatorList = List((0, 0, 0, 0), items=listIndicatorItems, columnDescriptions=columnDescriptions)
            paneDescriptions.append(dict(view=levelIndicatorList, identifier="levelIndicatorList"))
        except NameError:
            pass

        self.w.splitView = SplitView((0, 0, -0, -0), paneDescriptions, isVertical=False)

        if drawGrid:
            self.drawGrid()

        self.w.open()

class BrowserTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((440, 500), "Browser Test", minSize=(400, 400))

        import vanilla
        self.w.browser = ObjectBrowser((0, 0, 0, 0), vanilla)

        if drawGrid:
            self.drawGrid()

        self.w.open()


class TestCustomNSView(NSView):

    def viewDidEndLiveResize(self):
        self._recalcSize()

    def _recalcSize(self):
        # XXX Note that this is specific for embedding in a ScrollView,
        # it may behave strangely when used in another context.
        w, h = self.superview().visibleRect()[1]
        self.setFrame_(((0, 0), (w, h)))

    def drawRect_(self, rect):
        if self.inLiveResize():
            self._recalcSize()
        from random import random
        NSColor.redColor().set()
        NSRectFill(self.bounds())
        width, height = self.frame()[1]
        w = width / 5
        h = height / 5
        for xI in xrange(5):
            for yI in xrange(5):
                x = xI * w
                y = height - (yI * h) - h
                r = ((x, y), (w, h))
                NSColor.colorWithDeviceRed_green_blue_alpha_(random(), random(), random(), 1.0).set()
                NSRectFill(r)


class ViewTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((450, 350), "View Test", minSize=(350, 300))

        self.w.tabs = Tabs((10, 10, 220, 120), ["Small", "Mini"])
        self.w.tabs[0].tabs = Tabs((10, 10, -10, -10), ["One", "Two", "Three"], sizeStyle="small")
        self.w.tabs[1].tabs = Tabs((10, 10, -10, -10), ["One", "Two", "Three"], sizeStyle="mini")

        self.w.box = Box((10, 140, 220, 70), "Box")
        self.w.box.box = Box((10, 10, -10, -10))

        self.scrollViewNSView = TestCustomNSView.alloc().initWithFrame_(((0, 0), (500, 500)))
        self.w.scrollView = ScrollView((240, 10, 200, 200), self.scrollViewNSView, backgroundColor=NSColor.redColor())

        self.splitViewNSView1 = TestCustomNSView.alloc().initWithFrame_(((0, 0), (0, 0)))
        self.splitViewNSView2 = TestCustomNSView.alloc().initWithFrame_(((0, 0), (0, 0)))
        view1 = ScrollView((0, 0, 0, 50), self.splitViewNSView1, autohidesScrollers=True, backgroundColor=NSColor.redColor())
        view2 = ScrollView((0, 0, 0, -10), self.splitViewNSView2, autohidesScrollers=True, backgroundColor=NSColor.redColor())
        paneDescriptions = [
            dict(view=view1, identifier="view1"),
            dict(view=view2, identifier="view2"),
        ]
        self.w.splitView = SplitView((10, 220, -10, -10), paneDescriptions)

        if drawGrid:
            self.drawGrid()

        self.w.open()


class ToolbarTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((350, 20), "Toolbar Test", minSize=(250, 20))

        customView = NSSegmentedControl.alloc().initWithFrame_(((0, 0), (100, 30)))
        cell = customView.cell()
        cell.setTrackingMode_(NSSegmentSwitchTrackingSelectOne)
        cell.setSegmentCount_(2)
        cell.setImage_forSegment_(NSCursor.arrowCursor().image(), 0)
        cell.setImage_forSegment_(NSCursor.crosshairCursor().image(), 1)
        customView.sizeToFit()

        toolbarItems = [
            {"itemIdentifier": "Test Item One",
             "label": "Test One",
             "imagePath": iconPath,
             "callback": self.basicCallback},
            {"itemIdentifier": "Test Item Two",
             "label": "Test Two",
             "imagePath": iconPath,
             "callback": self.basicCallback},
            {"itemIdentifier": "Test Item Three",
             "imagePath": iconPath,
             "callback": self.basicCallback},
            {"itemIdentifier": "Test Item Four",
             "label": "Test Four",
             "view": customView,
             "callback": self.basicCallback},
            {"itemIdentifier": NSToolbarPrintItemIdentifier, "visibleByDefault": False},
            {"itemIdentifier": NSToolbarFlexibleSpaceItemIdentifier},
            {"itemIdentifier": NSToolbarCustomizeToolbarItemIdentifier},
        ]

        self.w.addToolbar("Vanilla Test Toolbar", toolbarItems=toolbarItems)

        self.w.open()


class MiscTest(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((150, 180), "Misc. Test")

        self.w.spinner1 = ProgressSpinner((10, 10, 32, 32), sizeStyle="regular")
        self.w.spinner2 = ProgressSpinner((50, 10, 16, 16), sizeStyle="small")

        self.w.bar1 = ProgressBar((10, 50, -10, 16))
        self.w.bar2 = ProgressBar((10, 70, -10, 10), isIndeterminate=True, sizeStyle="small")

        self.w.progressStartButton = Button((10, 90, -10, 20), "Start Progress", callback=self.startProgress)

        self.w.colorWell = ColorWell((10, 130, -10, -10), callback=self.getCallback, color=NSColor.redColor())

        if drawGrid:
            self.drawGrid()

        self.w.open()

    def startProgress(self, sender):
        self.w.spinner1.start()
        self.w.spinner2.start()
        self.w.bar2.start()
        for i in xrange(10):
            self.w.bar1.increment(10)
            time.sleep(.1)
        time.sleep(.5)
        self.w.spinner1.stop()
        self.w.spinner2.stop()
        self.w.bar2.stop()
        self.w.bar1.set(0)


class _VanillaTestViewForSplitView(NSView):

    def drawRect_(self, rect):
        from AppKit import NSRectFill, NSBezierPath, NSColor
        self.color.set()
        NSRectFill(self.bounds())
        NSColor.blackColor().set()
        p = NSBezierPath.bezierPathWithRect_(self.bounds())
        p.setLineWidth_(10)
        p.stroke()


class TestSplitSubview(VanillaBaseObject):

    def __init__(self, posSize, color):
        self._setupView(_VanillaTestViewForSplitView, posSize)
        self._nsObject.color = color

class TestSplitView(BaseTest):

    def __init__(self, drawGrid=False):
        self.w = Window((600, 500), "", minSize=(300, 250))

        grp = Group((0, 0, 0, 0))
        grp.button = Button((10, 10, -10, 20), "Toggle", self.buttonCallback)

        self.view1 = TestSplitSubview((0, 0, 0, 0), NSColor.redColor())
        paneDescriptions2 = [
            dict(view=self.view1, canCollapse=True, size=50, identifier="pane1"),
            dict(view=grp, identifier="pane2"),
            dict(view=TestSplitSubview((0, 0, 0, 0), NSColor.greenColor()), minSize=50, identifier="pane3"),
            dict(view=TestSplitSubview((0, 0, 0, 0), NSColor.yellowColor()), identifier="pane4"),
        ]
        self.nestedSplit = SplitView((0, 0, 0, 0), paneDescriptions2, isVertical=True)
        paneDescriptions1 = [
            dict(view=self.nestedSplit, identifier="pane5"),
            dict(view=TestSplitSubview((0, 0, 0, 0), NSColor.magentaColor()), minSize=100, size=100, canCollapse=True, identifier="pane6"),
        ]
        self.w.splitView = SplitView((10, 10, -10, -10), paneDescriptions1, isVertical=False)

        if drawGrid:
            self.drawGrid()
        self.w.open()

    def buttonCallback(self, sender):
        self.nestedSplit.togglePane("pane1")


class Test(object):

    def __init__(self):
        self.w = FloatingWindow((200, 300, 120, 340))
        self.w.drawGrid = CheckBox((10, 10, -10, 22), "Draw Grid", value=False)
        self.w.windows = Button((10, 40, -10, 20), "Windows", callback=self.openTestCallback)
        self.w.geometry = Button((10, 70, -10, 20), "Geometry", callback=self.openTestCallback)
        self.w.text = Button((10, 100, -10, 20), "Text", callback=self.openTestCallback)
        self.w.buttons = Button((10, 130, -10, 20), "Buttons", callback=self.openTestCallback)
        self.w.list = Button((10, 160, -10, 20), "List", callback=self.openTestCallback)
        self.w.browser = Button((10, 190, -10, 20), "Browser", callback=self.openTestCallback)
        self.w.view = Button((10, 220, -10, 20), "Views", callback=self.openTestCallback)
        self.w.toolbar = Button((10, 250, -10, 20), "Toolbar", callback=self.openTestCallback)
        self.w.misc = Button((10, 280, -10, 20), "Misc.", callback=self.openTestCallback)
        self.w.split = Button((10, 310, -10, 20), "SplitView", callback=self.openTestCallback)
        self.w.open()

    def openTestCallback(self, sender):
        title = sender.getTitle()
        if title == "Windows":
            WindowTest()
        elif title == "Geometry":
            from vanilla.test.testGeometry import TestGeometry
            TestGeometry()
        elif title == "Text":
            TextTest(self.w.drawGrid.get())
        elif title == "Buttons":
            ButtonTest(self.w.drawGrid.get())
        elif title == "List":
            ListTest(self.w.drawGrid.get())
        elif title == "Browser":
            BrowserTest(self.w.drawGrid.get())
        elif title == "Views":
            ViewTest(self.w.drawGrid.get())
        elif title == "Toolbar":
            ToolbarTest(self.w.drawGrid.get())
        elif title == "Misc.":
            MiscTest(self.w.drawGrid.get())
        elif title == "SplitView":
            TestSplitView(self.w.drawGrid.get())


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
