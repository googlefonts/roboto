# Modify this to point to local Fontlab executable
set FONTLAB="C:\Program Files (x86)\Fontlab\Studio 5\Studio 5.exe"

echo BASEDIR=r"%cd%" > tmp-makefontsB.flw
type scripts\build-v2.py >> tmp-makefontsB.flw
set PYTHONPATH=%cd%\scripts\lib
%FONTLAB% tmp-makefontsB.flw
del tmp-makefontsB.flw
