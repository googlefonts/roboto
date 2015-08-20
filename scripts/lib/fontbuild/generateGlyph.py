from anchors import alignComponentsToAnchors
from FL import *
from string import find

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

def copyMarkAnchors(f, g, srcname, width):
    unicode_range = range(0x0030, 0x02B0) + range(0x1E00, 0x1EFF)
    anchors = f[srcname].anchors
    for anchor in anchors:
        if "top_dd" == anchor.name:
            anchor1 = Anchor(anchor)
            anchor1.x += width
            g.anchors.append(anchor1)
        if "bottom_dd" == anchor.name:
            anchor1 = Anchor(anchor)
            anchor1.x += width
            g.anchors.append(anchor1)
        if "top0315" == anchor.name:
            anchor1 = Anchor(anchor)
            anchor1.x += width
            g.anchors.append(anchor1)
        if "top" == anchor.name:
            if g.unicode == None:
                if (-1 == find(g.name, ".ccmp")) and (-1 == find(g.name, ".NAV")) and (-1 == find(g.name, ".smcp")):
                    continue                
            if False == (g.unicode in unicode_range):
                if (-1 == find(g.name, ".ccmp")) and (-1 == find(g.name, ".NAV")) and (-1 == find(g.name, ".smcp")):
                    continue
            #if g.unicode > 0x02B0:
            #    continue
            parenttop_present = 0
            for anc in g.anchors:
                if anc.name == "parent_top":
                    parenttop_present = 1
            if 0 == parenttop_present:
                anchor2 = Anchor(anchor)
                anchor2.name = "parent_top"
#               anchor1.x += width
                g.anchors.append(anchor2)

        if "bottom" == anchor.name:
            if g.unicode == None:
                if -1 == find(g.name, ".smcp"):
                    continue
            if False == (g.unicode in unicode_range):
                if -1 == find(g.name, ".smcp"):
                    continue
            #if g.unicode > 0x02B0:
            #    continue
            bottom_present = 0
            for anc in g.anchors:
                if anc.name == "bottom":
                    bottom_present = 1
            if 0 == bottom_present:
                anchor2 = Anchor(anchor)
                anchor2.name = "bottom"
#               anchor1.x += width
                g.anchors.append(anchor2)


#            anchor1 = Anchor(anchor)
#            anchor1.name = "top"
#            anchor1.x += width
#            g.anchors.append(anchor1)
            
 #       if "rhotichook" == anchor.name:
 #           anchor1 = Anchor(anchor)
 #           anchor1.x += width
 #           g.anchors.append(anchor1)
 
    #print g.anchors
    for anchor in g.anchors:
        if "top" == anchor.name:
            #print g.name, g.anchors
            return
 
    anchor_parent_top = None

    for anchor in g.anchors:
        if "parent_top" == anchor.name:
            anchor_parent_top = anchor
            break

    if anchor_parent_top:
        anchor_top = Anchor(anchor_parent_top)
        anchor_top.name = "top"
        g.anchors.append(anchor_top)
    
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
        copyMarkAnchors(f, g, baseName, offset[1] + offset[0])
        if f.FindGlyph(g.name) == -1:
            f.glyphs.append(g)
            g1 = f.glyphs[f.FindGlyph(g.name)]
            if (offset[0] != 0 or offset[1] != 0):
                g1.width += offset[1] + offset[0]
                shiftGlyphMembers(g1,offset[0])
            if len(accentNames) > 0:
                alignComponentsToAnchors(f,glyphName,baseName,accentNames)                
        return g

# generateGlyph(fl.font,"A+ogonek=Aogonek")
# fl.UpdateFont()