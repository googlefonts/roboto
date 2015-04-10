from booleanOperations import BooleanOperationManager
from robofab.world import OpenFont
from fontbuild.mix import Mix,Master,narrowFLGlyph
from fontbuild.instanceNames import setNamesRF
from fontbuild.italics import italicizeGlyph
from fontbuild.convertCurves import glyphCurvesToQuadratic
from fontbuild.mitreGlyph import mitreGlyph
from fontbuild.generateGlyph import generateGlyph
from fontTools.misc.transform import Transform
from fontbuild.features import readFeatureFile, writeFeatureFile
from fontbuild.markFeature import GenerateFeature_mark
from fontbuild.mkmkFeature import GenerateFeature_mkmk
from fontbuild.decomposeGlyph import decomposeGlyph
import ConfigParser
import os


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
        self.ot_kerningfeatures = self.basedir + "/" + self.config.get("res","ot_kerningfeaturesdir")
        adobeGlyphList = open(self.basedir + "/" + self.config.get("res", "agl_glyphlistfile")).readlines()
        self.adobeGlyphList = dict([line.split(";") for line in adobeGlyphList if not line.startswith("#")])
        
        # map exceptional glyph names in Roboto to names in the AGL
        roboNames = (
            ('Obar', 'Ocenteredtilde'), ('obar', 'obarred'),
            ('eturn', 'eturned'), ('Iota1', 'Iotaafrican'))
        for roboName, aglName in roboNames:
            self.adobeGlyphList[roboName] = self.adobeGlyphList[aglName]

        self.builddir = "out/v2"
        self.decompose = self.config.get("glyphs","decompose").split()
        self.predecompose = self.config.get("glyphs","predecompose").split()
        self.lessItalic = self.config.get("glyphs","lessitalic").split()
        self.deleteList = self.config.get("glyphs","delete").split()
        self.buildnumber = self.loadBuildNumber()
        
        self.buildOTF = False
        self.autohintOTF = False
        self.buildTTF = False
        self.buildFEA = False
        
        
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
                    
                # if i < 24:
                #     continue
                # if i > 86:
                #     for i,g in enumerate(fl.font.glyphs):
                #       fl.UpdateGlyph(i)
                #     # break
                #     assert False
                
                # print g.name
                # if self.thinfont != None:
                #                     narrowFLGlyph(g,self.thinfont.getGlyph(g.name),factor=narrowAmmount)
                
                if g.name != "eight" or g.name != "Q":
                    removeGlyphOverlap(g)

                    # not sure why FontLab sometimes refuses, seems to work if called twice

                if g.name in self.lessItalic:
                    italicizeGlyph(f, g, 9, stemWidth=stemWidth)
                elif g.name != ".notdef":
                    italicizeGlyph(f, g, 10, stemWidth=stemWidth)
                removeGlyphOverlap(g)
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
                decomposeGlyph(f[gname])

        log(">> Generating glyphs")
        generateGlyphs(f, self.diacriticList, self.adobeGlyphList)
        log(">> Copying features")
        readFeatureFile(f, self.ot_classes + self.basefont.features.text)
        log(">> Decomposing")
        for gname in self.decompose:
            if f.has_key(gname):
                decomposeGlyph(f[gname])

        setNamesRF(f, n, foundry=self.config.get('main', 'foundry'),
                         version=self.config.get('main', 'version'))
        cleanCurves(f)
        deleteGlyphs(f, self.deleteList)

        if kern:
            log(">> Generating kern classes")
            readFeatureFile(f, self.ot_kerningclasses)
            weight = f.info.styleName.split()[0]
            if weight in ["Light", "Italic"]:
                weight = "Regular"
            elif weight in ["Medium", "Black"]:
                weight = "Bold"
            feature_path = os.path.join(
                self.ot_kerningfeatures, "Roboto-%s.fea" % weight)
            readFeatureFile(f, open(feature_path).read(), prepend=False)

        log(">> Generating font files")
        GenerateFeature_mark(f)
        GenerateFeature_mkmk(f)
        ufoName = self.generateOutputPath(f, "ufo")
        f.save(ufoName)

        if self.buildOTF:
            log(">> Generating OTF file")
            newFont = OpenFont(ufoName)
            otfName = self.generateOutputPath(f, "otf")
            saveOTF(newFont, otfName, autohint=self.autohintOTF)

            if self.buildTTF:
                log(">> Generating TTF file")
                import fontforge
                otFont = fontforge.open(otfName)
                otFont.generate(self.generateOutputPath(f, "ttf"))


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


def saveOTF(font, destFile, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    from ufo2fdk import OTFCompiler

    # glyphs with multiple unicode values must be split up, due to FontTool's
    # use of a name -> UV dictionary during cmap compilation
    for glyph in font:
        if len(glyph.unicodes) > 1:
            newUV = glyph.unicodes.pop()
            newGlyph = font.newGlyph("uni%04X" % newUV)
            newGlyph.appendComponent(glyph.name)
            newGlyph.unicode = newUV
            newGlyph.width = glyph.width

    compiler = OTFCompiler()
    reports = compiler.compile(font, destFile, autohint=autohint)
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]
