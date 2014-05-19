from anchors import alignComponentsToAnchors
from FL import *

def parseComposite(composite):
    c = composite.split("=")
    d = c[1].split("/")
    glyphName = d[0]
    if len(d) == 1:
        offset = [0,0]
    else:
        offset = [int(i) for i in d[1].split(",")]
    accentString = c[0]
    accents = accentString.split("+")
    baseName = accents.pop(0)
    accentNames = [i.split(":") for i in accents ]
    return (glyphName, baseName, accentNames, offset)

def shiftGlyphMembers(g, x):
    g.Shift(Point(x,0))
    for c in g.components:
        c.deltas[0].x = c.deltas[0].x + x

def generateGlyph(f,gname):
    if gname.find("_") != -1:
        generateString = gname
        g = f.GenerateGlyph(generateString)
        if f.FindGlyph(g.name) == -1:
            f.glyphs.append(g)
        return g
    else: 
        glyphName, baseName, accentNames, offset = parseComposite(gname)
        components = [baseName] + [i[0] for i in accentNames]
        if len(components) == 1:
            components.append("NONE")
        generateString = "%s=%s" %("+".join(components), glyphName)
        g = f.GenerateGlyph(generateString)
        if f.FindGlyph(g.name) == -1:
            f.glyphs.append(g)
            g1 = f.glyphs[f.FindGlyph(g.name)]
            if len(accentNames) > 0:
                alignComponentsToAnchors(f,glyphName,baseName,accentNames)
            if (offset[0] != 0 or offset[1] != 0):
                g1.width += offset[1] + offset[0]
                shiftGlyphMembers(g1,offset[0])
        return g

# generateGlyph(fl.font,"A+ogonek=Aogonek")
# fl.UpdateFont()