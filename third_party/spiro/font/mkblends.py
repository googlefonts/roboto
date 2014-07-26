import os, sys

glyphmap = {}
for ln in file(sys.argv[1]).xreadlines():
    fnglyph = ln.strip().split(': ')
    if len(fnglyph) == 2:
        fn, name = fnglyph
        pgmf = fn[:-4] + '.pgm'
        if not glyphmap.has_key(name):
            glyphmap[name] = []
        glyphmap[name].append(pgmf)
for name in glyphmap.iterkeys():
    cmd = '~/garden/font/blend ' + ' '.join(glyphmap[name]) + ' | pnmtopng > ' + name + '.png'
    print cmd
    os.system(cmd)

