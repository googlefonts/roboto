def getGlyph(gname, font):
    return font[gname] if font.has_key(gname) else None


def getComponentByName(f, g, componentName):
    for c in g.components:
        if c.baseGlyph == componentName:
            return c

def getAnchorByName(g,anchorName):
    for a in g.anchors:
        if a.name == anchorName:
            return a


def moveMarkAnchors(f, g, anchorName, accentName, dx, dy):
    if "top"==anchorName:
        anchors = f[accentName].anchors
        for anchor in anchors:
            if "mkmktop_acc" == anchor.name:
                g.appendAnchor("top", (anchor.x + int(dx), anchor.y + int(dy)))
 
    elif "bottom"==anchorName:
        anchors = f[accentName].anchors
        for anchor in anchors:
            if "mkmkbottom_acc" == anchor.name:
                for anchor in g.anchors:
                    if anchor.name == "bottom":
                        g.removeAnchor(anchor)
                        break
                x = anchor.x + int(dx)
                for anc in anchors:
                    if "top" == anc.name:
                        x = anc.x + int(dx)
                g.appendAnchor("bottom", (x, anchor.y + int(dy)))


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
    offset = (a1.x - a2.x, a1.y - a2.y)
    c = getComponentByName(f, g, accentName)
    c.offset = offset
    moveMarkAnchors(f, g, anchorName, accentName, offset[0], offset[1])


def alignComponentsToAnchors(f,glyphName,baseName,accentNames):
    for a in accentNames:
        if len(a) == 1:
            continue
        alignComponentToAnchor(f,glyphName,baseName,a[0],a[1])

