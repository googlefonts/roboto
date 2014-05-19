from AppKit import *
from vanilla import Window as _Window
from vanilla import List as _List
from vanilla import PopUpButton as _PopUpButton
from vanilla import TextBox, EditText, Button, CheckBox, HorizontalLine, VerticalLine
from defconAppKit.controls.glyphLineView import GlyphLineView as _GlyphLineView
from defconAppKit.controls.glyphView import GlyphView as _GlyphView
from defconAppKit.tools.textSplitter import splitText


__all__ = ['ModalDialog', 'Button', 'TextBox', 'EditText', 'PopUpButton', 'List', 'CheckBox', 'HorizontalLine', 'VerticalLine', 'GlyphView', 'GlyphLineView']


def _getCurrentFont():
    # hack around CurrentFont incompatibilities
    from robofab.world import CurrentFont as RoboFabCurrentFont
    font = RoboFabCurrentFont()
    if font is not None:
        return font
    try:
        font = CurrentFont()
        return font
    except NameError:
        pass
    return None

def _getCurrentGlyph():
    # hack around CurrentGlyph incompatibilities
    from robofab.world import CurrentGlyph as RoboFabCurrentGlyph
    glyph = RoboFabCurrentGlyph()
    if glyph is not None:
        return glyph
    try:
        glyph = CurrentGlyph()
        return glyph
    except NameError:
        pass
    return None


class ModalDialog(_Window):

    nsWindowLevel = NSModalPanelWindowLevel

    def __init__(self, posSize, title=None, okText="OK", cancelText="Cancel", okCallback=None, cancelCallback=None):
        if title is None:
            title = ''
        super(ModalDialog, self).__init__(posSize, title, minSize=None, maxSize=None,
                textured=False, autosaveName=None, closable=False)
        window = self.getNSWindow()
        self._window.standardWindowButton_(NSWindowCloseButton).setHidden_(True)       
        self._window.standardWindowButton_(NSWindowZoomButton).setHidden_(True)
        self._window.standardWindowButton_(NSWindowMiniaturizeButton).setHidden_(True)
        #
        self._okCallback = okCallback
        self._cancelCallback = cancelCallback
        #
        self._bottomLine = HorizontalLine((10, -50, -10, 1))
        self._okButton = Button((-85, -35, 70, 20), okText, callback=self._internalOKCallback)
        self._cancelButton = Button((-165, -35, 70, 20), cancelText, callback=self._internalCancelCallback)
        self.setDefaultButton(self._okButton)
        self._cancelButton.bind('.', ['command'])
        if len(posSize) == 2:
            self.center()

    def open(self):
        super(ModalDialog, self).open()
        NSApp().runModalForWindow_(self.getNSWindow())

    def close(self):
        super(ModalDialog, self).close()
        NSApp().stopModal()

    def _internalOKCallback(self, sender):
        self.close()
        if self._okCallback is not None:
            self._okCallback(self)

    def _internalCancelCallback(self, sender):
        self.close()
        if self._cancelCallback is not None:
            self._cancelCallback(self)


class List(_List):

    def __init__(self, posSize, items, callback=None):
        super(List, self).__init__(posSize, items=items, selectionCallback=callback)


class PopUpButton(_PopUpButton):

    def setSelection(self, value):
        super(PopUpButton, self).set(value)

    def getSelection(self):
        return super(PopUpButton, self).get()


class GlyphLineView(_GlyphLineView):

    def __init__(self, posSize, text="", font=None, rightToLeft=False):
        if font is None:
            font = _getCurrentFont()
        self._font = font
        self._setText = None
        super(GlyphLineView, self).__init__(
            posSize, pointSize=None, rightToLeft=rightToLeft,
            autohideScrollers=True, showPointSizePlacard=False
        )
        #self.setFont(font)

    def set(self, text):
        glyphNames = splitText(text, self._font.getCharacterMapping())
        # this assumes that the naked glyph will be defcon based.
        # the only other option is to fork the defocnAppKit code to use only RoboFab objects.
        glyphs = [self._font[glyphName].naked() for glyphName in glyphNames if glyphName in self._font]
        super(GlyphLineView, self).set(glyphs)

    def get(self):
        return self._setText

    def setFont(self, font):
        self._font = font
        self.set(self._setText)


class GlyphView(_GlyphView):

    def __init__(self, posSize, font, glyph, margin=30,
        showFill=True, showOutline=False,
        showDescender=True, showBaseline=True, showXHeight=True,
        showAscender=True, showCapHeight=True, showUPMTop=False,
        showLeftSidebearing=True, showRightSidebearing=True,
        showOnCurvePoints=True):
        super(GlyphView, self).__init__(posSize)
        self.setShowFill(showFill)
        self.setShowOutline(showOutline)
        self.setShowDescender(showDescender)
        self.setShowBaseline(showBaseline)
        self.setShowXHeight(showXHeight)
        self.setShowAscender(showAscender)
        self.setShowCapHeight(showCapHeight)
        self.setShowUPMTop(showUPMTop)
        self.setShowLeftSidebearing(showLeftSidebearing)
        self.setShowRightSidebearing(showRightSidebearing)
        self.setShowOnCurvePoints(showOnCurvePoints)
        self.setMargin(margin)
        self.set(font, glyph)

    def set(self, font, glyph):
        if glyph is None:
            glyph = _getCurrentGlyph()
        if glyph is not None:
            glyph = glyph.naked()
        super(GlyphView, self).set(glyph)

    ###

    def getShowOutline(self):
        return super(GlyphView, self).getShowStroke()

    def setShowOutline(self, value):
        super(GlyphView, self).setShowStroke(value)

    def getMargin(self):
        return 0

    def setMargin(self, value):
        pass

    def getShowDescender(self):
        return self.getShowMetrics()

    def setShowDescender(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowBaseline(self):
        return self.getShowMetrics()

    def setShowBaseline(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowXHeight(self):
        return self.getShowMetrics()

    def setShowXHeight(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowAscender(self):
        return self.getShowMetrics()

    def setShowAscender(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowCapHeight(self):
        return self.getShowMetrics()

    def setShowCapHeight(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowUPMTop(self):
        return self.getShowMetrics()

    def setShowUPMTop(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowLeftSidebearing(self):
        return self.getShowMetrics()

    def setShowLeftSidebearing(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    def getShowRightSidebearing(self):
        return self.getShowMetrics()

    def setShowRightSidebearing(self, value):
        self.setShowMetrics(value)
        self.setShowMetricsTitles(value)

    ###

    def update(self):
        # defconAppKit automatically updates
        pass
