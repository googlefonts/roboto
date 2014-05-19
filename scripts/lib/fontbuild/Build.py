from FL import *
from fontbuild.mix import Mix,Master,narrowFLGlyph
from fontbuild.instanceNames import setNames
from fontbuild.italics import italicizeGlyph
from fontbuild.convertCurves import glyphCurvesToQuadratic
from fontbuild.mitreGlyph import mitreGlyph
from fontbuild.generateGlyph import generateGlyph
from fontTools.misc.transform import Transform
from fontbuild.kerning import generateFLKernClassesFromOTString
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
        
        self.builddir = "out"
        self.decompose = self.config.get("glyphs","decompose").split()
        self.predecompose = self.config.get("glyphs","predecompose").split()
        self.lessItalic = self.config.get("glyphs","lessitalic").split()
        self.deleteList = self.config.get("glyphs","delete").split()
        self.buildnumber = self.loadBuildNumber()
        
        
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
    
    
    def generateFont(self, mix, names, italic=False, swapSuffixes=None, stemWidth=185, kern=True):
        
        n = names.split("/")
        log("---------------------\n%s %s\n----------------------" %(n[0],n[1]))
        log(">> Mixing masters")
        if isinstance( mix, Mix):
            f = mix.generateFont(self.basefont)
        else:
            f = Font(mix)
        fl.Add(f)
        index = fl.ifont
        fl.CallCommand(33239) # Sort glyphs by unicode
        if italic == True:
            log(">> Italicizing")
            fl.UpdateFont(fl.ifont)
            tweakAmmount = .085
            narrowAmmount = .93
            if names.find("Thin") != -1:
                tweakAmmount = .05
            if names.find("Condensed") != -1:
                narrowAmmount = .96
            i = 0
            for g in f.glyphs:
                i += 1
                if i % 10 == 0: print g.name
                
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
                    g.RemoveOverlap()
                    
                    # not sure why FontLab sometimes refuses, seems to work if called twice
                
                if (g.name in self.lessItalic):
                    italicizeGlyph(g, 9, stemWidth=stemWidth)
                else:
                    italicizeGlyph(g, 10, stemWidth=stemWidth)
                g.RemoveOverlap()
                g.width += 10
                fl.UpdateGlyph(i-1)
            
        if swapSuffixes != None:
            for swap in swapSuffixes:
                swapList = [g.name for g in f.glyphs if g.name.endswith(swap)]
                for gname in swapList:
                    print gname
                    swapGlyphs(f, gname.replace(swap,""), gname)
        for gname in self.predecompose:
            g = f[f.FindGlyph(gname)]
            if g != None:
                g.Decompose()

        log(">> Generating glyphs")
        generateGlyphs(f, self.diacriticList)
        log(">> Copying features")
        f.ot_classes = self.ot_classes
        copyFeatures(self.basefont,f)
        fl.UpdateFont(index)
        log(">> Decomposing")
        for gname in self.decompose:
            g = f[f.FindGlyph(gname)]
            if g != None:
                g.Decompose()
                g.Decompose()

        setNames(f, n, foundry=self.config.get('main','foundry'), 
                       version=self.config.get('main','version'), 
                       build=self.buildnumber)
        cleanCurves(f)
        deleteGlyphs(f,self.deleteList)
        if kern:
            generateFLKernClassesFromOTString(f,self.ot_kerningclasses)
        log(">> Generating font files")
        directoryName = n[0].replace(" ","")
        directoryPath = "%s/%s/%sTTF"%(self.basedir,self.builddir,directoryName)        
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)
        ttfName = "%s/%s.ttf"%(directoryPath,f.font_name)
        fl.GenerateFont(fl.ifont,ftTRUETYPE,ttfName)
        f.modified = 0
        fl.Close(index)

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
        g1 = f.glyphs[f.FindGlyph(gName1)]
        g2 = f.glyphs[f.FindGlyph(gName2)]
    except IndexError:
        log("swapGlyphs failed for %s %s"%(gName1, gName2))
        return
    g3 = Glyph(g1)
    
    g1.Clear()
    g1.Insert(g2)
    g1.SetMetrics(g2.GetMetrics())
    
    g2.Clear()
    g2.Insert(g3)
    g2.SetMetrics(g3.GetMetrics())
    
def log(msg):
    print msg

# def addOTFeatures(f):
#     f.ot_classes = ot_classes

def copyFeatures(f1, f2):
    for ft in f1.features:
        t = Feature(ft.tag, ft.value)
        f2.features.append(t)
    #f2.ot_classes = f1.ot_classes
    f2.classes = []
    f2.classes = f1.classes

def generateGlyphs(f, glyphNames):
    log(">> Generating diacritics")
    glyphnames = [gname for gname in glyphNames if not gname.startswith("#") and gname != ""]
    
    for glyphName in glyphNames:
        generateGlyph(f, glyphName)

def cleanCurves(f):
    log(">> Removing overlaps")
    for g in f.glyphs:
        g.UnselectAll()
        g.RemoveOverlap()

    log(">> Mitring sharp corners")
    # for g in f.glyphs:
    #     mitreGlyph(g, 3., .7)
    
    log(">> Converting curves to quadratic")
    # for g in f.glyphs:
    #     glyphCurvesToQuadratic(g)
    
def deleteGlyphs(f,deleteList):
    fl.Unselect()
    for name in deleteList:
        glyphIndex = f.FindGlyph(name)
        if glyphIndex != -1:
            del f.glyphs[glyphIndex]
    fl.UpdateFont()
