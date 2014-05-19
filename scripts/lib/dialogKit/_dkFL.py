"""
Known Issues:
-------------
- GlyphLineView does not properly handle fonts that are not saved to a file.
  this is because there is not good way to find the font index for a given font
  and the preview control requires a font index. so, the best thing i can
  do at this point is get the font index by comparing file paths.
- GlyphView only works with the first master in a multiple master font.
  Dealing with multiple masters is a pain, so I have no plans for fixing this.
"""

import os
import weakref
from FL import *


__all__ = ['ModalDialog', 'Button', 'TextBox', 'EditText', 'PopUpButton', 'List', 'CheckBox', 'GlyphLineView', 'GlyphView', 'HorizontalLine', 'VerticalLine']


osName = os.name
if osName == 'possix':
    osName = 'mac'


class ModalDialog(object):

    def __init__(self, posSize, title=None, okText="OK", cancelText="Cancel", okCallback=None, cancelCallback=None):
        self._dialog = Dialog(self)
        if len(posSize) == 2:
            x, y = posSize
            self._dialog.size = Point(x, y)
            self._dialog.Center()
            self._size = (x, y)
        else:
            x, y, w, h = posSize
            self._dialog.rectangle = Rect(x, y, x+w, y+h)
            self._size = (w, h)
        if title is None:
            title = ''
        self._dialog.title = title
        self._dialog.ok = okText
        self._dialog.cancel = cancelText
        #
        self._okCallback=okCallback
        self._cancelCallback=cancelCallback
    
    def __setattr__(self, attr, value):
        if isinstance(value, UIBaseObject):
            assert not hasattr(self, attr), "attribute '%s' can not be replaced" % attr
            #
            value._contentID = 'contentID_for_' + attr
            # hack for canvas controls:
            # FL requires that custom controls begin with '_'
            if isinstance(value, _CanvasWrapper):
                value._contentID = '_' + value._contentID
            #
            value._setDialog(self)
            value._setupContent()
            #
            x, y, w, h = value._posSize
            # convert posSize to Dialog coordinates
            winW, winH = self._size
            if x < 0:
                l = winW + x
            else:
                l = x
            #
            if w <= 0:
                r = winW + w
            else:
                r = l + w
            #
            if y < 0:
                t = winH + y
            else:
                t = y
            #
            if h <= 0:
                b = winH + h
            else:
                b = t + h
            #
            # _CanvasWrapper needs to know the rect size
            # when it is painting, so store it.
            value._rectSize = (r-l, b-t)
            #
            pos = Rect(l, t, r, b)
            self._dialog.AddControl(value._type, pos, value._contentID, value._style, value._title)
            #
            # it doesn't matter if the value does not have a callback
            # assigned. the _callbackWrapper method safely handles
            # those cases. the reason it is not handled here is that
            # custom controls (used by _CanvasWrapper) use the method 
            # normally reserved for control hits to paint the control.
            setattr(self, 'on_%s' % value._contentID, value._callbackWrapper)
        super(ModalDialog, self).__setattr__(attr, value)        
    
    def open(self):
        """open the dialog"""
        self._dialog.Run()
    
    def close(self):
        """close the dialog"""
        self._dialog.End()
    
    def on_cancel(self, code):
        if self._cancelCallback is not None:
            self._cancelCallback(self)
    
    def on_ok(self, code):
        if self._okCallback is not None:
            self._okCallback(self)


class UIBaseObject(object):
    
    def __init__(self, posSize, title, callback=None, content=None):
        self._posSize = posSize
        self._title = title
        self._callback = callback
        self._content = content

    def _setDialog(self, dialog):
        self._dialog = weakref.ref(dialog)
    
    def _callbackWrapper(self, code):
        if self._callback is not None:
            self._callback(self)
    
    def _setupContent(self):
        # set the attribute data in the parent class.
        # this will be used for GetValue and PutValue operations.
        setattr(self._dialog(), self._contentID, self._content)
    
    def enable(self, value):
        """
        enable the object by passing True
        disable the object by passing False
        """
        value = int(value)
        dialog = self._dialog()
        dialog._dialog.Enable(self._contentID, value)
    
    def show(self, value):
        """
        show the object by passing True
        hide the object by passing False
        """
        dialog = self._dialog()
        dialog._dialog.Show(self._contentID, value)
    
    def set(self, value):
        """
        set the content of the object
        """
        # temporarily suspend the callback
        # bacause FontLab 5 calls the method
        # assigned to a control when the
        # control value is set programatically
        callback = self._callback
        self._callback = None
        # set the ccontent
        self._content = value
        dialog = self._dialog()
        setattr(dialog, self._contentID, value)
        dialog._dialog.PutValue(self._contentID)
        # reset the callback
        self._callback = callback
    
    def get(self):
        """
        return the contents of the object
        """
        dialog = self._dialog()
        dialog._dialog.GetValue(self._contentID)
        self._content = getattr(dialog, self._contentID)
        return self._content
    

class Button(UIBaseObject):
    
    _type = BUTTONCONTROL
    _style = STYLE_BUTTON
    
    def __init__(self, posSize, title, callback=None):
        super(Button, self).__init__(posSize=posSize, title=title, callback=callback, content=title)
    
    def set(self, value):
        """
        Not implemented for Button
        """
        raise NotImplementedError, "It is not possible to set the text in a button"


class PopUpButton(UIBaseObject):
    
    _type = CHOICECONTROL
    _style = STYLE_CHOICE
    
    def __init__(self, posSize, items, callback=None):
        super(PopUpButton, self).__init__(posSize=posSize, title='', callback=callback, content=items)
    
    def _setupContent(self):
        super(PopUpButton, self)._setupContent()
        self._contentIndexID = self._contentID + '_index'
        self.setSelection(0)
    
    def setSelection(self, value):
        """
        set the selected item
        value should be an index
        """
        # temporarily suspend the callback
        callback = self._callback
        self._callback = None
        # set the value
        if value is None:
            value = -1
        dialog = self._dialog()
        setattr(dialog, self._contentIndexID, value)
        dialog._dialog.PutValue(self._contentID)
        # reset the callback
        self._callback = callback
    
    def getSelection(self):
        """
        return the index of the selected item
        """
        dialog = self._dialog()
        dialog._dialog.GetValue(self._contentID)
        getattr(dialog, self._contentID)
        index = getattr(dialog, self._contentIndexID)
        if index == -1:
            index = None
        return index


class List(UIBaseObject):
    
    _type = LISTCONTROL
    _style = STYLE_LIST
    
    def __init__(self, posSize, items, callback=None):
        super(List, self).__init__(posSize=posSize, title='', callback=callback, content=items)

    def _setupContent(self):
        super(List, self)._setupContent()
        self._contentIndexID = self._contentID + '_index'
        self.setSelection([0])

    def __len__(self):
        return len(self._content)
    
    def __getitem__(self, index):
        return self._content[index]
    
    def __setitem__(self, index, value):
        self._content[index] = value
        self.set(self._content)
    
    def __delitem__(self, index):
        del self._content[index]
        self.set(self._content)

    def __getslice__(self, a, b):
        return self._content[a:b]

    def __delslice__(self, a, b):
        del self._content[a:b]
        self.set(self._content)

    def __setslice__(self, a, b, items):
        self._content[a:b] = items
        self.set(self._content)

    def append(self, item):
        self._content.append(item)
        self.set(self._content)

    def remove(self, item):
        index = self._content.index(item)
        del self._content[index]
        self.set(self._content)

    def index(self, item):
        return self._content.index(item)

    def insert(self, index, item):
        self._content.insert(index, item)
        self.set(self._content)

    def extend(self, items):
        self._content.extend(items)
        self.set(self._content)

    def replace(self, index, item):
        del self._content[index]
        self._content.insert(index, item)
        self.set(self._content)
    
    #
    
    def setSelection(self, value):
        """
        set the selected item index(es)
        value should be a list of indexes
        
        in FontLab, it setting multiple
        selection indexes is not possible.
        """
        dialog = self._dialog()
        if len(value) < 1:
            value = -1
        else:
            value = value[0]
        setattr(dialog, self._contentIndexID, value)
        dialog._dialog.PutValue(self._contentID)
    
    def getSelection(self):
        """
        return a list of selected item indexes
        """
        dialog = self._dialog()
        dialog._dialog.GetValue(self._contentID)
        getattr(dialog, self._contentID)
        index = getattr(dialog, self._contentIndexID)
        if index == -1:
            return []
        return [index]
    
    def set(self, value):
        """
        set the contents of the list
        """
        self._content = value
        dialog = self._dialog()
        setattr(dialog, self._contentID, value)
        dialog._dialog.PutValue(self._contentID)
    
    def get(self):
        """
        return the contents of the list
        """
        return self._content


class EditText(UIBaseObject):
    
    _type = EDITCONTROL
    _style = STYLE_EDIT
    
    def __init__(self, posSize, text="", callback=None):
        super(EditText, self).__init__(posSize=posSize, title='', callback=callback, content=text)
    
    def set(self, value):
        if osName == 'mac':
            value = '\r'.join(value.splitlines())
        super(EditText, self).set(value)


class TextBox(UIBaseObject):
    
    _type = STATICCONTROL
    _style = STYLE_LABEL
    
    def __init__(self, posSize, text):
        super(TextBox, self).__init__(posSize=posSize, title=text, callback=None, content=text)

    def set(self, value):
        if osName == 'mac':
            value = '\r'.join(value.splitlines())
        super(TextBox, self).set(value)
        

class CheckBox(UIBaseObject):
    
    _type = CHECKBOXCONTROL
    _style = STYLE_CHECKBOX
    
    def __init__(self, posSize, title, callback=None, value=False):
        value = int(value)
        super(CheckBox, self).__init__(posSize=posSize, title=title, callback=callback, content=value)

    def set(self, value):
        """
        set the state of the object
        value should be a boolean
        """
        value = int(value)
        super(CheckBox, self).set(value)
    
    def get(self):
        """
        returns a boolean representing the state of the object
        """
        value = super(CheckBox, self).get()
        return bool(value)


class _CanvasWrapper(UIBaseObject):

    _type = STATICCONTROL
    _style = STYLE_CUSTOM

    def __init__(self, posSize):
        super(_CanvasWrapper, self).__init__(posSize=posSize, title='', callback=None, content=None)

    def _callbackWrapper(self, canvas):
        # oddly, the custom control is painted
        # by the method that would normally be
        # called when the control is hit.
        self._paint(canvas)


class _Line(_CanvasWrapper):

    def __init__(self, posSize):
        super(_Line, self).__init__(posSize=posSize)

    def _paint(self, canvas):
        canvas.brush_color = cRGB_GRAY
        canvas.brush_style = cBRUSH_SOLID
        canvas.draw_style = 1
        #
        w, h = self._rectSize
        r = Rect(0, 0, w, h)
        canvas.Rectangle(0, r)

class HorizontalLine(_Line):

    def __init__(self, posSize):
        x, y, w, h = posSize
        super(HorizontalLine, self).__init__(posSize=(x, y, w, 1))

class VerticalLine(_Line):

    def __init__(self, posSize):
        x, y, w, h = posSize
        super(VerticalLine, self).__init__(posSize=(x, y, 1, h))


def _unwrapRobofab(obj):
    # this could be a raw FontLab object or a robofab object.
    # the preference is for raw FontLab objects. this
    # function safely unwraps robofab objects.
    try:
        from robofab.world import RFont, RGlyph
        haveRobofab = True
    except ImportError:
        haveRobofab = False
    if haveRobofab:
        if isinstance(obj, RFont) or isinstance(obj, RGlyph):
            return obj.naked()
    return obj

def _fontIndex(font):
    font = _unwrapRobofab(font)
    #
    fonts = [(fl[i], i) for i in xrange(len(fl))]
    #
    for otherFont, index in fonts:
        if otherFont.file_name == font.file_name: # grrr.
            return index
    return -1


class GlyphLineView(UIBaseObject):
    
    _type = PREVIEWCONTROL
    _style = STYLE_LABEL
    
    def __init__(self, posSize, text="", font=None, rightToLeft=False):
        if font is None:
            self._fontIndex = fl.ifont
        else:
            self._fontIndex = _fontIndex(font)
        self._rightToLeft = False
        text = self._makeText(text)
        super(GlyphLineView, self).__init__(posSize=posSize, title="", callback=None, content=text)
    
    def _makeText(self, text):
        text = "f:%d|d:%s|r:%d" % (self._fontIndex, text, self._rightToLeft)
        return text
    
    def set(self, text):
        """
        set the text displayed text string
        """
        text = self._makeText(text)
        super(GlyphLineView, self).set(text)
    
    def get(self):
        """
        return the displayed text string
        """
        return self._content[6:-4]
    
    def setFont(self, font):
        """
        set the index for the font that should be displayed
        """
        if font is None:
            self._fontIndex = -1
        else:
            self._fontIndex = _fontIndex(font)
        self.set(self.get())
    
    def setRightToLeft(self, value):
        """
        set the setting directon of the display
        """
        self._rightToLeft = value
        self.set(self.get())


class GlyphView(_CanvasWrapper):
    
    def __init__(self, posSize, font, glyph, margin=30,
        showFill=True, showOutline=False,
        showDescender=True, showBaseline=True, showXHeight=True,
        showAscender=True, showCapHeight=True, showUPMTop=False,
        showLeftSidebearing=True, showRightSidebearing=True,
        showOnCurvePoints=True):
        #
        super(GlyphView, self).__init__(posSize=posSize)
        #
        self._showFill = showFill
        self._showOutline = showOutline
        self._margin = margin
        self._showDescender = showDescender
        self._showBaseline = showBaseline
        self._showXHeight = showXHeight
        self._showAscender = showAscender
        self._showCapHeight = showCapHeight
        self._showUPMTop = showUPMTop
        self._showLeftSidebearing = showLeftSidebearing
        self._showRightSidebearing = showRightSidebearing
        #
        self._showOnCurvePoints = showOnCurvePoints
        #
        self.set(font, glyph)
    
    def set(self, font, glyph):
        """
        change the glyph displayed in the view
        """
        if font is None or glyph is None:
            self._font = None
            self._glyph = None
        else:
            self._font = _unwrapRobofab(font)
            self._glyph = _unwrapRobofab(glyph)
    
    ###

    def getShowFill(self):
        return self._showFill

    def setShowFill(self, value):
        self._showFill = value

    def getShowOutline(self):
        return self._showOutline

    def setShowOutline(self, value):
        self._showOutline = value

    def getMargin(self):
        return self._margin

    def setMargin(self, value):
        self._margin = value

    def getShowDescender(self):
        return self._showDescender

    def setShowDescender(self, value):
        self._showDescender = value

    def getShowBaseline(self):
        return self._showBaseline

    def setShowBaseline(self, value):
        self._showBaseline = value

    def getShowXHeight(self):
        return self._showXHeight

    def setShowXHeight(self, value):
        self._showXHeight = value

    def getShowAscender(self):
        return self._showAscender

    def setShowAscender(self, value):
        self._showAscender = value

    def getShowCapHeight(self):
        return self._showCapHeight

    def setShowCapHeight(self, value):
        self._showCapHeight = value

    def getShowUPMTop(self):
        return self._showUPMTop

    def setShowUPMTop(self, value):
        self._showUPMTop = value

    def getShowLeftSidebearing(self):
        return self._showLeftSidebearing

    def setShowLeftSidebearing(self, value):
        self._showLeftSidebearing = value

    def getShowRightSidebearing(self):
        return self._showRightSidebearing

    def setShowRightSidebearing(self, value):
        self._showRightSidebearing = value

    def getShowOnCurvePoints(self):
        return self._showOnCurvePoints

    def setShowOnCurvePoints(self, value):
        self._showOnCurvePoints = value

    ###
    
    def update(self):
        if hasattr(self, '_dialog'):
            dialog = self._dialog()
            dialog._dialog.Repaint(self._contentID)
    
    def _paint(self, canvas):
        if self._font is None or self._glyph is None:
            return
        font = self._font
        glyph = self._glyph
        #
        upm = font.upm
        descender = font.descender[0]
        baseline = 0
        xHeight = font.x_height[0]
        ascender = font.ascender[0]
        capHeight = font.cap_height[0]
        #
        glyphWidth = glyph.width
        #
        viewWidth, viewHeight = self._rectSize
        liveWidth = viewWidth - (self._margin * 2)
        liveHeight = viewHeight - (self._margin * 2)
        #
        scale = liveHeight / float(upm)
        #
        xOffset = (viewWidth - (glyphWidth * scale)) / 2
        yOffset = ((upm + descender) * scale) + self._margin
        #
        left = -xOffset * (1.0 / scale)
        right = glyphWidth + abs(left)
        top = upm + descender + (self._margin * (1.0 / scale))
        bottom = descender - (self._margin * (1.0 / scale))
        #
        canvas.delta = Point(xOffset, yOffset)
        canvas.scale = Point(scale, -scale)
        #
        canvas.pen_color = cRGB_LTGRAY
        #
        if self._showDescender:
            canvas.MoveTo(Point(left, descender))
            canvas.LineTo(Point(right, descender))
        if self._showBaseline:
            canvas.MoveTo(Point(left, baseline))
            canvas.LineTo(Point(right, baseline))
        if self._showXHeight:
            canvas.MoveTo(Point(left, xHeight))
            canvas.LineTo(Point(right, xHeight))
        if self._showAscender:
            canvas.MoveTo(Point(left, ascender))
            canvas.LineTo(Point(right, ascender))
        if self._showCapHeight:
            canvas.MoveTo(Point(left, capHeight))
            canvas.LineTo(Point(right, capHeight))
        if self._showUPMTop:
            canvas.MoveTo(Point(left, upm+descender))
            canvas.LineTo(Point(right, upm+descender))
        #
        if self._showLeftSidebearing:
            canvas.MoveTo(Point(0, bottom))
            canvas.LineTo(Point(0, top))
        if self._showRightSidebearing:
            canvas.MoveTo(Point(glyphWidth, bottom))
            canvas.LineTo(Point(glyphWidth, top))
        #
        if self._showFill:
            canvas.FillGlyph(glyph)
            canvas.OutlineGlyph(glyph)  # XXX hack to hide gray outline
        if self._showOutline:
            canvas.OutlineGlyph(glyph)
        #
        if self._showOnCurvePoints:
            canvas.pen_color = cRGB_RED
            canvas.brush_color = cRGB_RED
            markerSize = 5 * (1.0 / scale)
            halfMarkerSize = markerSize / 2
            for node in glyph.nodes:
                x, y = node.x, node.y
                x -= halfMarkerSize
                y -= halfMarkerSize
                if node.alignment == nSMOOTH:
                    mode = 1
                else:
                    mode = 0
                canvas.Rectangle(mode, Rect(x, y, x+markerSize, y+markerSize))
