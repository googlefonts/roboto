import re

def markKernClassesLR(f):
    for i in range(len(f.classes)):
        classname = f.classes[i].split(':', 1).pop(0).strip()
        if classname.startswith('_'):
            l = 0
            r = 0
            if classname.endswith('_L'):
                l = 1
            elif classname.endswith('_R'):
                r = 1
            elif classname.endswith('_LR'):
                l = 1
                r = 1
            f.SetClassFlags(i, l, r)
    fl.UpdateFont()

def generateFLKernClassesFromOTString(f,classString):
    classString.replace("\r","\n")
    rx = re.compile(r"@(_[\w]+)\s*=\s*\[\s*(\w+?)\s+(.*?)\]\s*;")
    classes = ["%s : %s' %s" %(m[0],m[1],m[2]) for m in rx.findall(classString)]
    f.classes = classes    
    markKernClassesLR(f)

