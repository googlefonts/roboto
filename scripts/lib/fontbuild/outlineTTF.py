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


import time

from fontTools.ttLib import newTable, TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from ufo2fdk.outlineOTF import OutlineOTFCompiler

from fontbuild.ttGlyphPen import TTGlyphPen


class OutlineTTFCompiler(OutlineOTFCompiler):
    """Compiler for a TTF containing just outline data."""

    def compile(self):
        """Compile the TTF."""

        self.ufo.info.openTypeHeadCreated = time.strftime("%Y/%m/%d %H:%M:%S")
        self.otf = TTFont()

        # populate basic tables
        self.setupTable_head()
        self.setupTable_hhea()
        self.setupTable_hmtx()
        self.setupTable_name()
        self.setupTable_maxp()
        self.setupTable_cmap()
        self.setupTable_OS2()
        self.setupTable_post()
        self.setupTable_glyf()
        self.setupOtherTables()

        # write the file
        self.otf.save(self.path)

        # discard the object
        self.otf.close()
        del self.otf

    def setupTable_name(self):
        """Make the name table."""

        font = self.ufo
        nameVals = {
            "0": font.info.copyright,
            "1": font.info.styleMapFamilyName,
            "2": font.info.styleMapStyleName.title(),
            "3": font.info.openTypeNameUniqueID,
            "4": "%s %s" % (font.info.familyName, font.info.styleName),
            "5": font.info.openTypeNameVersion,
            "6": font.info.postscriptFontName,
            "7": font.info.trademark,
            "9": font.info.openTypeNameDesigner,
            "11": font.info.openTypeNameManufacturerURL,
            "12": font.info.openTypeNameDesignerURL,
            "13": font.info.openTypeNameLicense,
            "14": font.info.openTypeNameLicenseURL,
            "16": font.info.openTypeNamePreferredFamilyName,
            "17": font.info.openTypeNamePreferredSubfamilyName}
        nameIds = nameVals.keys()
        nameIds.sort()

        self.otf["name"] = name = newTable("name")
        name.names = []
        for ids in [(1, 0, 0x0), (3, 1, 0x409)]:
            for nameId in nameIds:
                rec = NameRecord()
                rec.platformID, rec.platEncID, rec.langID = ids
                rec.nameID = int(nameId)
                rec.string = nameVals[nameId].encode(rec.getEncoding(), "strict")
                name.names.append(rec)

    def makeOfficialGlyphOrder(self, _):
        """Make the final glyph order."""

        return sorted(self.allGlyphs.keys())

    def setupTable_maxp(self):
        """Make the maxp table."""

        self.otf["maxp"] = maxp = newTable("maxp")
        maxp.tableVersion = 0b10000
        maxp.maxZones = 1
        maxp.maxTwilightPoints = 0
        maxp.maxStorage = 0
        maxp.maxFunctionDefs = 0
        maxp.maxInstructionDefs = 0
        maxp.maxStackElements = 0
        maxp.maxSizeOfInstructions = 0
        maxp.maxComponentElements = max(len(g.components) for g in self.ufo)

    def setupTable_post(self):
        """Make a format 2 post table with the compiler's glyph order."""

        super(OutlineTTFCompiler, self).setupTable_post()
        post = self.otf["post"]
        post.formatType = 2.0
        post.extraNames = []
        post.mapping = {}
        post.glyphOrder = self.glyphOrder

    def setupTable_glyf(self):
        """Make the glyf table."""

        self.otf["loca"] = newTable("loca")
        self.otf["glyf"] = glyf = newTable("glyf")
        glyf.glyphs = {}
        glyf.glyphOrder = self.glyphOrder
        for glyph in self.ufo:
            pen = TTGlyphPen()
            glyph.draw(pen)
            glyf[glyph.name] = pen.glyph()
