from anchors import alignComponentsToAnchors


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


def copyMarkAnchors(f, g, srcname, width):
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
                continue
            if g.unicode > 0x02B0:
                continue
            parenttop_present = 0
            for anc in g.anchors:
                if anc.name == "parent_top":
                    parenttop_present = 1
            if parenttop_present:
                continue
            anchor1 = Anchor(anchor)
            anchor1.name = "parent_top"
#            anchor1.x += width
            g.anchors.append(anchor1)

 #       if "rhotichook" == anchor.name:
 #           anchor1 = Anchor(anchor)
 #           anchor1.x += width
 #           g.anchors.append(anchor1)


def generateGlyph(f,gname,glyphList={}):
    glyphName, baseName, accentNames, offset = parseComposite(gname)

    if baseName.find("_") != -1:
        g = f.newGlyph(glyphName)
        for componentName in baseName.split("_"):
            g.appendComponent(componentName, (g.width, 0))
            g.width += f[componentName].width

    else: 
        if not f.has_key(glyphName):
            try:
                f.compileGlyph(glyphName, baseName, accentNames)
            except KeyError as e:
                print ("KeyError raised for composition rule '%s', likely %s "
                    "anchor not found in glyph '%s'" % (gname, e, baseName))
                return
            g = f[glyphName]
            copyMarkAnchors(f, g, baseName, offset[1] + offset[0])
            if offset[0] != 0 or offset[1] != 0:
                g.width += offset[1] + offset[0]
                g.move((offset[0], 0))
            if len(accentNames) > 0:
                alignComponentsToAnchors(f, glyphName, baseName, accentNames)
        else:
            print ("Existing glyph '%s' found in font, ignoring composition "
                "rule '%s'" % (glyphName, gname))

    # try to ensure every glyph has a unicode value -- used by FDK to make OTFs
    if glyphName in glyphList:
        f[glyphName].unicode = int(glyphList[glyphName], 16)
