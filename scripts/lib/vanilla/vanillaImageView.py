from AppKit import *
from vanillaBase import VanillaBaseObject

_imageAlignmentMap = {
    ("center", "center") : NSImageAlignCenter,
    ("left", "center") : NSImageAlignLeft,
    ("right", "center") : NSImageAlignRight,
    ("center", "top") : NSImageAlignTop,
    ("left", "top") : NSImageAlignTopLeft,
    ("right", "top") : NSImageAlignTopRight,
    ("center", "bottom") : NSImageAlignBottom,
    ("left", "bottom") : NSImageAlignBottomLeft,
    ("right", "bottom") : NSImageAlignBottomRight
}

_imageScaleMap = {
    "proportional" : NSScaleProportionally,
    "none" : NSScaleNone,
    "fit" : NSScaleToFit
}


class ImageView(VanillaBaseObject):

    """
    A view that displays an image.

    **posSize** Tuple of form *(left, top, width, height)* representing
    the position and size of the view.

    **horizontalAlignment** A string representing the desired horizontal
    alignment of the image in the view. The options are:

    +-------------+-------------------------+
    | "left"      | Image is aligned left.  |
    +-------------+-------------------------+
    | "right"     | Image is aligned right. |
    +-------------+-------------------------+
    | "center"    | Image is centered.      |
    +-------------+-------------------------+

    **verticalAlignment** A string representing the desired vertical alignment
    of the image in the view. The options are:

    +-------------+--------------------------+
    | "top"       | Image is aligned top.    |
    +-------------+--------------------------+
    | "bottom"    | Image is aligned bottom. |
    +-------------+--------------------------+
    | "center"    | Image is centered.       |
    +-------------+--------------------------+

    **scale** A string representing the desired scale style of the image in the
    view. The options are:

    +----------------+----------------------------------------------+
    | "porportional" | Proportionally scale the image to fit in the |
    |                | view if it is larger than the view.          |
    +----------------+----------------------------------------------+
    | "fit"          | Distort the proportions of the image until   |
    |                | it fits exactly in the view.                 |
    +----------------+----------------------------------------------+
    | "none"         | Do not scale the image.                      |
    +----------------+----------------------------------------------+
    """

    nsImageViewClass = NSImageView

    def __init__(self, posSize, horizontalAlignment="center", verticalAlignment="center", scale="proportional"):
        self._setupView(self.nsImageViewClass, posSize)
        align = _imageAlignmentMap[(horizontalAlignment, verticalAlignment)]
        self._nsObject.setImageAlignment_(align)
        scale = _imageScaleMap[scale]
        self._nsObject.setImageScaling_(scale)

    def getNSImageView(self):
        """
        Return the *NSImageView* that this object wraps.
        """
        return self._nsObject

    def setImage(self, imagePath=None, imageNamed=None, imageObject=None):
        """
        Set the image in the view.

        **imagePath** A file path to an image.

        **imageNamed** The name of an image already load as a *NSImage*
        by the application.

        **imageObject** A *NSImage* object.

        *Only one of imagePath, imageNamed, imageObject should be set.*
        """
        if imagePath is not None:
            image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        else:
            raise ValueError, "no image source defined"
        self._nsObject.setImage_(image)
