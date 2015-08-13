#! /usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Converts a cubic bezier curve to a quadratic spline with 
exactly two off curve points.

"""

from math import sqrt

from numpy import array
from fontTools.misc import bezierTools
from robofab.objects.objectsRF import RSegment

def replaceSegments(contour, segments):
    while len(contour):
        contour.removeSegment(0)
    for s in segments:
        contour.appendSegment(s.type, [(p.x, p.y) for p in s.points], s.smooth)


def lerp(p1, p2, t):
    """Linearly interpolate between p1 and p2 at time t."""
    return p1 * (1 - t) + p2 * t


def extend(p1, p2, n):
    """Return the point extended from p1 in the direction of p2 scaled by n."""
    return p1 + (p2 - p1) * n


def dist(p1, p2):
    """Calculate the distance between two points."""
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def bezierAt(p, t):
    """Return the point on a bezier curve at time t."""

    n = len(p)
    if n == 1:
        return p[0]
    return lerp(bezierAt(p[:n - 1], t), bezierAt(p[1:n], t), t)


def cubicApprox(p, t):
    """Approximate a cubic bezier curve with a quadratic one."""

    p1 = extend(p[0], p[1], 1.5)
    p2 = extend(p[3], p[2], 1.5)
    return [p[0], lerp(p1, p2, t), p[3]]


def cubicApproxContour(p, n):
    """Approximate a cubic bezier curve with a contour of n quadratics."""

    contour = [p[0]]
    ts = [(float(i) / n) for i in range(1, n)]
    segments = [
        map(array, segment)
        for segment in bezierTools.splitCubicAtT(p[0], p[1], p[2], p[3], *ts)]
    for i in range(len(segments)):
        segment = cubicApprox(segments[i], float(i) / (n - 1))
        contour.append(segment[1])
    contour.append(p[3])
    return contour


def curveContourDist(bezier, contour):
    """Max distance between a bezier and quadratic contour at sampled ts."""

    TOTAL_STEPS = 20
    error = 0
    n = len(contour) - 2
    steps = TOTAL_STEPS / n
    for i in range(1, n + 1):
        segment = [
            contour[0] if i == 1 else segment[2],
            contour[i],
            contour[i + 1] if i == n else lerp(contour[i], contour[i + 1], 0.5)]
        for j in range(steps):
            p1 = bezierAt(bezier, (float(j) / steps + i - 1) / n)
            p2 = bezierAt(segment, float(j) / steps)
            error = max(error, dist(p1, p2))
    return error


def convertToQuadratic(p0,p1,p2,p3):
    MAX_N = 10
    MAX_ERROR = 10
    p = [array([i.x, i.y]) for i in [p0, p1, p2, p3]]
    for n in range(2, MAX_N + 1):
        contour = cubicApproxContour(p, n)
        if curveContourDist(p, contour) <= MAX_ERROR:
            break
    return contour


def cubicSegmentToQuadratic(c,sid):
    
    segment = c[sid]
    if (segment.type != "curve"):
        print "Segment type not curve"
        return
    
    #pSegment,junk = getPrevAnchor(c,sid)
    pSegment = c[sid-1] #assumes that a curve type will always be proceeded by another point on the same contour
    points = convertToQuadratic(pSegment.points[-1],segment.points[0],
                                segment.points[1],segment.points[2])
    return RSegment(
        'qcurve', [[int(i) for i in p] for p in points[1:]], segment.smooth)

def glyphCurvesToQuadratic(g):

    for c in g:
        segments = []
        for i in range(len(c)):
            s = c[i]
            if s.type == "curve":
                try:
                    segments.append(cubicSegmentToQuadratic(c, i))
                except Exception:
                    print g.name, i
                    raise
            else:
                segments.append(s)
        replaceSegments(c, segments)
