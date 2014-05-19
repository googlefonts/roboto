"""
This is adapted from the PyObjC PythonBrowser demo.
I beleive that demo was written by Just van Rossum.
"""


from Foundation import NSObject
from AppKit import *
from operator import getitem, setitem
from types import NoneType
import sys
from vanillaBase import VanillaBaseObject
from nsSubclasses import getNSSubclass


TYPE_COLUMN_MAP = {
    "list" : "",
    "dict" : "",
    "NoneType" : "None",
    "instance" : "",
    "int" : "Integer",
    "float" : "Float",
    "str" : "String",
}

class ObjectBrowser(VanillaBaseObject):

    """
    An object browser.

    **posSize** Tuple of form *(left, top, width, height)* representing the position and
    size of the browser.

    **obj** The object to be displayed.
    """

    def __init__(self, posSize, obj):
        self._model = PythonBrowserModel.alloc().initWithObject_(obj)

        self._posSize = posSize

        self._nsObject = getNSSubclass("NSScrollView")(self)
        self._nsObject.setAutohidesScrollers_(True)
        self._nsObject.setHasHorizontalScroller_(True)
        self._nsObject.setHasVerticalScroller_(True)
        self._nsObject.setBorderType_(NSBezelBorder)
        self._nsObject.setDrawsBackground_(True)

        self._outlineView = getNSSubclass("NSOutlineView")(self)
        self._outlineView.setFrame_(((0, 0), (100, 100)))
        self._outlineView.setUsesAlternatingRowBackgroundColors_(True)
        self._outlineView.setRowHeight_(17.0)

        self._outlineView.setColumnAutoresizingStyle_(NSTableViewUniformColumnAutoresizingStyle)
        columns = [
            ("name", "Name"),
            ("type", "Type"),
            ("value", "Value")
        ]
        for key, title in columns:
            column = NSTableColumn.alloc().initWithIdentifier_(key)
            column.setResizingMask_(NSTableColumnAutoresizingMask)
            column.headerCell().setTitle_(title)
            dataCell = column.dataCell()
            dataCell.setDrawsBackground_(False)
            dataCell.setStringValue_("") # cells have weird default values
            column.setEditable_(False)
            self._outlineView.addTableColumn_(column)
            if key == "name":
                self._outlineView.setOutlineTableColumn_(column)

        self._outlineView.setDataSource_(self._model)
        self._outlineView.setDelegate_(self._model)

        self._nsObject.setDocumentView_(self._outlineView)
        self._setAutosizingFromPosSize(posSize)

    def getNSScrollView(self):
        return self._nsObject

    def getNSOutlineView(self):
        return self._outlineView


class PythonBrowserModel(NSObject):

    """This is a delegate as well as a data source for NSOutlineViews."""

    def initWithObject_(self, obj):
        self = self.init()
        self.setObject_(obj)
        return self

    def setObject_(self, obj):
        self.root = PythonItem("<root>", obj, None, None)

    # NSOutlineViewDataSource  methods

    def outlineView_numberOfChildrenOfItem_(self, view, item):
        if item is None:
            item = self.root
        return len(item)

    def outlineView_child_ofItem_(self, view, child, item):
        if item is None:
            item = self.root
        return item.getChild(child)

    def outlineView_isItemExpandable_(self, view, item):
        if item is None:
            item = self.root
        return item.isExpandable()

    def outlineView_objectValueForTableColumn_byItem_(self, view, col, item):
        if item is None:
            item = self.root
        identifier = col.identifier()
        value = getattr(item, identifier)
        # filter the type values
        if identifier == "type":
            value = TYPE_COLUMN_MAP.get(value, value)
        return value

    def outlineView_shouldEditTableColumn_item_(self, view, col, item):
        return False


# objects of these types are not eligable for expansion in the outline view
SIMPLE_TYPES = (str, unicode, int, long, float, complex)


def getInstanceVarNames(obj):
    """Return a list the names of all (potential) instance variables."""
    # Recipe from Guido
    slots = {}
    if hasattr(obj, "__dict__"):
        slots.update(obj.__dict__)
    if hasattr(obj, "__class__"):
        slots["__class__"] = 1
    cls = getattr(obj, "__class__", type(obj))
    if hasattr(cls, "__mro__"):
        for base in cls.__mro__:
            for name, value in base.__dict__.items():
                # XXX using callable() is a heuristic which isn"t 100%
                # foolproof.
                if hasattr(value, "__get__") and not callable(value) and \
                        hasattr(obj, name):
                    slots[name] = 1
    if "__dict__" in slots:
        del slots["__dict__"]
    slots = slots.keys()
    slots = [i for i in slots if not i.startswith("_")]
    slots.sort()
    return slots


class NiceError:

    """Wrapper for an exception so we can display it nicely in the browser."""

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def __repr__(self):
        from traceback import format_exception_only
        lines = format_exception_only(*self.exc_info[:2])
        assert len(lines) == 1
        error = lines[0].strip()
        return "*** error *** %s" %error


class PythonItem(NSObject):

    """Wrapper class for items to be displayed in the outline view."""

    # We keep references to all child items (once created). This is
    # neccesary because NSOutlineView holds on to PythonItem instances
    # without retaining them. If we don"t make sure they don"t get
    # garbage collected, the app will crash. For the same reason this
    # class _must_ derive from NSObject, since otherwise autoreleased
    # proxies will be fed to NSOutlineView, which will go away too soon.

    def __new__(cls, *args, **kwargs):
        # "Pythonic" constructor
        return cls.alloc().init()

    def __init__(self, name, obj, parent, setvalue):
        self.realName = name
        self.name = str(name)
        self.parent = parent
        self._setValue = setvalue
        self.type = type(obj).__name__
        if obj is None:
            self.value = "None"
        elif not isinstance(obj, SIMPLE_TYPES):
            self.value = ""
        else:
            self.value = obj
        self.object = obj
        self.childrenEditable = 0
        if isinstance(obj, dict):
            self.children = obj.keys()
            self.children.sort()
            self._getChild = getitem
            self._setChild = setitem
            self.childrenEditable = 1
        elif obj is None or isinstance(obj, SIMPLE_TYPES):
            self._getChild = None
            self._setChild = None
        elif isinstance(obj, (list, tuple)):
            self.children = range(len(obj))
            self._getChild = getitem
            self._setChild = setitem
            if isinstance(obj, list):
                self.childrenEditable = 1
        else:
            self.children = getInstanceVarNames(obj)
            self._getChild = getattr
            self._setChild = setattr
            self.childrenEditable = 1  # XXX we don"t know that...
        self._childRefs = {}

    def setValue(self, value):
        self._setValue(self.parent, self.realName, value)
        self.__init__(self.realName, value, self.parent, self._setValue)

    def isEditable(self):
        return self._setValue is not None

    def isExpandable(self):
        return self._getChild is not None

    def getChild(self, child):
        if self._childRefs.has_key(child):
            return self._childRefs[child]

        name = self.children[child]
        try:
            obj = self._getChild(self.object, name)
        except:
            obj = NiceError(sys.exc_info())
        if self.childrenEditable:
            childObj = PythonItem(name, obj, self.object, self._setChild)
        else:
            childObj = PythonItem(name, obj, None, None)
        self._childRefs[child] = childObj
        return childObj

    def __len__(self):
        return len(self.children)
