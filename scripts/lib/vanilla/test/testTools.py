from AppKit import *
from PyObjCTools import AppHelper


class _VanillaMiniAppDelegate(NSObject):

    def applicationShouldTerminateAfterLastWindowClosed_(self, notification):
        return True


def executeVanillaTest(cls, **kwargs):
    """
    Execute a Vanilla UI class in a mini application.
    """
    app = NSApplication.sharedApplication()
    delegate = _VanillaMiniAppDelegate.alloc().init()
    app.setDelegate_(delegate)
    cls(**kwargs)
    app.activateIgnoringOtherApps_(True)
    AppHelper.runEventLoop()

