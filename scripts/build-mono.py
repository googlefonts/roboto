
import sys
sys.path.insert(0,"%s/scripts/lib"%BASEDIR)

from fontbuild.Build import FontProject
from fontbuild.mix import Mix,Master

# Masters

mn = Master("%s/src/mono/Roboto_Mono.vfb"%BASEDIR)
proj = FontProject(mn.font, BASEDIR, "res/roboto.cfg", mn.ffont)
proj.generateFont(mn.font,"Roboto Mono/Regular/Regular/Rg", kern=False)
proj.generateFont(mn.font,"Roboto Mono/Italic/Italic/Rg", italic=True, stemWidth=180, kern=False)



# for i in range(len(fl)):
    # fl.Close(0)

# sys.exit(0)