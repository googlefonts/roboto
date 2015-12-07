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


import re
from anchors import alignComponentsToAnchors
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


def copyMarkAnchors(f, g, srcname, width):
    unicode_range = range(0x0030, 0x02B0) + range(0x1E00, 0x1EFF)
    anchors = f[srcname].anchors
    for anchor in anchors:
        if "top_dd" == anchor.name:
            g.appendAnchor(anchor.name, (anchor.x + width, anchor.y))
        if "bottom_dd" == anchor.name:
            g.appendAnchor(anchor.name, (anchor.x + width, anchor.y))
        if "top0315" == anchor.name:
            g.appendAnchor(anchor.name, (anchor.x + width, anchor.y))
        if "top" == anchor.name:
            if g.unicode == None:
                if not g.name.endswith(('.ccmp', '.smcp', '.NAV')):
                    continue                
            if False == (g.unicode in unicode_range):
                if not g.name.endswith(('.ccmp', '.smcp', '.NAV')):
                    continue
            #if g.unicode > 0x02B0:
            #    continue
            parenttop_present = 0
            for anc in g.anchors:
                if anc.name == "parent_top":
                    parenttop_present = 1
            if 0 == parenttop_present:
                g.appendAnchor("parent_top", anchor.position)

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
                g.appendAnchor("bottom", anchor.position)


#            g.appendAnchor("top", anchor.position)
            
 #       if "rhotichook" == anchor.name:
 #           g.appendAnchor(anchor.name, (anchor.x + width, anchor.y))
 
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

    if anchor_parent_top is not None:
        g.appendAnchor("top", anchor_parent_top.position)


def generateGlyph(f,gname,glyphList={}):
    glyphName, baseName, accentNames, offset = parseComposite(gname)

    if baseName.find("_") != -1:
        g = f.newGlyph(glyphName)
        for componentName in baseName.split("_"):
            g.appendComponent(componentName, (g.width, 0))
            g.width += f[componentName].width
            setUnicodeValue(g, glyphList)

    else: 
        if not f.has_key(glyphName):
            try:
                f.compileGlyph(glyphName, baseName, accentNames)
            except KeyError as e:
                print ("KeyError raised for composition rule '%s', likely %s "
                    "anchor not found in glyph '%s'" % (gname, e, baseName))
                return
            g = f[glyphName]
            setUnicodeValue(g, glyphList)
            copyMarkAnchors(f, g, baseName, offset[1] + offset[0])
            if offset[0] != 0 or offset[1] != 0:
                g.width += offset[1] + offset[0]
                g.move((offset[0], 0), anchors=False)
            if len(accentNames) > 0:
                alignComponentsToAnchors(f, glyphName, baseName, accentNames)
        else:
            print ("Existing glyph '%s' found in font, ignoring composition "
                "rule '%s'" % (glyphName, gname))


def setUnicodeValue(glyph, glyphList):
    """Try to ensure glyph has a unicode value -- used by FDK to make OTFs."""

    if glyph.name in glyphList:
        glyph.unicode = int(glyphList[glyph.name], 16)
    else:
        uvNameMatch = re.match("uni([\dA-F]{4})$", glyph.name)
        if uvNameMatch:
            glyph.unicode = int(uvNameMatch.group(1), 16)
