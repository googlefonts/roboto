from AppKit import *
from vanillaBase import VanillaBaseObject, _breakCycles, _sizeStyleMap, VanillaCallbackWrapper, \
        _reverseSizeStyleMap


class VanillaTabItem(VanillaBaseObject):

    nsTabViewItemClass = NSTabViewItem

    def __init__(self, title):
        self._tabItem = self.nsTabViewItemClass.alloc().initWithIdentifier_(title)
        self._tabItem.setLabel_(title)

    def _getContentView(self):
        return self._tabItem.view()

    def _breakCycles(self):
        _breakCycles(self._tabItem.view())


class VanillaTabsDelegate(NSObject):

    def tabView_didSelectTabViewItem_(self, tabView, tabViewItem):
        if hasattr(self, "_target"):
            self._target.action_(tabView.vanillaWrapper())


class Tabs(VanillaBaseObject):

    """
    A drawer attached to a window. Drawers are capable of containing controls.

    To add a control to a tab, simply set it as an attribute of the tab.::

        from vanilla import *

        class TabDemo(object):

            def __init__(self):
                self.w = Window((250, 100))
                self.w.tabs = Tabs((10, 10, -10, -10), ["Tab One", "Tab Two"])
                tab1 = self.w.tabs[0]
                tab1.text = TextBox((10, 10, -10, -10), "This is tab 1")
                tab2 = self.w.tabs[1]
                tab2.text = TextBox((10, 10, -10, -10), "This is tab 2")
                self.w.open()

        TabDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    To retrieve a particular tab, access it by index:::

        myTab = self.w.tabs[0]


    **posSize** Tuple of form *(left, top, width, height)* representing the position
    and size of the tabs.

    **titles** An ordered list of tab titles.

    **callback** The method to be called when the user selects a new tab.

    **sizeStyle** A string representing the desired size style of the tabs.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsTabViewClass = NSTabView
    vanillaTabViewItemClass = VanillaTabItem

    allFrameAdjustments = {
        # The sizeStyle will be part of the
        # className used for the lookup here.
        "Tabs-mini": (-7, -10, 14, 12),
        "Tabs-small": (-7, -10, 14, 13),
        "Tabs-regular": (-7, -10, 14, 16),
    }

    def __init__(self, posSize, titles=["Tab"], callback=None, sizeStyle="regular", showTabs=True):
        self._setupView(self.nsTabViewClass, posSize) # hold off on setting callback
        self._setSizeStyle(sizeStyle)
        self._tabItems = []
        for title in titles:
            tab = self.vanillaTabViewItemClass(title)
            self._tabItems.append(tab)
            self._nsObject.addTabViewItem_(tab._tabItem)
        if not showTabs:
            self._nsObject.setTabViewType_(NSNoTabsNoBorder)
            self._nsObject.setDrawsBackground_(False)
        # now that the tabs are all set, set the callback.
        # this is done because the callback will be called
        # while the tabs are being added.
        if callback is not None:
            self._setCallback(callback)

    def getNSTabView(self):
        """
        Return the *NSTabView* that this object wraps.
        """
        return self._nsObject

    def _adjustPosSize(self, frame):
        if self._nsObject.tabViewType() == NSNoTabsNoBorder:
            return frame
        sizeStyle = _reverseSizeStyleMap[self._nsObject.controlSize()]
        tabsType = "Tabs-" + sizeStyle
        self.frameAdjustments = self.allFrameAdjustments[tabsType]
        return super(Tabs, self)._adjustPosSize(frame)

    def _setCallback(self, callback):
        if callback is not None:
            self._target = VanillaCallbackWrapper(callback)
            delegate = self._nsObject.delegate()
            if delegate is None:
                self._delegate = delegate = VanillaTabsDelegate.alloc().init()
                self._nsObject.setDelegate_(delegate)
            delegate._target = self._target

    def _setSizeStyle(self, value):
        value = _sizeStyleMap[value]
        self._nsObject.setControlSize_(value)
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(value))
        self._nsObject.setFont_(font)

    def __getitem__(self, index):
        return self._tabItems[index]

    def _breakCycles(self):
        super(Tabs, self)._breakCycles()
        for item in self._tabItems:
            item._breakCycles()

    def get(self):
        """
        Get the index of the selected tab.
        """
        item = self._nsObject.selectedTabViewItem()
        index = self._nsObject.indexOfTabViewItem_(item)
        return index

    def set(self, value):
        """
        Set the selected tab.

        **value** The index of the tab to be selected.
        """
        self._nsObject.selectTabViewItemAtIndex_(value)
