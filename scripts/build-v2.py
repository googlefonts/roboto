
import sys
# BASEDIR="/Users/robertsonc/GoogleDrive/Fonts/Roboto_src"
sys.path.insert(0,"%s/scripts/lib"%BASEDIR)

from robofab.world import RFont
from fontTools.misc.transform import Transform
from fontbuild.Build import FontProject,swapGlyphs,transformGlyphMembers
from fontbuild.mix import Mix,Master
from fontbuild.italics import condenseGlyph, transformFLGlyphMembers

# Masters

rg = Master("%s/src/v2/Roboto_Regular.vfb"%BASEDIR)
bd = Master("%s/src/v2/Roboto_Bold.vfb"%BASEDIR)
th = Master("%s/src/v2/Roboto_Thin.vfb"%BASEDIR)

# build condensed masters

condensed = Font(th.font)

lessCondensed = "plusminus \
bracketleft bracketright dieresis \
macron percent \
multiply degree at i j zero one two \
three four five six seven eight nine braceright braceleft".split()
uncondensed = "tonos breve acute grave quotesingle quotedbl asterisk \
period currency registered copyright bullet ring degree dieresis comma bar brokenbar dotaccent \
dotbelow colon semicolon uniFFFC uniFFFD uni0488 uni0489 ringbelow estimated".split()
moreCondensed = "z Z M W A V".split()


def condenseFont(font, scale=.8, stemWidth=185):
    f = RFont(font)
    
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
proj.incrementBuildNumber()

# FAMILYNAME = "Roboto 2 DRAFT"
# FAMILYNAME = "Roboto2"
FAMILYNAME = "Roboto"

proj.generateFont(th.font,"%s/Thin/Regular/Th"%FAMILYNAME)
proj.generateFont(Mix([th,rg], 0.45),"%s/Light/Regular/Lt"%FAMILYNAME)
proj.generateFont(Mix([th,rg], Point(0.90, 0.92)),"%s/Regular/Regular/Rg"%FAMILYNAME)
proj.generateFont(Mix([rg,bd], 0.35),"%s/Medium/Regular/Lt"%FAMILYNAME)
proj.generateFont(Mix([rg,bd], Point(0.73, 0.73)),"%s/Bold/Bold/Rg"%FAMILYNAME)
proj.generateFont(Mix([rg,bd], Point(1.125, 1.0)),"%s/Black/Bold/Bk"%FAMILYNAME)

proj.generateFont(th.font,"%s/Thin Italic/Italic/Th"%FAMILYNAME, italic=True, stemWidth=80)
proj.generateFont(Mix([th,rg], 0.45),"%s/Light Italic/Italic/Lt"%FAMILYNAME, italic=True, stemWidth=120)
proj.generateFont(Mix([th,rg], Point(0.90, 0.92)),"%s/Italic/Italic/Rg"%FAMILYNAME, italic=True, stemWidth=185)
proj.generateFont(Mix([rg,bd], 0.35),"%s/Medium Italic/Bold Italic/Lt"%FAMILYNAME, italic=True, stemWidth=230)
proj.generateFont(Mix([rg,bd], Point(0.73, 0.73)),"%s/Bold Italic/Bold Italic/Rg"%FAMILYNAME, italic=True, stemWidth=290)
proj.generateFont(Mix([rg,bd], Point(1.125, 1.0)),"%s/Black Italic/Bold Italic/Bk"%FAMILYNAME, italic=True, stemWidth=290)

thcn1 = Master(condenseFont(Font(th.font), .84, 40).naked())
cn1 = Master( rg.ffont.addDiff(thcn1.ffont, th.ffont))
bdcn1 = Master( bd.ffont.addDiff(thcn1.ffont, th.ffont))

proj.generateFont(Mix([thcn1,cn1], Point(0.45, 0.47)), "%s Condensed/Light/Regular/Lt"%FAMILYNAME, swapSuffixes=[".cn"])
proj.generateFont(Mix([thcn1,cn1], Point(0.9, 0.92)), "%s Condensed/Regular/Regular/Rg"%FAMILYNAME, swapSuffixes=[".cn"])
proj.generateFont(Mix([cn1,bdcn1], Point(0.75, 0.75)), "%s Condensed/Bold/Bold/Rg"%FAMILYNAME, swapSuffixes=[".cn"])

proj.generateFont(Mix([thcn1,cn1], Point(0.45, 0.47)), "%s Condensed/Light Italic/Italic/Lt"%FAMILYNAME, italic=True, swapSuffixes=[".cn"], stemWidth=120)
proj.generateFont(Mix([thcn1,cn1], Point(0.9, 0.92)), "%s Condensed/Italic/Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".cn"], stemWidth=185)
proj.generateFont(Mix([cn1,bdcn1], Point(0.75, 0.75)), "%s Condensed/Bold Italic/Bold Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".cn"], stemWidth=240)

for i in range(len(fl)):
    fl.Close(0)
    
sys.exit(0)



## Old stuff

# for g in condensed.glyphs:
#     scaleX = .78
#     marginX = 25
#     if g.name in lessCondensed:
#         transformGlyphMembers(g, Matrix(scaleX * 1.15,0,0,1,marginX,0))
#     elif g.name in moreCondensed:
#         transformGlyphMembers(g, Matrix(scaleX * .95,0,0,1,marginX,0))
#     else:
#         transformGlyphMembers(g, Matrix(scaleX,0,0,1,marginX,0))
#     g.width += marginX * 2
# cn = Master(condensed)
# 
# 
# bdcn = Master( bd.ffont.addDiff(cn.ffont, th.ffont))
# rgcn = Master( rg.ffont.addDiff(cn.ffont, th.ffont))
# cn1 = Master(Mix([th, rgcn], Point(.7,.7)).generateFFont())
# bdcn1 = Master(Mix([bd, bdcn], Point(.7,.7)).generateFFont())

# cn1 = Master(condenseFont(Font(rg.font), .82, 180).naked())
# bdcn1 = Master(condenseFont(Font(bd.font), .82, 320).naked())

# proj.generateFont(Mix([cn1, bdcn1], Point(0.22, 0.2)), "%s Condensed/Regular/Regular/Rg"%FAMILYNAME, swapSuffixes=[".cnn"])
# proj.generateFont(Mix([cn1, bdcn1], Point(0.22, 0.2)), "%s Condensed/Italic/Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".cn",".it"])
# 
# proj.generateFont(Mix([cn1, bdcn1], Point(.80, .75)), "%s Condensed/Bold/Bold/Rg"%FAMILYNAME, swapSuffixes=[".cnn"])
# proj.generateFont(Mix([cn1, bdcn1], Point(.80, .75)), "%s Condensed/Bold Italic/Bold Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".cn",".it"])
# 
# proj.generateFont(Mix([cn, cn1], Point(.74, .72)), "%s Condensed/Light/Regular/Lt"%FAMILYNAME, swapSuffixes=[".cnn"])
# proj.generateFont(Mix([cn, cn1], Point(.74, .72)), "%s Condensed/Light Italic/Italic/Lt"%FAMILYNAME, italic=True, swapSuffixes=[".cn",".it"])

# wide = Mix([
#         Master(Mix([cn1, bdcn1], Point(0.22, 0.2)).generateFFont()),
#         Master(Mix([th,rg], Point(0.90, 0.92)).generateFFont())],
#         1.15)
# widebd = Mix([
#         Master(Mix([cn1, bdcn1], Point(.80, .75)).generateFFont()),
#         Master(Mix([rg,bd], Point(0.75, 0.7)).generateFFont())],
#         1.15)
# proj.generateFont(wide, "%s Wide/Regular/Regular/Rg" %FAMILYNAME , swapSuffixes=[".ss06"])
# proj.generateFont(wide,"%s Wide/Italic/Italic/Rg" %FAMILYNAME, italic=True, swapSuffixes=[".it", ".ss06"])
# proj.generateFont(widebd,"%s Wide/Bold/Bold/Rg"%FAMILYNAME, swapSuffixes=[".ss06"])
# proj.generateFont(widebd,"%s Wide/Bold Italic/Bold Italic/Rg"%FAMILYNAME, italic=True, swapSuffixes=[".it", ".ss06"])


