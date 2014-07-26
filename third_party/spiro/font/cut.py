import sys

athresh = 100
border = 20

segf = sys.argv[1]
if len(sys.argv) > 2:
    pref = sys.argv[2]
else:
    pref = '/tmp/cut'
rects = []
starts = {}
for l in file(segf).xreadlines():
    ls = l.split()
    if len(ls) == 6 and ls[-1] == 'rect':
        r = map(int, ls[:4])
        area = (r[2] - r[0]) * (r[3] - r[1])
        if area > athresh:
            rpad = [r[0] - border, r[1] - border, r[2] + border, r[3] + border]
            if not starts.has_key(rpad[1]):
                starts[rpad[1]] = []
            starts[rpad[1]].append(len(rects))
            rects.append(rpad)
inf = sys.stdin
l = inf.readline()
if l != 'P5\n':
    raise 'expected pgm file'
while 1:
    l = inf.readline()
    if l[0] != '#': break
x, y = map(int, l.split())
l = inf.readline()

active = {}
for j in range(y):
    if starts.has_key(j):
        for ix in starts[j]:
            r = rects[ix]
            ofn = pref + '%04d.pgm' % ix
            of = file(ofn, 'w')
            active[ix] = of
            print >> of, 'P5'
            print >> of, r[2] - r[0], r[3] - r[1]
            print >> of, '255'
    buf = inf.read(x)
    for ix, of in active.items():
        r = rects[ix]
        of.write(buf[r[0]:r[2]])
        if j == r[3] - 1:
            of.close()
            del active[ix]

