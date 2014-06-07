#import numpy as np
from FL import *


def getGlyph(gname,font):
    index = font.FindGlyph(gname)
    if index != -1:
        return font.glyphs[index]
    else:
        return None

def getComponentByName(f,g,componentName):
    componentIndex = f.FindGlyph(componentName)
    for c in g.components:
        if c.index == componentIndex:
            return c

def getAnchorByName(g,anchorName):
    for a in g.anchors:
        if a.name == anchorName:
            return a


def alignComponentToAnchor(f,glyphName,baseName,accentName,anchorName):
    g = getGlyph(glyphName,f)
    base = getGlyph(baseName,f)
    accent = getGlyph(accentName,f)
    if g == None or base == None or accent == None:
        return
    a1 = getAnchorByName(base,anchorName)
    a2 = getAnchorByName(accent,"_" + anchorName)
    if a1 == None or a2 == None:
        return
    offset = a1.p - a2.p
    c = getComponentByName(f,g,accentName)
    c.deltas[0].x = offset.x
    c.deltas[0].y = offset.y

def alignComponentsToAnchors(f,glyphName,baseName,accentNames):
    for a in accentNames:
        if len(a) == 1:
            continue
        alignComponentToAnchor(f,glyphName,baseName,a[0],a[1])

