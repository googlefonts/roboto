import os
import objc
from AppKit import NSImage

d = os.path.dirname(__file__)
p = os.path.join(d, "RBSplitView.framework")

objc.loadBundle("RBSplitView", globals(), objc.pathForFramework(p))
objc.loadBundle("RBSplitSubview", globals(), objc.pathForFramework(p))

thumb = NSImage.alloc().initWithContentsOfFile_(os.path.join(d, "Thumb8.png"))
thumb.setName_("RBSplitViewThumb8")
