
import sys
sys.path.insert(0,"%s/scripts/lib"%BASEDIR)

from fontbuild.Build import FontProject,swapGlyphs,transformGlyphMembers
from fontbuild.mix import Mix,Master

# Masters

rg = Master("%s/src/sans/Roboto_Regular.vfb"%BASEDIR)
bd = Master("%s/src/sans/Roboto_Bold.vfb"%BASEDIR)
th = Master("%s/src/sans/Roboto_Thin.vfb"%BASEDIR)

# build condensed masters

condensed = Font(th.font)

lessCondensed = "plusminus \
quotesingle quotedbl bracketleft bracketright ampersand acute grave dieresis \
macron breve asterisk ring plus percent bullet currency registered copyright \
multiply degree at".split()
moreCondensed = "Z M W T U Y z".split()

for g in condensed.glyphs:
    scaleX = .72
    marginX = 18
    if g.name in lessCondensed:
        transformGlyphMembers(g, Matrix(scaleX * 1.07,0,0,1,marginX,0))
    elif g.name in moreCondensed:
        transformGlyphMembers(g, Matrix(scaleX * .95,0,0,1,marginX,0))
    else:
        transformGlyphMembers(g, Matrix(scaleX,0,0,1,marginX,0))
    g.width += marginX * 2
cn = Master(condensed)

bdcn = Master( bd.ffont.addDiff(cn.ffont, th.ffont))
rgcn = Master( rg.ffont.addDiff(cn.ffont, th.ffont))
cn1 = Master(Mix([th, rgcn], Point(.7,.7)).generateFFont())
bdcn1 = Master(Mix([bd, bdcn], Point(.7,.7)).generateFFont())

proj = FontProject(rg.font, BASEDIR, "res/roboto.cfg", th.ffont)
proj.incrementBuildNumber()

proj.generateFont(th.font,"Roboto/Thin/Regular/Th")
proj.generateFont(th.font,"Roboto/Thin Italic/Italic/Th", italic=True, swapSuffixes=[".it"])

proj.generateFont(Mix([th,rg], 0.45),"Roboto/Light/Regular/Lt")
proj.generateFont(Mix([th,rg], 0.45),"Roboto/Light Italic/Italic/Lt", italic=True, swapSuffixes=[".it"])

proj.generateFont(Mix([th,rg], Point(0.90, 0.90)),"Roboto/Regular/Regular/Rg")
proj.generateFont(Mix([th,rg], Point(0.90, 0.90)),"Roboto/Italic/Italic/Rg", italic=True, swapSuffixes=[".it"])

proj.generateFont(Mix([rg,bd], 0.35),"Roboto/Medium/Regular/Lt")
proj.generateFont(Mix([rg,bd], 0.35),"Roboto/Medium Italic/Bold Italic/Lt", italic=True, swapSuffixes=[".it"])

proj.generateFont(Mix([rg,bd], Point(0.75, 0.65)),"Roboto/Bold/Bold/Rg")
proj.generateFont(Mix([rg,bd], Point(0.75, 0.65)),"Roboto/Bold Italic/Bold Italic/Rg", italic=True, swapSuffixes=[".it"])

proj.generateFont(Mix([rg,bd], Point(1.125, 1.0)),"Roboto/Black/Bold/Bk")
proj.generateFont(Mix([rg,bd], Point(1.125, 1.0)),"Roboto/Black Italic/Bold Italic/Bk", italic=True, swapSuffixes=[".it"])

proj.generateFont(Mix([cn1, bdcn1], Point(0.33, 0.2)), "Roboto Condensed/Regular/Regular/Rg", swapSuffixes=[".cn"])
proj.generateFont(Mix([cn1, bdcn1], Point(0.33, 0.2)), "Roboto Condensed/Italic/Italic/Rg", italic=True, swapSuffixes=[".cn",".it"])

proj.generateFont(Mix([cn1, bdcn1], Point(.80, .75)), "Roboto Condensed/Bold/Bold/Rg", swapSuffixes=[".cn"])
proj.generateFont(Mix([cn1, bdcn1], Point(.80, .75)), "Roboto Condensed/Bold Italic/Bold Italic/Rg", italic=True, swapSuffixes=[".cn",".it"])

proj.generateFont(Mix([cn, cn1], Point(.74, .72)), "Roboto Condensed/Light/Regular/Lt", swapSuffixes=[".cn"])
proj.generateFont(Mix([cn, cn1], Point(.74, .72)), "Roboto Condensed/Light Italic/Italic/Lt", italic=True, swapSuffixes=[".cn",".it"])

for i in range(len(fl)):
    fl.Close(0)
    
sys.exit(0)
