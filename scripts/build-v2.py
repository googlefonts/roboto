import sys

sys.path.insert(0,"%s/scripts/lib"%BASEDIR)

from robofab.objects.objectsRF import RPoint
from fontbuild.Build import FontProject
from fontbuild.mix import Mix,Master

# Masters

rg = Master("%s/src/v2/Roboto_Regular.ufo"%BASEDIR)
bd = Master("%s/src/v2/Roboto_Bold.ufo"%BASEDIR)
th = Master("%s/src/v2/Roboto_Thin.ufo"%BASEDIR)

proj = FontProject(rg.font, BASEDIR, "res/roboto.cfg", th.ffont)
#proj.incrementBuildNumber()

# FAMILYNAME = "Roboto 2 DRAFT"
# FAMILYNAME = "Roboto2"
FAMILYNAME = "Roboto"

proj.buildOTF = True
#proj.checkOTFOutlines = True
#proj.autohintOTF = True
proj.buildTTF = True
proj.buildFEA = True

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

sys.exit(0)
