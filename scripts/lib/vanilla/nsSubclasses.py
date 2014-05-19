import objc
import weakref


class _VanillaMethods:

    def __new__(cls, wrapper):
        self = cls.alloc().init()
        self.setVanillaWrapper_(wrapper)
        return self

    def setVanillaWrapper_(self, wrapper):
        self._wrapperRef = weakref.ref(wrapper)
        return self

    def vanillaWrapper(self):
        try:
            return self._wrapperRef()
        except AttributeError:
            return None


_subclasses = {}
def getNSSubclass(classOrName=None):
    """
    Return a subclass of a given Objective-C class.
    This subclass allows us to store a weakref to a Vanilla wrapper
    object. This way we can always get back at it. Mainly meant to
    translate "sender" arguments of action methods to a Vanilla object.

    The returned subclass can be instantiated from Python like this:

        >>> class Wrapper(object): pass
        ...
        >>> wrpr = Wrapper()
        >>> view = getNSSubclass("NSBox")(wrpr)
        >>> view.vanillaWrapper() is wrpr
        True

        >>> from Foundation import NSObject
        >>> class MyCustomNSClass(NSObject): pass
        ...
        >>> view = getNSSubclass(MyCustomNSClass)(wrpr)
        >>> view.vanillaWrapper() is wrpr
        True

    """
    subCls = None
    if isinstance(classOrName, basestring):
        cls = objc.lookUpClass(classOrName)
        className = classOrName
    else:
        cls = classOrName
        className = cls.__name__
    subCls = _subclasses.get(className)
    if subCls is None:
        vName = "V" + className
        subCls = cls.__class__(vName, (cls,), _VanillaMethods.__dict__.copy())
        _subclasses[className] = subCls
    return subCls


def _doctest():
    """
        >>> from AppKit import NSTextView
        >>> sc = getNSSubclass('NSTextView')
        >>> sc.__name__
        'VNSTextView'
        >>> issubclass(sc, NSTextView)
        True
        >>> hasattr(sc, 'setVanillaWrapper_')
        True
        >>> hasattr(sc, 'vanillaWrapper')
        True
        >>> # duplicate test to test caching
        >>> sc = getNSSubclass('NSTextView')
        >>> sc.__name__
        'VNSTextView'
        >>> issubclass(sc, NSTextView)
        True
        >>> class Wrapper(object): pass
        ...
        >>> wrpr = Wrapper()
        >>> isinstance(sc(wrpr), NSTextView)
        True
        >>> # test custom class
        >>> from Foundation import NSObject
        >>> class TestClass(NSObject): pass
        ...
        >>> sc = getNSSubclass(TestClass)
        >>> sc.__name__
        'VTestClass'
        >>> isinstance(sc(wrpr), NSObject)
        True
        >>> isinstance(sc(wrpr), TestClass)
        True
        >>> hasattr(sc, 'setVanillaWrapper_')
        True
        >>> hasattr(sc, 'vanillaWrapper')
        True
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
