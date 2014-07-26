import sys
from math import *

from Numeric import *
import LinearAlgebra as la

import poly3

n = 15
m = zeros(((n + 1) * 4, (n + 1) * 4), Float)
for i in range(n):
    m[4 * i + 2][4 * i + 0] = .5
    m[4 * i + 2][4 * i + 1] = -1./12
    m[4 * i + 2][4 * i + 2] = 1./48
    m[4 * i + 2][4 * i + 3] = -1./480
    m[4 * i + 2][4 * i + 4] = .5
    m[4 * i + 2][4 * i + 5] = 1./12
    m[4 * i + 2][4 * i + 6] = 1./48
    m[4 * i + 2][4 * i + 7] = 1./480

    m[4 * i + 3][4 * i + 0] = 1
    m[4 * i + 3][4 * i + 1] = .5
    m[4 * i + 3][4 * i + 2] = .125
    m[4 * i + 3][4 * i + 3] = 1./48
    m[4 * i + 3][4 * i + 4] = -1
    m[4 * i + 3][4 * i + 5] = .5
    m[4 * i + 3][4 * i + 6] = -.125
    m[4 * i + 3][4 * i + 7] = 1./48

    m[4 * i + 4][4 * i + 0] = 0
    m[4 * i + 4][4 * i + 1] = 1
    m[4 * i + 4][4 * i + 2] = .5
    m[4 * i + 4][4 * i + 3] = .125
    m[4 * i + 4][4 * i + 4] = 0
    m[4 * i + 4][4 * i + 5] = -1
    m[4 * i + 4][4 * i + 6] = .5
    m[4 * i + 4][4 * i + 7] = -.125

    m[4 * i + 5][4 * i + 0] = 0
    m[4 * i + 5][4 * i + 1] = 0
    m[4 * i + 5][4 * i + 2] = 1
    m[4 * i + 5][4 * i + 3] = .5
    m[4 * i + 5][4 * i + 4] = 0
    m[4 * i + 5][4 * i + 5] = 0
    m[4 * i + 5][4 * i + 6] = -1
    m[4 * i + 5][4 * i + 7] = .5

m[n * 4 + 2][2] = 1
m[n * 4 + 3][3] = 1

m[0][n * 4 + 2] = 1
m[1][n * 4 + 3] = 1

def printarr(m):
    for j in range(n * 4 + 4):
        for i in range(n * 4 + 4):
            print '%6.1f' % m[j][i],
        print ''

sys.output_line_width = 160
#print array2string(m, precision = 3)
mi = la.inverse(m)
#printarr(mi)

# fit arc to pts (0, 0), (x, y), and (1, 0), return th tangent to
# arc at (x, y)
def fit_arc(x, y):
    th = atan2(y - 2 * x * y, y * y + x - x * x)
    return th

def mod_2pi(th):
    u = th / (2 * pi)
    return 2 * pi * (u - floor(u + 0.5))

def plot_path(path, th, k):
    if path[0][2] == '{': closed = 0
    else: closed = 1
    j = 0
    cmd = 'moveto'
    for i in range(len(path) + closed - 1):
        i1 = (i + 1) % len(path)
        x0, y0, t0 = path[i]
        x1, y1, t1 = path[i1]
        j1 = (j + 1) % len(th)
        th0 = th[j]
        k0 = k[j]
        th1 = th[j1]
        k1 = k[j1]
        chord_th = atan2(y1 - y0, x1 - x0)
        chord_len = hypot(y1 - y0, x1 - x0)
        ks = poly3.solve_3spiro(mod_2pi(chord_th - th0),
                                mod_2pi(th1 - chord_th),
                                k0 * chord_len, k1 * chord_len)
        ksp = (ks[0] * .5, ks[1] * .25, ks[2] * .125, ks[3] * .0625)
        pside = poly3.int_3spiro_poly(ksp, 64)
        ksm = (ks[0] * -.5, ks[1] * .25, ks[2] * -.125, ks[3] * .0625)
        mside = poly3.int_3spiro_poly(ksm, 64)
        mside.reverse()
        for i in range(len(mside)):
            mside[i] = (-mside[i][0], -mside[i][1])
        pts = mside + pside[1:]
        rot = chord_th - atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0])
        scale = hypot(x1 - x0, y1 - y0) / hypot(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0])
        u, v = scale * cos(rot), scale * sin(rot)
        xt = x0 - u * pts[0][0] + v * pts[0][1]
        yt = y0 - u * pts[0][1] - v * pts[0][0]
        for x, y in pts:
            print xt + u * x - v * y, yt + u * y + v * x, cmd
            cmd = 'lineto'
        if t1 == 'v':
            j += 2
        else:
            j += 1
    print 'stroke'
    if 0:
        j = 0
        for i in range(len(path)):
            x0, y0, t0 = path[i]
            print 'gsave', x0, y0, 'translate'
            print ' ', th[j] * 180 / pi, 'rotate'
            print '  -50 0 moveto 50 0 lineto stroke'
            print 'grestore'
            j += 1

def plot_ks(path, th, k):
    if path[0][2] == '{': closed = 0
    else: closed = 1
    j = 0
    cmd = 'moveto'
    xo = 36
    yo = 550
    xscale = .5
    yscale = 2000
    x = xo
    for i in range(len(path) + closed - 1):
        i1 = (i + 1) % len(path)
        x0, y0, t0 = path[i]
        x1, y1, t1 = path[i1]
        j1 = (j + 1) % len(th)
        th0 = th[j]
        k0 = k[j]
        th1 = th[j1]
        k1 = k[j1]
        chord_th = atan2(y1 - y0, x1 - x0)
        chord_len = hypot(y1 - y0, x1 - x0)
        ks = poly3.solve_3spiro(mod_2pi(chord_th - th0),
                                mod_2pi(th1 - chord_th),
                                k0 * chord_len, k1 * chord_len)
        ksp = (ks[0] * .5, ks[1] * .25, ks[2] * .125, ks[3] * .0625)
        pside = poly3.int_3spiro_poly(ksp, 64)
        ksm = (ks[0] * -.5, ks[1] * .25, ks[2] * -.125, ks[3] * .0625)
        mside = poly3.int_3spiro_poly(ksm, 64)
        print '%', x0, y0, k0, k1
        print "% ks = ", ks
        l = 2 * chord_len / hypot(pside[-1][0] + mside[-1][0], pside[-1][1] + mside[-1][1])
        for i in range(100):
            s = .01 * i - 0.5
            kp = poly3.eval_cubic(ks[0], ks[1], .5 * ks[2], 1./6 * ks[3], s)
            kp /= l
            print x + xscale * l * (s + .5), yo + yscale * kp, cmd
            cmd = 'lineto'
        x += xscale * l
        if t1 == 'v':
            j += 2
        else:
            j += 1
    print 'stroke'
    print xo, yo, 'moveto', x, yo, 'lineto stroke'

def make_error_vec(path, th, k):
    if path[0][2] == '{': closed = 0
    else: closed = 1
    n = len(path)
    v = zeros(n * 2, Float)
    j = 0
    for i in range(len(path) + closed - 1):
        i1 = (i + 1) % len(path)
        x0, y0, t0 = path[i]
        x1, y1, t1 = path[i1]
        j1 = (j + 1) % len(th)
        th0 = th[j]
        k0 = k[j]
        th1 = th[j1]
        k1 = k[j1]
        chord_th = atan2(y1 - y0, x1 - x0)
        chord_len = hypot(y1 - y0, x1 - x0)
        ks = poly3.solve_3spiro(mod_2pi(chord_th - th0),
                                mod_2pi(th1 - chord_th),
                                k0 * chord_len, k1 * chord_len)
        ksp = (ks[0] * .5, ks[1] * .25, ks[2] * .125, ks[3] * .0625)
        pside = poly3.int_3spiro_poly(ksp, 64)
        ksm = (ks[0] * -.5, ks[1] * .25, ks[2] * -.125, ks[3] * .0625)
        mside = poly3.int_3spiro_poly(ksm, 64)
        l = chord_len / hypot(pside[-1][0] + mside[-1][0], pside[-1][1] + mside[-1][1])
        k1l = (ks[1] - .5 * ks[2] + .125 * ks[3]) / (l * l)
        k1r = (ks[1] + .5 * ks[2] + .125 * ks[3]) / (l * l)
        k2l = (ks[2] - .5 * ks[3]) / (l * l * l)
        k2r = (ks[2] + .5 * ks[3]) / (l * l * l)

        if t0 == 'o' or t0 == '[' or t0 == 'v':
            v[2 * j] -= k1l
            v[2 * j + 1] -= k2l
        elif t0 == 'c':
            v[2 * j + 1] += k2l

        if t1 == 'o' or t1 == ']' or t1 == 'v':
            v[2 * j1] += k1r
            v[2 * j1 + 1] += k2r
        elif t1 == 'c':
            v[2 * j1] += k2r

        print "% left k'", k1l, "k''", k2l, "right k'", k1r, "k''", k2r
        if t1 == 'v':
            j += 2
        else:
            j += 1
    print '% error vector:'
    for i in range(n):
        print '%  ', v[2 * i], v[2 * i + 1]
    return v

def add_k1l(m, row, col, col1, l, s):
    l2 = l * l
    m[row][2 * col] += s * 36 / l2
    m[row][2 * col + 1] -= s * 9 / l
    m[row][2 * col1] += s * 24 / l2
    m[row][2 * col1 + 1] += s * 3 / l

def add_k1r(m, row, col, col1, l, s):
    l2 = l * l
    m[row][2 * col] += s * 24 / l2
    m[row][2 * col + 1] -= s * 3 / l
    m[row][2 * col1] += s * 36 / l2
    m[row][2 * col1 + 1] += s * 9 / l

def add_k2l(m, row, col, col1, l, s):
    l2 = l * l
    l3 = l2 * l
    m[row][2 * col] -= s * 192 / l3
    m[row][2 * col + 1] += s * 36 / l2
    m[row][2 * col1] -= s * 168 / l3
    m[row][2 * col1 + 1] -= s * 24 / l2

def add_k2r(m, row, col, col1, l, s):
    l2 = l * l
    l3 = l2 * l
    m[row][2 * col] += s * 168 / l3
    m[row][2 * col + 1] -= s * 24 / l2
    m[row][2 * col1] += s * 192 / l3
    m[row][2 * col1 + 1] += s * 36 / l2

def make_matrix(path, th, k):
    if path[0][2] == '{': closed = 0
    else: closed = 1
    n = len(path)
    m = zeros((n * 2, n * 2), Float)
    j = 0
    for i in range(len(path) + closed - 1):
        i1 = (i + 1) % len(path)
        x0, y0, t0 = path[i]
        x1, y1, t1 = path[i1]
        j1 = (j + 1) % len(th)
        th0 = th[j]
        k0 = k[j]
        th1 = th[j1]
        k1 = k[j1]
        chord_th = atan2(y1 - y0, x1 - x0)
        chord_len = hypot(y1 - y0, x1 - x0)
        ks = poly3.solve_3spiro(mod_2pi(chord_th - th0),
                                mod_2pi(th1 - chord_th),
                                k0 * chord_len, k1 * chord_len)
        ksp = (ks[0] * .5, ks[1] * .25, ks[2] * .125, ks[3] * .0625)
        pside = poly3.int_3spiro_poly(ksp, 64)
        ksm = (ks[0] * -.5, ks[1] * .25, ks[2] * -.125, ks[3] * .0625)
        mside = poly3.int_3spiro_poly(ksm, 64)
        l = chord_len / hypot(pside[-1][0] + mside[-1][0], pside[-1][1] + mside[-1][1])

        if t0 == 'o' or t0 == '[' or t0 == 'v':
            add_k1l(m, 2 * j, j, j1, l, -1)
            add_k2l(m, 2 * j + 1, j, j1, l, -1)
        elif t0 == 'c':
            add_k2l(m, 2 * j + 1, j, j1, l, 1)

        if t1 == 'o' or t1 == ']' or t1 == 'v':
            add_k1r(m, 2 * j1, j, j1, l, 1)
            add_k2r(m, 2 * j1 + 1, j, j1, l, 1)
        elif t1 == 'c':
            add_k2r(m, 2 * j1, j, j1, l, 1)

        if t1 == 'v':
            j += 2
        else:
            j += 1
    return m

def solve(path):
    if path[0][2] == '{': closed = 0
    else: closed = 1
    dxs = []
    dys = []
    chords = []
    for i in range(len(path) - 1):
        dxs.append(path[i + 1][0] - path[i][0])
        dys.append(path[i + 1][1] - path[i][1])
        chords.append(hypot(dxs[-1], dys[-1]))
    nominal_th = []
    nominal_k = []
    if not closed:
        nominal_th.append(atan2(dys[0], dxs[0]))
        nominal_k.append(0)
    for i in range(1 - closed, len(path) - 1 + closed):
        x0, y0, t0 = path[(i + len(path) - 1) % len(path)]
        x1, y1, t1 = path[i]
        x2, y2, t2 = path[(i + 1) % len(path)]
        dx = float(x2 - x0)
        dy = float(y2 - y0)
        ir2 = dx * dx + dy * dy
        x = ((x1 - x0) * dx + (y1 - y0) * dy) / ir2
        y = ((y1 - y0) * dx - (x1 - x0) * dy) / ir2
        th = fit_arc(x, y) + atan2(dy, dx)
        bend_angle = mod_2pi(atan2(y2 - y1, x2 - x1) - atan2(y1 - y0, x1 - x0))
        k = 2 * bend_angle/(hypot(y2 - y1, x2 - x1) + hypot(y1 - y0, x1 - x0))
        print '% bend angle', bend_angle, 'k', k
        if t1 == ']':
            th = atan2(y1 - y0, x1 - x0)
            k = 0
        elif t1 == '[':
            th = atan2(y2 - y1, x2 - x1)
            k = 0
        nominal_th.append(th)
        nominal_k.append(k)
    if not closed:
        nominal_th.append(atan2(dys[-1], dxs[-1]))
        nominal_k.append(0)
    print '%', nominal_th
    print '0 0 1 setrgbcolor .5 setlinewidth'
    plot_path(path, nominal_th, nominal_k)
    plot_ks(path, nominal_th, nominal_k)
    th = nominal_th[:]
    k = nominal_k[:]
    n = 8
    for i in range(n):
        ev = make_error_vec(path, th, k)
        m = make_matrix(path, th, k)
        #print m
        #print 'inverse:'
        #print la.inverse(m)
        v = dot(la.inverse(m), ev)
        #print v
        for j in range(len(path)):
            th[j] += 1. * v[2 * j]
            k[j] -= 1. * .5 * v[2 * j + 1]
        if i == n - 1:
            print '0 0 0 setrgbcolor 1 setlinewidth'
        elif i == 0:
            print '1 0 0 setrgbcolor'
        elif i == 1:
            print '0 0.5 0 setrgbcolor'
        elif i == 2:
            print '0.3 0.3 0.3 setrgbcolor'
        plot_path(path, th, k)
        plot_ks(path, th, k)
    print '% th:', th
    print '% k:', k

path = [(100, 100, 'o'), (200, 250, 'o'), (350, 225, 'o'),
         (450, 350, 'c'), (450, 200, 'o'), (300, 100, 'o')]
if 0:
 path = [(100, 480, '['), (100, 300, ']'), (300, 100, 'o'),
        (500, 300, '['), (500, 480, ']'), (480, 500, '['),
        (120, 500, ']')]


path = [(100, 480, ']'), (100, 120, '['),
        (120, 100, ']'), (480, 100, '['),
        (500, 120, ']'), (500, 480, '['),
        (480, 500, ']'), (120, 500, '[')]

path = [(100, 120, '['), (120, 100, ']'),
        (140, 100, 'o'), (160, 100, 'o'), (180, 100, 'o'), (200, 100, 'o'),
        (250, 250, 'o'),
        (100, 200, 'o'), (100, 180, 'o'), (100, 160, 'o'), (100, 140, 'o')]

path = [(100, 350, 'o'), (225, 350, 'o'), (350, 450, 'o'),
        (450, 400, 'o'), (315, 205, 'o'), (300, 200, 'o'),
        (285, 205, 'o')]

if 0:
    path = []
    path.append((350, 600, 'c'))
    path.append((50, 450, 'c'))
    for i in range(10):
        path.append((50 + i * 30, 300 - i * 5, 'c'))
    for i in range(11):
        path.append((350 + i * 30, 250 + i * 5, 'c'))
    path.append((650, 450, 'c'))

solve(path)
print 'showpage'
