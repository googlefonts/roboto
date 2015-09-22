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


import array

from fontTools.pens.basePen import AbstractPen
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables._g_l_y_f import GlyphComponent
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates


class TTGlyphPen(AbstractPen):
    """Pen used for drawing to a TrueType glyph."""

    def __init__(self):
        self.points = []
        self.endPts = []
        self.types = []
        self.components = []

    def _addPoint(self, pt, onCurve):
        self.points.append([int(coord) for coord in pt])
        self.types.append(onCurve)

    def lineTo(self, pt):
        self._addPoint(pt, 1)

    def moveTo(self, pt):
        self.lineTo(pt)

    def qCurveTo(self, *points):
        for pt in points[:-1]:
            self._addPoint(pt, 0)
        self._addPoint(points[-1], 1)

    def closePath(self):
        endPt = len(self.points) - 1

        # ignore anchors
        if endPt == 0 or (self.endPts and endPt == self.endPts[-1] + 1):
            self.points.pop()
            self.types.pop()
            return

        self.endPts.append(endPt)

    def endPath(self):
        self.closePath()

    def addComponent(self, glyphName, transformation):
        component = GlyphComponent()
        component.glyphName = glyphName
        component.transform = (transformation[:2], transformation[2:4])
        component.x, component.y = [int(n) for n in transformation[4:]]
        component.flags = 0
        self.components.append(component)

    def glyph(self):
        glyph = Glyph()

        glyph.coordinates = GlyphCoordinates(self.points)
        glyph.endPtsOfContours = self.endPts
        glyph.flags = array.array("B", self.types)
        glyph.components = self.components

        if glyph.components:
            glyph.numberOfContours = -1
        else:
            glyph.numberOfContours = len(glyph.endPtsOfContours)

        glyph.program = ttProgram.Program()
        glyph.program.fromBytecode("")

        return glyph
