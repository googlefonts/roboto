from FL import *
from numpy import array, append
import copy

class FFont:
    "Font wrapper for floating point operations"
    
    def __init__(self,f=None):
        self.glyphs = {}
        self.hstems = []
        self.vstems = []
        if isinstance(f,FFont):
            #self.glyphs = [g.copy() for g in f.glyphs]
            for key,g in f.glyphs.iteritems():
                self.glyphs[key] = g.copy()
            self.hstems = list(f.hstems)
            self.vstems = list(f.vstems)
        elif f != None:
            self.copyFromFont(f)
        
    def copyFromFont(self,f):
        for g in f.glyphs:
            self.glyphs[g.name] = FGlyph(g)
        self.hstems = [s for s in f.stem_snap_h[0]]
        self.vstems = [s for s in f.stem_snap_v[0]]
    
            
    def copyToFont(self,f):
        for g in f.glyphs:
            try:
                gF = self.glyphs[g.name]
                gF.copyToGlyph(g)
            except:
                print "Copy to glyph failed for" + g.name
        f.stem_snap_h[0] = self.hstems
        f.stem_snap_v[0] = self.vstems
        
    def getGlyph(self, gname):
        try:
            return self.glyphs[gname]
        except:
            return None
        
    def setGlyph(self, gname, glyph):
        self.glyphs[gname] = glyph
    
    def addDiff(self,b,c):
        newFont = FFont(self)
        for key,g in newFont.glyphs.iteritems():
            gB = b.getGlyph(key)
            gC = c.getGlyph(key)
            try:
                newFont.glyphs[key] = g.addDiff(gB,gC)
            except:
                print "Add diff failed for '%s'" %key
        return newFont

class FGlyph:
    "provides a temporary floating point compatible glyph data structure"
    
    def __init__(self, g=None):
        self.nodes = []
        self.width = 0.
        self.components = []
        self.kerning = []
        self.anchors = []
        if g != None:
            self.copyFromGlyph(g)
        
    def copyFromGlyph(self,g):
        self.name = g.name
        valuesX = []
        valuesY = []
        self.width = len(valuesX)
        valuesX.append(g.width)
        for c in g.components:
            self.components.append((len(valuesX),len(valuesY)))
            valuesX.append(c.scale.x)
            valuesY.append(c.scale.y)
            valuesX.append(c.delta.x)
            valuesY.append(c.delta.y)
        
        for a in g.anchors:
            self.anchors.append((len(valuesX), len(valuesY)))
            valuesX.append(a.x)
            valuesY.append(a.y)
                
        for i in range(len(g.nodes)):
            self.nodes.append([])
            for j in range (len(g.nodes[i])):
                self.nodes[i].append( (len(valuesX), len(valuesY)) )
                valuesX.append(g.nodes[i][j].x)
                valuesY.append(g.nodes[i][j].y)
                
        for k in g.kerning:
            self.kerning.append(KerningPair(k))
            
        self.dataX = array(valuesX)
        self.dataY = array(valuesY)
        
    def copyToGlyph(self,g):
        g.width = self._derefX(self.width)
        if len(g.components) == len(self.components):
            for i in range(len(self.components)):
                g.components[i].scale.x = self._derefX( self.components[i][0] + 0)
                g.components[i].scale.y = self._derefY( self.components[i][1] + 0)
                g.components[i].deltas[0].x = self._derefX( self.components[i][0] + 1)
                g.components[i].deltas[0].y = self._derefY( self.components[i][1] + 1)
        g.kerning = []
        if len(g.anchors) == len(self.anchors):
            for i in range(len(self.anchors)):
                g.anchors[i].x = self._derefX( self.anchors[i][0])
                g.anchors[i].y = self._derefY( self.anchors[i][1])
        for k in self.kerning:
            g.kerning.append(KerningPair(k))
        for i in range( len(g.nodes)) :
            for j in range (len(g.nodes[i])):
                g.nodes[i][j].x = self._derefX( self.nodes[i][j][0] )
                g.nodes[i][j].y = self._derefY( self.nodes[i][j][1] )
    
    def isCompatible(self,g):
        return len(self.dataX) == len(g.dataX) and len(self.dataY) == len(g.dataY) and len(g.nodes) == len(self.nodes)
    
    def __add__(self,g):
        if self.isCompatible(g):
            newGlyph = self.copy()
            newGlyph.dataX = self.dataX + g.dataX
            newGlyph.dataY = self.dataY + g.dataY
            return newGlyph
        else:
            print "Add failed for '%s'" %(self.name)
            raise Exception
    
    def __sub__(self,g):
        if self.isCompatible(g):
            newGlyph = self.copy()
            newGlyph.dataX = self.dataX - g.dataX
            newGlyph.dataY = self.dataY - g.dataY
            return newGlyph
        else:
            print "Subtract failed for '%s'" %(self.name)
            raise Exception
    
    def __mul__(self,scalar):
        newGlyph = self.copy()
        newGlyph.dataX = self.dataX * scalar
        newGlyph.dataY = self.dataY * scalar
        return newGlyph
    
    def scaleX(self,scalar):
        newGlyph = self.copy()
        if len(self.dataX) > 0:
            newGlyph.dataX = self.dataX * scalar
            for i in range(len(newGlyph.components)):
                newGlyph.dataX[newGlyph.components[i][0]] = self.dataX[newGlyph.components[i][0]]
        return newGlyph
        
    def shift(self,ammount):
        newGlyph = self.copy()
        newGlyph.dataX = self.dataX + ammount
        for i in range(len(newGlyph.components)):
            newGlyph.dataX[newGlyph.components[i][0]] = self.dataX[newGlyph.components[i][0]]
        return newGlyph
    
    def interp(self, g, v):
        gF = self.copy()
        if not self.isCompatible(g):
            print "Interpolate failed for '%s'; outlines incompatible" %(self.name)
            raise Exception
        
        gF.dataX += (g.dataX - gF.dataX) * v.x
        gF.dataY += (g.dataY - gF.dataY) * v.y
        gF.kerning = interpolateKerns(self,g,v)
        return gF
    
    def copy(self):
        ng = FGlyph()
        ng.nodes = list(self.nodes)
        ng.width = self.width
        ng.components = list(self.components)
        ng.kerning = list(self.kerning)
        ng.anchors = list(self.anchors)
        ng.dataX = self.dataX.copy()
        ng.dataY = self.dataY.copy()
        ng.name = self.name
        return ng
    
    def _derefX(self,id):
        return int(round(self.dataX[id]))
    
    def _derefY(self,id):
        return int(round(self.dataY[id]))
    
    def addDiff(self,gB,gC):
        newGlyph = self + (gB - gC)
        return newGlyph
        
    

class Master:
    
    
    def __init__(self,font=None,v=0,ifont=None, kernlist=None, overlay=None):
        if isinstance(font,FFont):
            self.font = None
            self.ffont = font
        elif isinstance(font,str):
            self.openFont(font,overlay)
        elif isinstance(font,Mix):
            self.font = font
        else:
            self.font = font
            self.ifont = ifont
            self.ffont = FFont(font)
        if isinstance(v,float) or isinstance(v,int):
            self.v = Point(v,v)
        else:
            self.v = v
        if kernlist != None:
            kerns = [i.strip().split() for i in open(kernlist).readlines()]
            
            self.kernlist = [{'left':k[0], 'right':k[1], 'value': k[2]} 
                            for k in kerns 
                            if not k[0].startswith("#")
                            and not k[0] == ""]
            #TODO implement class based kerning / external kerning file
    
    def openFont(self, path, overlayPath=None):
        fl.Open(path,True)
        self.ifont = fl.ifont
        for g in fl.font.glyphs:
          size = len(g)
          csize = len(g.components)
          if (size > 0 and csize > 0):
            g.Decompose()

        self.ifont = fl.ifont
        self.font = fl.font
        if overlayPath != None:
            fl.Open(overlayPath,True)
            ifont = self.ifont
            font = self.font
            overlayIfont = fl.ifont
            overlayFont = fl.font

            for overlayGlyph in overlayFont.glyphs:
                glyphIndex = font.FindGlyph(overlayGlyph.name)
                if glyphIndex != -1:
                    oldGlyph = Glyph(font.glyphs[glyphIndex])
                    kernlist = [KerningPair(k) for k in oldGlyph.kerning]
                    font.glyphs[glyphIndex] = Glyph(overlayGlyph)
                    font.glyphs[glyphIndex].kerning = kernlist
                else:
                    font.glyphs.append(overlayGlyph)
            fl.UpdateFont(ifont)
            fl.Close(overlayIfont)
        self.ffont = FFont(self.font)


class Mix:
    def __init__(self,masters,v):
        self.masters = masters
        if isinstance(v,float) or isinstance(v,int):
            self.v = Point(v,v)
        else:
            self.v = v
    
    def getFGlyph(self, master, gname):
        if isinstance(master.font, Mix):
            return font.mixGlyphs(gname)
        return master.ffont.getGlyph(gname)
    
    def getGlyphMasters(self,gname):
        masters = self.masters
        if len(masters) <= 2:
            return self.getFGlyph(masters[0], gname), self.getFGlyph(masters[-1], gname)
    
    def generateFFont(self):
        ffont = FFont(self.masters[0].ffont)
        for key,g in ffont.glyphs.iteritems():
            ffont.glyphs[key] = self.mixGlyphs(key)
        return ffont
    
    def generateFont(self, baseFont):
        newFont = Font(baseFont)
        #self.mixStems(newFont)  todo _ fix stems code
        for g in newFont.glyphs:
            gF = self.mixGlyphs(g.name)
            if gF == None:
                g.mark = True
            else:
                # FIX THIS #print gF.name, g.name, len(gF.nodes),len(g.nodes),len(gF.components),len(g.components)
                try:
                    gF.copyToGlyph(g)
                except:
                    "Nodes incompatible"
        return newFont
    
    def mixGlyphs(self,gname):
        gA,gB = self.getGlyphMasters(gname)        
        try:
            return gA.interp(gB,self.v)
        except:
            print "mixglyph failed for %s" %(gname)
            if gA != None:
                return gA.copy()

def narrowFLGlyph(g, gThin, factor=.75):
    gF = FGlyph(g)
    if not isinstance(gThin,FGlyph):
        gThin = FGlyph(gThin)
    gCondensed = gThin.scaleX(factor)
    try:
        gNarrow = gF + (gCondensed - gThin)
        gNarrow.copyToGlyph(g)
    except:
        print "No dice for: " + g.name
            
def interpolate(a,b,v,e=0):
    if e == 0:
        return a+(b-a)*v
    qe = (b-a)*v*v*v + a   #cubic easing
    le = a+(b-a)*v   # linear easing
    return le + (qe-le) * e
    
def interpolateKerns(gA,gB,v):
    kerns = []
    for kA in gA.kerning:
        key = kA.key
        matchedKern = None
        for kB in gA.kerning:
            if key == kB.key:
                matchedKern = kB
                break
        # if matchedkern == None:
        #     matchedkern = Kern(kA)
        #     matchedkern.value = 0
        if matchedKern != None:
            kernValue = interpolate(kA.value, matchedKern.value, v.x)
            kerns.append(KerningPair(kA.key,kernValue))
    return kerns