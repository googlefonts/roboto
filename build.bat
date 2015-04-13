# Modify this to point to local Python executable
set PYTHONEXE="C:\Python27\Python.exe"

echo BASEDIR=r"%cd%" > tmp-makefontsB.py
type scripts\build-v2.py >> tmp-makefontsB.py
set PYTHONPATH=%cd%\scripts\lib
%PYTHONEXE% tmp-makefontsB.py
del tmp-makefontsB.py
