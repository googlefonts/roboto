# Copyright 2016 Google Inc. All Rights Reserved.
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


import os
import sys
from fontTools.misc.transform import Transform

from fontbuild.Build import (
    FontProject, deleteGlyphs, removeGlyphOverlap, swapContours)
from fontbuild.instanceNames import setNamesRF
from fontbuild.italics import italicizeGlyph, transformFLGlyphMembers
from fontbuild.mix import Master, Mix


FAMILYNAME = "Roboto"

# The root of the Roboto tree
BASEDIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))

# Masters
rg = Master("%s/src/v2/Roboto-Regular.ufo" % BASEDIR)
bd = Master("%s/src/v2/Roboto-Bold.ufo" % BASEDIR)
th = Master("%s/src/v2/Roboto-Thin.ufo" % BASEDIR)

uncondensed = (
    "tonos breve acute grave quotesingle quotedbl asterisk "
    "period currency registered copyright bullet ring degree "
    "dieresis comma bar brokenbar dotaccent dotbelow "
    "colon semicolon uniFFFC uniFFFD uni0488 uni0489 ringbelow "
    "estimated").split()


def condenseFont(font, scale=.8, stemWidth=185):
    f = font.copy()
    for g in f:
        if len(g) > 0 and g.name in uncondensed:
            continue
        m = Transform(scale, 0, 0, 1, 20, 0)
        g.transform(m)
        transformFLGlyphMembers(g, m, transformAnchors=False)
        if g.width != 0:
            g.width += 40
    return f


def generateCondensedMasters(proj):
    thcn1 = Master(condenseFont(th.font, .84, 40))
    cn1 = Master(rg.ffont.addDiff(thcn1.ffont, th.ffont))
    bdcn1 = Master(bd.ffont.addDiff(thcn1.ffont, th.ffont))

    proj.generateFont(Mix([thcn1, cn1], 0),
                      "%s Condensed/Thin/Regular/Th" % FAMILYNAME,
                      swapSuffixes=[".cn"])
    proj.generateFont(Mix([thcn1, cn1], 1),
                      "%s Condensed/Regular/Regular/Rg" % FAMILYNAME,
                      swapSuffixes=[".cn"])
    proj.generateFont(Mix([cn1, bdcn1], 1),
                      "%s Condensed/Bold/Bold/Rg" % FAMILYNAME,
                      swapSuffixes=[".cn"])


def generateItalicMasters(proj):
    proj.generateFont(th.font, "%s/Thin Italic/Italic/Th" % FAMILYNAME,
                      italic=True, stemWidth=80)

    #TODO figure out best stem widths for consistent output
    proj.generateFont(rg.font, "%s/Italic/Italic/Rg" % FAMILYNAME,
                      italic=True, stemWidth=200)
    proj.generateFont(bd.font, "%s/Bold Italic/Bold Italic/Rg" % FAMILYNAME,
                      italic=True, stemWidth=320)


def generateCondensedItalicFromItalic():
    rg = Master("%s/src/v2/Roboto-Italic.ufo" % BASEDIR)
    bd = Master("%s/src/v2/Roboto-BoldItalic.ufo" % BASEDIR)
    th = Master("%s/src/v2/Roboto-ThinItalic.ufo" % BASEDIR)
    proj = MasterFontProject(rg.font, BASEDIR, "res/roboto.cfg")

    thcn1 = Master(condenseFont(th.font, .84, 40))
    cn1 = Master(rg.ffont.addDiff(thcn1.ffont, th.ffont))
    bdcn1 = Master(bd.ffont.addDiff(thcn1.ffont, th.ffont))

    proj.generateFont(Mix([thcn1, cn1], 0),
                      "%s Condensed/Thin Italic/Italic/Th" % FAMILYNAME,
                      swapSuffixes=[".cn"])
    proj.generateFont(Mix([thcn1, cn1], 1),
                      "%s Condensed/Italic/Italic/Rg" % FAMILYNAME,
                      swapSuffixes=[".cn"])
    proj.generateFont(Mix([cn1, bdcn1], 1),
                      "%s Condensed/Bold Italic/Bold Italic/Rg" % FAMILYNAME,
                      swapSuffixes=[".cn"])


def generateCondensedItalicFromCondensed(proj):
    thcn1 = Master(condenseFont(th.font, .84, 40))
    cn1 = Master(rg.ffont.addDiff(thcn1.ffont, th.ffont))
    bdcn1 = Master(bd.ffont.addDiff(thcn1.ffont, th.ffont))

    proj.generateFont(Mix([thcn1, cn1], 0),
                      "%s Condensed/Thin Italic/Italic/Th" % FAMILYNAME,
                      italic=True, swapSuffixes=[".cn"], stemWidth=80)
    proj.generateFont(Mix([thcn1, cn1], 1),
                      "%s Condensed/Italic/Italic/Rg" % FAMILYNAME,
                      italic=True, swapSuffixes=[".cn"], stemWidth=200)
    proj.generateFont(Mix([cn1, bdcn1], 1),
                      "%s Condensed/Bold Italic/Bold Italic/Rg" % FAMILYNAME,
                      italic=True, swapSuffixes=[".cn"], stemWidth=260)


class MasterFontProject(FontProject):
    def generateFont(
            self, mix, names, italic=False, swapSuffixes=None, stemWidth=185):
        n = names.split("/")
        print("-------------------\n%s %s\n-------------------" % (n[0], n[1]))
        print(">> Mixing masters")
        if isinstance(mix, Mix):
            f = mix.generateFont(self.basefont)
        else:
            f = mix.copy()

        if italic:
            print(">> Italicizing")
            i = 0
            for g in f:
                i += 1
                if i % 10 == 0: print g.name
                if g.name == "uniFFFD":
                    continue
                removeGlyphOverlap(g)
                if g.name in self.lessItalic:
                    italicizeGlyph(f, g, 9, stemWidth=stemWidth)
                elif g.name not in self.noItalic:
                    italicizeGlyph(f, g, 10, stemWidth=stemWidth)
                if g.width != 0:
                    g.width += 10
            # set the oblique flag in fsSelection
            f.info.openTypeOS2Selection.append(9)

        if swapSuffixes is not None:
            for swap in swapSuffixes:
                swapList = [g.name for g in f if g.name.endswith(swap)]
                for gname in swapList:
                    print gname
                    swapContours(f, gname.replace(swap, ""), gname)

        setNamesRF(f, n, foundry=self.config.get('main', 'foundry'),
                         version=self.config.get('main', 'version'),
                         master=True)
        deleteGlyphs(f, self.deleteList)

        print(">> Generating font files")
        family = f.info.familyName.replace(" ", "")
        style = f.info.styleName.replace(" ", "")
        ufoName = os.path.join(
            os.path.dirname(f.path), "%s-%s.ufo" % (family, style))
        print(ufoName)
        f.save(ufoName)


if __name__ == '__main__':
    cmd = sys.argv[1]
    proj = MasterFontProject(rg.font, BASEDIR, "res/roboto.cfg")
    if cmd == 'masters-condensed':
        generateCondensedMasters(proj)
    elif cmd == 'masters-italic':
        generateItalicMasters(proj)
    elif cmd == 'masters-condenseditalic-fromitalic':
        generateCondensedItalicFromItalic()
    elif cmd == 'masters-condenseditalic-fromcondensed':
        generateCondensedItalicFromCondensed(proj)
    else:
        print 'Unrecognized command "%s"' % cmd
