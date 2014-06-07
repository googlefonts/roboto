import sys
sys.path.insert(0,"%s/scripts/lib"%BASEDIR)

from fontbuild.Build import FontProject,swapGlyphs,transformGlyphMembers
from fontbuild.mix import Mix,Master

# Masters

# rg_slab = Master("%s/src/slab/RobotoSlab_Regular.vfb"%BASEDIR)
# bd_slab = Master("%s/src/slab/RobotoSlab_Bold.vfb"%BASEDIR)
# th_slab = Master("%s/src/slab/RobotoSlab_Thin.vfb"%BASEDIR)
# 
# proj = FontProject(rg_slab.font, BASEDIR, "res/roboto.cfg", th_slab.ffont)
# proj.generateFont(Mix([th_slab,rg_slab], 0.0),"Roboto Slab/Thin/Regular/Th")
# proj.generateFont(Mix([th_slab,rg_slab], 0.45),"Roboto Slab/Light/Regular/Lt")
# proj.generateFont(Mix([th_slab,rg_slab], Point(0.90, 0.90)),"Roboto Slab/Regular/Regular/Rg")
# proj.generateFont(Mix([rg_slab,bd_slab], 0.35),"Roboto Slab/Medium/Regular/Lt")
# proj.generateFont(Mix([rg_slab,bd_slab], Point(0.75, 0.65)),"Roboto Slab/Bold/Bold/Rg")
# 
# for i in range(len(fl)):
#     fl.Close(0)
#     
rg_slab = Master("%s/src/Slab/RobotoSlab_Regular.vfb"%BASEDIR,overlay="%s/src/Slab/RobotoSlab__Italic.vfb"%BASEDIR)
bd_slab = Master("%s/src/Slab/RobotoSlab_Bold.vfb"%BASEDIR,overlay="%s/src/Slab/RobotoSlab__ItalicBold.vfb"%BASEDIR)
th_slab = Master("%s/src/Slab/RobotoSlab_Thin.vfb"%BASEDIR,overlay="%s/src/Slab/RobotoSlab__ItalicThin.vfb"%BASEDIR)

proj = FontProject(rg_slab.font, BASEDIR, "res/roboto.cfg", th_slab.ffont)

proj.generateFont(Mix([th_slab,rg_slab], 0.0),"Roboto Slab/Thin Italic/Italic/Th",italic=True)
proj.generateFont(Mix([th_slab,rg_slab], 0.45),"Roboto Slab/Light Italic/Italic/Lt",italic=True)
proj.generateFont(Mix([th_slab,rg_slab], Point(0.90, 0.90)),"Roboto Slab/Italic/Italic/Rg",italic=True)
proj.generateFont(Mix([rg_slab,bd_slab], 0.35),"Roboto Slab/Medium Italic/Bold Italic/Lt",italic=True)
proj.generateFont(Mix([rg_slab,bd_slab], Point(0.75, 0.65)),"Roboto Slab/Bold Italic/Bold Italic/Rg",italic=True)

for i in range(len(fl)):
    fl.Close(0)

sys.exit(0)