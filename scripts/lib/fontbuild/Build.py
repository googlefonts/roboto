from robofab.world import OpenFont
from fontbuild.mix import Mix,Master,narrowFLGlyph
from fontbuild.instanceNames import setNamesRF
from fontbuild.italics import italicizeGlyph
from fontbuild.convertCurves import glyphCurvesToQuadratic
from fontbuild.mitreGlyph import mitreGlyph
from fontbuild.generateGlyph import generateGlyph
from fontTools.misc.transform import Transform
from fontbuild.features import generateFeatureFile, readFeatureFile, readGlyphClasses, writeFeatureFile
from fontbuild.markFeature import GenerateFeature_mark
from fontbuild.mkmkFeature import GenerateFeature_mkmk
from fontbuild.decomposeGlyph import decomposeGlyph
from fontbuild.removeGlyphOverlap import removeGlyphOverlap
from fontbuild.saveOTF import saveOTF, conformToAGL
from fontbuild.sortGlyphs import sortGlyphsByUnicode
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
        self.ot_features = open(self.basedir + "/" + self.config.get("res","ot_featuresfile")).read()
        adobeGlyphList = open(self.basedir + "/" + self.config.get("res", "agl_glyphlistfile")).readlines()
        self.adobeGlyphList = set([line.split(";")[0] for line in adobeGlyphList if not line.startswith("#")])
        
        self.builddir = "out"
        self.decompose = self.config.get("glyphs","decompose").split()
        self.predecompose = self.config.get("glyphs","predecompose").split()
        self.lessItalic = self.config.get("glyphs","lessitalic").split()
        self.deleteList = self.config.get("glyphs","delete").split()
        self.buildnumber = self.loadBuildNumber()
        
        self.buildOTF = False
        self.checkOTFOutlines = False
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
        path = "%s/%s/%s%s" % (self.basedir, self.builddir, family, ext.upper())
        if not os.path.exists(path):
            os.makedirs(path)
        return "%s/%s-%s.%s" % (path, family, style, ext.lower())
    
    def generateFont(self, mix, names, italic=False, swapSuffixes=None, stemWidth=185, kern=True):
        
        n = names.split("/")
        log("---------------------\n%s %s\n----------------------" %(n[0],n[1]))
        log(">> Mixing masters")
        if isinstance( mix, Mix):
            f = mix.generateFont(self.basefont)
        else:
            f = mix
        sortGlyphsByUnicode(f)
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
                g.width += 10

        if swapSuffixes != None:
            for swap in swapSuffixes:
                swapList = [g.name for g in f if g.name.endswith(swap)]
                for gname in swapList:
                    print gname
                    swapGlyphs(f, gname.replace(swap,""), gname)
        for gname in self.predecompose:
            if f.has_key(gname):
                decomposeGlyph(f[gname])

        log(">> Generating glyphs")
        generateGlyphs(f, self.diacriticList)
        log(">> Copying features")
        readGlyphClasses(f, self.ot_classes)
        readFeatureFile(f, self.basefont.features.text)
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
            readGlyphClasses(f, self.ot_kerningclasses, update=False)

        log(">> Generating font files")
        generateFeatureFile(f)
        ufoName = self.generateOutputPath(f, "ufo")
        f.save(ufoName)

        if self.buildOTF:
            log(">> Generating OTF file")
            newFont = OpenFont(ufoName)
            conformToAGL(newFont, self.adobeGlyphList)
            otfName = self.generateOutputPath(f, "otf")
            saveOTF(newFont, otfName, autohint=self.autohintOTF)

            if self.checkOTFOutlines or self.buildTTF:
                import fontforge
                otFont = fontforge.open(otfName)

                if self.checkOTFOutlines:
                    for glyphName in otFont:
                        otFont[glyphName].removeOverlap()
                    otFont.generate(otfName)

                if self.buildTTF:
                    log(">> Generating TTF file")
                    otFont.generate(self.generateOutputPath(f, "ttf"))

        if self.buildFEA:
          log(">> Generating FEA files")  
          GenerateFeature_mark(f)
          GenerateFeature_mkmk(f)
          writeFeatureFile(f, self.generateOutputPath(f, "fea"))


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

def swapGlyphs(f,gName1,gName2):
    try:
        g1 = f[gName1]
        g2 = f[gName2]
    except KeyError:
        log("swapGlyphs failed for %s %s" % (gName1, gName2))
        return
    g3 = g1.copy()

    g1.clear()
    g1.appendGlyph(g2)
    g1.width = g2.width

    g2.clear()
    g2.appendGlyph(g3)
    g2.width = g3.width


def log(msg):
    print msg


def generateGlyphs(f, glyphNames):
    log(">> Generating diacritics")
    glyphnames = [gname for gname in glyphNames if not gname.startswith("#") and gname != ""]
    
    for glyphName in glyphNames:
        generateGlyph(f, glyphName)

def cleanCurves(f):
    #TODO(jamesgk) remove calls to removeGlyphOverlap if we decide to use AFDKO
    log(">> Removing overlaps")
    for g in f:
        removeGlyphOverlap(g)

    log(">> Mitring sharp corners")
    # for g in f.glyphs:
    #     mitreGlyph(g, 3., .7)
    
    log(">> Converting curves to quadratic")
    # for g in f.glyphs:
    #     glyphCurvesToQuadratic(g)


def deleteGlyphs(f, deleteList):
    for name in deleteList:
        if f.has_key(name):
            f.removeGlyph(name)
