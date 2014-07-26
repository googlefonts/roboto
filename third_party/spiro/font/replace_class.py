#!/usr/bin/env python

import sys
srfile = file(sys.argv[1])
table = {}
for line in srfile.xreadlines():
    clas, repl = line.split()
    if repl[-1] not in '-?':
        table['class' + clas] = repl

for line in sys.stdin.xreadlines():
    fn, clas = line.split()
    if table.has_key(clas):
        print fn, table[clas]
