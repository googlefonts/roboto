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


import ConfigParser
import os
import sys

from booleanOperations import BooleanOperationManager
from cu2qu.rf import fonts_to_quadratic
from fontTools.misc.transform import Transform
from robofab.world import OpenFont
from ufo2ft import compileOTF, compileTTF

from fontbuild.decomposeGlyph import decomposeGlyph
from fontbuild.features import readFeatureFile, writeFeatureFile
from fontbuild.generateGlyph import generateGlyph
from fontbuild.instanceNames import setNamesRF
from fontbuild.italics import italicizeGlyph
from fontbuild.markFeature import RobotoFeatureCompiler, RobotoKernWriter
from fontbuild.mitreGlyph import mitreGlyph
from fontbuild.mix import Mix,Master,narrowFLGlyph


class FontProject:
    
    def __init__(self, basefont, basedir, configfile, thinfont = None):
        self.basefont = basefont
        self.thinfont = thinfont
        self.basedir = basedir
        self.config = ConfigParser.RawConfigParser()
        self.configfile = self.basedir+"/"+configfile
        self.config.read(self.configfile)
        
        diacriticList = open(self.basedir + "/" + self.config.get("res","diacriticfile")).readlines()
        self.diacriticList = [line.strip() for line in diacriticList if not line.startswith("#")]
        self.ot_classes = open(self.basedir + "/" + self.config.get("res","ot_classesfile")).read()
        self.ot_kerningclasses = open(self.basedir + "/" + self.config.get("res","ot_kerningclassesfile")).read()
        #self.ot_features = open(self.basedir + "/" + self.config.get("res","ot_featuresfile")).read()
        adobeGlyphList = open(self.basedir + "/" + self.config.get("res", "agl_glyphlistfile")).readlines()
        self.adobeGlyphList = dict([line.split(";") for line in adobeGlyphList if not line.startswith("#")])
        
        # map exceptional glyph names in Roboto to names in the AGL
        roboNames = (
            ('Obar', 'Ocenteredtilde'), ('obar', 'obarred'),
            ('eturn', 'eturned'), ('Iota1', 'Iotaafrican'))
        for roboName, aglName in roboNames:
            self.adobeGlyphList[roboName] = self.adobeGlyphList[aglName]

        self.builddir = "out"
        self.decompose = self.config.get("glyphs","decompose").split()
        self.predecompose = self.config.get("glyphs","predecompose").split()
        self.lessItalic = self.config.get("glyphs","lessitalic").split()
        self.deleteList = self.config.get("glyphs","delete").split()
        self.noItalic = self.config.get("glyphs","noitalic").split()
        self.buildnumber = self.loadBuildNumber()
        
        self.buildOTF = False
        self.compatible = False
        self.generatedFonts = []
        
        
    def loadBuildNumber(self):
        versionFile = open(self.basedir + "/" + self.config.get("main","buildnumberfile"), "r+")
        buildnumber = int(versionFile.read().strip())
        buildnumber = "%05d" %(int(buildnumber) + 1)
        print "BuildNumber: %s" %(buildnumber)
        versionFile.close()
        return buildnumber
        
    def incrementBuildNumber(self):
        if len(self.buildnumber) > 0:
            versionFile = open(self.basedir + "/" + self.config.get("main","buildnumberfile"), "r+")
            versionFile.seek(0)
            versionFile.write(self.buildnumber)
            versionFile.truncate()
            versionFile.close()
        else:
            raise Exception("Empty build number")

    def generateOutputPath(self, font, ext):
        family = font.info.familyName.replace(" ", "")
        style = font.info.styleName.replace(" ", "")
        path = os.path.join(self.basedir, self.builddir, family + ext.upper())
        if not os.path.exists(path):
            os.makedirs(path)
        return os.path.join(path, "%s-%s.%s" % (family, style, ext))
    
    def generateFont(self, mix, names, italic=False, swapSuffixes=None, stemWidth=185, kern=True):
        
        n = names.split("/")
        log("---------------------\n%s %s\n----------------------" %(n[0],n[1]))
        log(">> Mixing masters")
        if isinstance( mix, Mix):
            f = mix.generateFont(self.basefont)
        else:
            f = mix.copy()
        if italic == True:
            log(">> Italicizing")
            tweakAmmount = .085
            narrowAmmount = .93
            if names.find("Thin") != -1:
                tweakAmmount = .05
            if names.find("Condensed") != -1:
                narrowAmmount = .96
            i = 0
            for g in f:
                i += 1
                if i % 10 == 0: print g.name
                
                if g.name == "uniFFFD":
                    continue

                removeGlyphOverlap(g)

                if g.name in self.lessItalic:
                    italicizeGlyph(f, g, 9, stemWidth=stemWidth)
                elif False == (g.name in self.noItalic):
                    italicizeGlyph(f, g, 10, stemWidth=stemWidth)
                #elif g.name != ".notdef":
                #    italicizeGlyph(g, 10, stemWidth=stemWidth)
                if g.width != 0:
                    g.width += 10

        if swapSuffixes != None:
            for swap in swapSuffixes:
                swapList = [g.name for g in f if g.name.endswith(swap)]
                for gname in swapList:
                    print gname
                    swapContours(f, gname.replace(swap,""), gname)
        for gname in self.predecompose:
            if f.has_key(gname):
                decomposeGlyph(f, gname)

        log(">> Generating glyphs")
        generateGlyphs(f, self.diacriticList, self.adobeGlyphList)
        log(">> Copying features")
        readFeatureFile(f, self.ot_classes + self.basefont.features.text)
        log(">> Decomposing")
        for gname in self.decompose:
            if f.has_key(gname):
                decomposeGlyph(f, gname)

        setNamesRF(f, n, foundry=self.config.get('main', 'foundry'),
                         version=self.config.get('main', 'version'))
        if not self.compatible:
            cleanCurves(f)
        deleteGlyphs(f, self.deleteList)

        if kern:
            log(">> Generating kern classes")
            readFeatureFile(f, self.ot_kerningclasses)

        log(">> Generating font files")
        ufoName = self.generateOutputPath(f, "ufo")
        f.save(ufoName)
        self.generatedFonts.append(ufoName)

        if self.buildOTF:
            log(">> Generating OTF file")
            newFont = OpenFont(ufoName)
            otfName = self.generateOutputPath(f, "otf")
            saveOTF(newFont, otfName)

    def generateTTFs(self):
        """Build TTF for each font generated since last call to generateTTFs."""

        fonts = [OpenFont(ufo) for ufo in self.generatedFonts]
        self.generatedFonts = []

        log(">> Converting curves to quadratic")
        # using a slightly higher max error (e.g. 0.0025 em), dots will have
        # fewer control points and look noticeably different
        max_err = 0.002
        if self.compatible:
            fonts_to_quadratic(fonts, max_err_em=max_err, dump_stats=True)
        else:
            for font in fonts:
                fonts_to_quadratic([font], max_err_em=max_err, dump_stats=True)

        log(">> Generating TTF files")
        for font in fonts:
            ttfName = self.generateOutputPath(font, "ttf")
            log(os.path.basename(ttfName))
            for glyph in font:
                for contour in glyph:
                    contour.reverseContour()
            saveOTF(font, ttfName, truetype=True)


def transformGlyphMembers(g, m):
    g.width = int(g.width * m.a)
    g.Transform(m)
    for a in g.anchors:
        p = Point(a.p)
        p.Transform(m)
        a.p = p
    for c in g.components:
        # Assumes that components have also been individually transformed
        p = Point(0,0)
        d = Point(c.deltas[0])
        d.Transform(m)
        p.Transform(m)
        d1 = d - p
        c.deltas[0].x = d1.x
        c.deltas[0].y = d1.y
        s = Point(c.scale)
        s.Transform(m)
        #c.scale = s

def swapContours(f,gName1,gName2):
    try:
        g1 = f[gName1]
        g2 = f[gName2]
    except KeyError:
        log("swapGlyphs failed for %s %s" % (gName1, gName2))
        return
    g3 = g1.copy()

    while g1.contours:
        g1.removeContour(0)
    for contour in g2.contours:
        g1.appendContour(contour)
    g1.width = g2.width

    while g2.contours:
        g2.removeContour(0)
    for contour in g3.contours:
        g2.appendContour(contour)
    g2.width = g3.width


def log(msg):
    print msg


def generateGlyphs(f, glyphNames, glyphList={}):
    log(">> Generating diacritics")
    glyphnames = [gname for gname in glyphNames if not gname.startswith("#") and gname != ""]
    
    for glyphName in glyphNames:
        generateGlyph(f, glyphName, glyphList)

def cleanCurves(f):
    log(">> Removing overlaps")
    for g in f:
        removeGlyphOverlap(g)

    # log(">> Mitring sharp corners")
    # for g in f:
    #     mitreGlyph(g, 3., .7)
    
    # log(">> Converting curves to quadratic")
    # for g in f:
    #     glyphCurvesToQuadratic(g)


def deleteGlyphs(f, deleteList):
    for name in deleteList:
        if f.has_key(name):
            f.removeGlyph(name)


def removeGlyphOverlap(glyph):
    """Remove overlaps in contours from a glyph."""
    #TODO(jamesgk) verify overlaps exist first, as per library's recommendation
    manager = BooleanOperationManager()
    contours = glyph.contours
    glyph.clearContours()
    manager.union(contours, glyph.getPointPen())


def saveOTF(font, destFile, truetype=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    if truetype:
        compiler = compileTTF
    else:
        compiler = compileOTF
    otf = compiler(font, featureCompilerClass=RobotoFeatureCompiler,
                   kernWriter=RobotoKernWriter)
    otf.save(destFile)
