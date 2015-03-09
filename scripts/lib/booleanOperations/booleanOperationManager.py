from fontTools.pens.basePen import BasePen
from flatten import InputContour, OutputContour
import pyClipper


"""
General Suggestions:
- Contours should only be sent here if they actually overlap.
  This can be checked easily using contour bounds.
- Only perform operations on closed contours.
- contours must have an on curve point
- some kind of a log
"""


class BooleanOperationManager(object):

    def _performOperation(self, operation, subjectContours, clipContours, outPen):
        # prep the contours
        subjectInputContours = [InputContour(contour) for contour in subjectContours if contour and len(contour) > 1]
        clipInputContours = [InputContour(contour) for contour in clipContours if contour and len(contour) > 1]
        inputContours = subjectInputContours + clipInputContours

        resultContours = pyClipper.clipExecute([subjectInputContour.originalFlat for subjectInputContour in subjectInputContours], 
                                               [clipInputContour.originalFlat for clipInputContour in clipInputContours], 
                                               operation, subjectFillType="noneZero", clipFillType="noneZero")
        # convert to output contours
        outputContours = [OutputContour(contour) for contour in resultContours]
        # re-curve entire contour
        for inputContour in inputContours:
            for outputContour in outputContours:
                if outputContour.final:
                    continue
                if outputContour.reCurveFromEntireInputContour(inputContour):
                    # the input is expired if a match was made,
                    # so stop passing it to the outputs
                    break
        # re-curve segments
        for inputContour in inputContours:
            # skip contours that were comppletely used in the previous step
            if inputContour.used:
                continue
            # XXX this could be expensive if an input becomes completely used
            # it doesn't stop from being passed to the output
            for outputContour in outputContours:
                outputContour.reCurveFromInputContourSegments(inputContour)
        # curve fit
        for outputContour in outputContours:
            outputContour.reCurveSubSegments(inputContours)
        # output the results
        for outputContour in outputContours:
            outputContour.drawPoints(outPen)
        return outputContours

    def union(self, contours, outPen):
        return self._performOperation("union", contours, [], outPen)
    
    def difference(self, subjectContours, clipContours, outPen):
        return self._performOperation("difference", subjectContours, clipContours, outPen)
    
    def intersection(self, subjectContours, clipContours, outPen):
        return self._performOperation("intersection", subjectContours, clipContours, outPen)
    
    def xor(self, subjectContours, clipContours, outPen):
        return self._performOperation("xor", subjectContours, clipContours, outPen)

    def getIntersections(self, contours):
        from flatten import _scalePoints, inverseClipperScale
        # prep the contours
        inputContours = [InputContour(contour) for contour in contours if contour and len(contour) > 1]

        inputFlatPoints = set()
        for contour in inputContours:
            inputFlatPoints.update(contour.originalFlat)
        
        resultContours = pyClipper.clipExecute([inputContour.originalFlat for inputContour in inputContours], 
                                               [], 
                                               "union", subjectFillType="noneZero", clipFillType="noneZero")

        resultFlatPoints = set()
        for contour in resultContours:
            resultFlatPoints.update(contour)
        
        intersections = resultFlatPoints - inputFlatPoints
        return _scalePoints(intersections, inverseClipperScale)


    