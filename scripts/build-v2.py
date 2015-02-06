import sys

sys.path.insert(0,"%s/scripts/lib"%BASEDIR)

from robofab.objects.objectsRF import RFont, RPoint
from fontTools.misc.transform import Transform
from fontbuild.Build import FontProject,swapGlyphs,transformGlyphMembers
from fontbuild.mix import Mix,Master
from fontbuild.italics import condenseGlyph, transformFLGlyphMembers

# Masters

rg = Master("%s/src/v2/Roboto_Regular.ufo"%BASEDIR)
bd = Master("%s/src/v2/Roboto_Bold.ufo"%BASEDIR)
th = Master("%s/src/v2/Roboto_Thin.ufo"%BASEDIR)

# build condensed masters

lessCondensed = "plusminus \
bracketleft bracketright dieresis \
macron percent \
multiply degree at i j zero one two \
three four five six seven eight nine braceright braceleft".split()
uncondensed = "tonos breve acute grave quotesingle quotedbl asterisk \
period currency registered copyright bullet ring degree dieresis comma bar brokenbar dotaccent \
dotbelow colon semicolon uniFFFC uniFFFD uni0488 uni0489 ringbelow estimated".split()
moreCondensed = "z Z M W A V".split()


def condenseFont(f, scale=.8, stemWidth=185):
    xscale = scale
    CAPS = "A B C.cn D.cn E F G.cn H I J K L M N O.cn P Q.cn R S T U.cn V W X Y Z one two three four five six seven eight nine zero".split()
    LC = "a.cn b.cn c.cn d.cn e.cn f g.cn h i j k l m n o.cn p.cn q.cn r s t u v w x y z".split()
    # for g in [f[name] for name in LC]:
    for g in f:
        if (len(g) > 0):
            # print g.name
            if g.name in lessCondensed:
                scale = xscale * 1.1
            if g.name in uncondensed:
                continue
            if g.name in moreCondensed:
                scale = xscale * .90
            # g2 = condenseGlyph(g, xscale)
            # g.clear()
            # g2.drawPoints(g.getPointPen())
        m = Transform(xscale, 0, 0, 1, 20, 0)
        g.transform(m)
        transformFLGlyphMembers(g,m,transformAnchors=False)
        g.width += 40
    return f


proj = FontProject(rg.font, BASEDIR, "res/roboto.cfg", th.ffont)
#proj.incrementBuildNumber()

# FAMILYNAME = "Roboto 2 DRAFT"
# FAMILYNAME = "Roboto2"
FAMILYNAME = "Roboto"

proj.buildOTF = True
#proj.checkOTFOutlines = True
#proj.autohintOTF = True
#proj.buildFEA = True

proj.generateFont(th.font,"%s/Thin/Regular/Th"%FAMILYNAME)
proj.generateFont(Mix([th,rg], 0.45),"%s/Light/Regular/Lt"%FAMILYNAME)
proj.generateFont(Mix([th,rg], RPoint(0.90, 0.92)),"%s/Regular/Regular/Rg"%FAMILYNAME)
proj.generateFont(Mix([rg,bd], 0.35),"%s/Medium/Regular/Lt"%FAMILYNAME)
proj.generateFont(Mix([rg,bd], RPoint(0.73, 0.73)),"%s/Bold/Bold/Rg"%FAMILYNAME)
proj.generateFont(Mix([rg,bd], RPoint(1.125, 1.0)),"%s/Black/Bold/Bk"%FAMILYNAME)

proj.generateFont(th.font,"%s/Thin Italic/Italic/Th"%FAMILYNAME, italic=True, stemWidth=80)
proj.generateFont(Mix([th,rg], 0.45),"%s/Light Italic/Italic/Lt"%FAMILYNAME, italic=True, stemWidth=120)
proj.generateFont(Mix([th,rg], RPoint(0.90, 0.92)),"%s/Italic/Italic/Rg"%FAMILYNAME, italic=True, stemWidth=185)
proj.generateFont(Mix([rg,bd], 0.35),"%s/Medium Italic/Bold Italic/Lt"%FAMILYNAME, italic=True, stemWidth=230)
proj.generateFont(Mix([rg,bd], RPoint(0.73, 0.73)),"%s/Bold Italic/Bold Italic/Rg"%FAMILYNAME, italic=True, stemWidth=290)
proj.generateFont(Mix([rg,bd], RPoint(1.125, 1.0)),"%s/Black Italic/Bold Italic/Bk"%FAMILYNAME, italic=True, stemWidth=290)

thcn1 = Master(condenseFont(th.font, .84, 40))
cn1 = Master( rg.ffont.addDiff(thcn1.ffont, th.ffont))
bdcn1 = Master( bd.ffont.addDiff(thcn1.ffont, th.ffont))

proj.generateFont(Mix([thcn1,cn1], RPoint(0.45, 0.47)), "%s Condensed/Light/Regular/Lt"%FAMILYNAME, swapSuffixes=[".cn"])
proj.generateFont(Mix([thcn1,cn1], RPoint(0.9, 0.92)), "%s Condensed/Regular/Regular/Rg"%FAMILYNAME, swapSuffixes=[".cn"])
proj.generateFont(Mix([cn1,bdcn1], RPoint(0.75, 0.75)), "%s Condensed/Bold/Bold/Rg"%FAMILYNAME, swapSuffixes=[".cn"])

proj.generateFont(Mix([thcn1,cn1], RPoint(0.45, 0.47)), "%s Condensed/Light Italic/Italic/Lt"%FAMILYNAME, italic=True, swapSuffixes=[".cn"], stemWidth=120)
proj.generateFont(Mix([thcn1,cn1], RPoint(0.9, 0.92)), "%s Condensed/Italic/Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".cn"], stemWidth=185)
proj.generateFont(Mix([cn1,bdcn1], RPoint(0.75, 0.75)), "%s Condensed/Bold Italic/Bold Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".cn"], stemWidth=240)

sys.exit(0)
