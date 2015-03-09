import weakref
from copy import deepcopy

from robofab.pens.pointPen import AbstractPointPen
from defcon.pens.clockwiseTestPointPen import ClockwiseTestPointPen

from booleanOperationManager import BooleanOperationManager

manager = BooleanOperationManager()

class BooleanGlyphDataPointPen(AbstractPointPen):

    def __init__(self, glyph):
        self._glyph = glyph
        self._points = []
        self.copyContourData = True

    def _flushContour(self):
        points = self._points
        if len(points) == 1 and points[0][0] == "move":
            self._glyph.anchors.append((pt, name))
        elif self.copyContourData:
            contour = self._glyph.contourClass()
            contour._points = points
            self._glyph.contours.append(contour)

    def beginPath(self):
        self._points = []

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
        self._points.append((segmentType, pt, smooth, name))

    def endPath(self):
        self._flushContour()

    def addComponent(self, baseGlyphName, transformation):
        self._glyph.components.append((baseGlyphName, transformation))

class BooleanContour(object):

    """
    Contour like object.
    """

    def __init__(self):
        self._points = []
        self._clockwise = None
        self._bounds = None

    def __len__(self):
        return len(self._points)

    ## shallow contour API

    def draw(self, pen):
        from robofab.pens.adapterPens import PointToSegmentPen
        pointPen = PointToSegmentPen(pen)
        self.drawPoints(pointPen)

    def drawPoints(self, pointPen):
        pointPen.beginPath()
        for segmentType, pt, smooth, name in self._points:
            pointPen.addPoint(pt=pt, segmentType=segmentType, smooth=smooth, name=name)
        pointPen.endPath()

    def _get_clockwise(self):
        if self._clockwise is None:
            pointPen = ClockwiseTestPointPen()
            self.drawPoints(pointPen)
            self._clockwiseCache = pointPen.getIsClockwise()
        return self._clockwise

    clockwise = property(_get_clockwise)

    def _get_bounds(self):
        if self._bounds is None:
            from robofab.pens.boundsPen import BoundsPen
            pen = BoundsPen(None)
            self.draw(pen)
            self._boundsCache = pen.bounds
        return self._bounds

    bounds = property(_get_bounds)

class BooleanGlyph(object):
    
    """
    Glyph like object handling boolean operations.
    
    union:
        result = BooleanGlyph(glyph).union(BooleanGlyph(glyph2))
        result = BooleanGlyph(glyph) | BooleanGlyph(glyph2)
    
    difference:
        result = BooleanGlyph(glyph).difference(BooleanGlyph(glyph2))
        result = BooleanGlyph(glyph) % BooleanGlyph(glyph2)
    
    intersection:
        result = BooleanGlyph(glyph).intersection(BooleanGlyph(glyph2))
        result = BooleanGlyph(glyph) & BooleanGlyph(glyph2)
    
    xor:
        result = BooleanGlyph(glyph).xor(BooleanGlyph(glyph2))
        result = BooleanGlyph(glyph) ^ BooleanGlyph(glyph2)
    
    """
    
    contourClass = BooleanContour

    def __init__(self, glyph=None, copyContourData=True):
        self.contours = []
        self.components = []
        self.anchors = []
        
        self.name = None
        self.unicodes = None
        self.width = None
        self.lib = {}
        self.note = None

        if glyph:
            pen = self.getPointPen()
            pen.copyContourData = copyContourData
            glyph.drawPoints(pen)
            
            self.name = glyph.name
            self.unicodes = glyph.unicodes
            self.width = glyph.width
            self.lib = deepcopy(glyph.lib)
            self.note = glyph.note

            if not isinstance(glyph, self.__class__):
                self.getSourceGlyph = weakref.ref(glyph)
    
    def __repr__(self):
        return "<BooleanGlyph %s>" % self.name

    def __len__(self):
        return len(self.contours)

    def __getitem__(self, index):
        return self.contours[index]

    def getSourceGlyph(self):
        return None
    
    ## shalllow glyph API

    def draw(self, pen):
        from robofab.pens.adapterPens import PointToSegmentPen
        pointPen = PointToSegmentPen(pen)
        self.drawPoints(pointPen)
    
    def drawPoints(self, pointPen):
        for contour in self.contours:
            contour.drawPoints(pointPen)
        for baseName, transformation in self.components:
            pointPen.addComponent(baseName, transformation)
        for pt, name in self.anchors:
            pointPen.beginPath()
            pointPen.addPoint(pt=pt, segmentType="move", smooth=False, name=name)
            pointPen.endPath()
    
    def getPen(self):
        from robofab.pens.adapterPens import SegmentToPointPen
        return SegmentToPointPen(self.getPointPen())

    def getPointPen(self):
        from defcon.pens.glyphObjectPointPen import GlyphObjectPointPen
        return BooleanGlyphDataPointPen(self)

    ## boolean operations

    def _booleanMath(self, operation, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        destination = self.__class__(self, copyContourData=False)
        func = getattr(manager, operation)

        if operation == "union":
            contours = self.contours
            if other is not None:
                contours += other.contours
            func(contours, destination.getPointPen())    
        else:
            subjectContours = self.contours
            clipContours = other.contours
            func(subjectContours, clipContours, destination.getPointPen())
        return destination
    
    def __or__(self, other):
        return self.union(other)
    
    __ror__ = __ior__ = __or__

    def __mod__(self, other):
        return self.difference(other)

    __rmod__ = __imod__ = __mod__

    def __and__(self, other):
        return self.intersection(other)
    
    __rand__ = __iand__ = __and__

    def __xor__(self, other):
        return self.xor(other)

    __rxor__ = __ixor__ = __xor__

    def union(self, other):
        return self._booleanMath("union", other)

    def difference(self, other):
        return self._booleanMath("difference", other)

    def intersection(self, other):
        return self._booleanMath("intersection", other)

    def xor(self, other):
        return self._booleanMath("xor", other)

    def removeOverlap(self):
        return self._booleanMath("union", None)

