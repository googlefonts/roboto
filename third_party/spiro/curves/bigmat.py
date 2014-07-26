# Solver based on direct Newton solving of 4 parameters for each curve
# segment

import sys
from math import *

from Numeric import *
import LinearAlgebra as la

import poly3
import band

class Seg:
    def __init__(self, chord, th):
        self.ks = [0., 0., 0., 0.]
        self.chord = chord
        self.th = th
    def compute_ends(self, ks):
        chord, ch_th = poly3.integ_chord(ks)
        l = chord / self.chord
        thl = ch_th - (-.5 * ks[0] + .125 * ks[1] - 1./48 * ks[2] + 1./384 * ks[3])
        thr = (.5 * ks[0] + .125 * ks[1] + 1./48 * ks[2] + 1./384 * ks[3]) - ch_th
        k0l = l * (ks[0] - .5 * ks[1] + .125 * ks[2] - 1./48 * ks[3])
        k0r = l * (ks[0] + .5 * ks[1] + .125 * ks[2] + 1./48 * ks[3])
        l2 = l * l
        k1l = l2 * (ks[1] - .5 * ks[2] + .125 * ks[3])
        k1r = l2 * (ks[1] + .5 * ks[2] + .125 * ks[3])
        l3 = l2 * l
        k2l = l3 * (ks[2] - .5 * ks[3])
        k2r = l3 * (ks[2] + .5 * ks[3])
        return (thl, k0l, k1l, k2l), (thr, k0r, k1r, k2r), l
    def set_ends_from_ks(self):
        self.endl, self.endr, self.l = self.compute_ends(self.ks)
    def fast_pderivs(self):
        l = self.l
        l2 = l * l
        l3 = l2 * l
        return [((.5, l, 0, 0), (.5, l, 0, 0)),
                ((-1./12, -l/2, l2, 0), (1./12, l/2, l2, 0)),
                ((1./48, l/8, -l2/2, l3), (1./48, l/8, l2/2, l3)),
                ((-1./480, -l/48, l2/8, -l3/2), (1./480, l/48, l2/8, l3/2))]
    def compute_pderivs(self):
        rd = 2e6
        delta = 1./rd
        base_ks = self.ks
        base_endl, base_endr, dummy = self.compute_ends(base_ks)
        result = []
        for i in range(4):
            try_ks = base_ks[:]
            try_ks[i] += delta
            try_endl, try_endr, dummy = self.compute_ends(try_ks)
            deriv_l = (rd * (try_endl[0] - base_endl[0]),
                       rd * (try_endl[1] - base_endl[1]),
                       rd * (try_endl[2] - base_endl[2]),
                       rd * (try_endl[3] - base_endl[3]))
            deriv_r = (rd * (try_endr[0] - base_endr[0]),
                       rd * (try_endr[1] - base_endr[1]),
                       rd * (try_endr[2] - base_endr[2]),
                       rd * (try_endr[3] - base_endr[3]))
            result.append((deriv_l, deriv_r))
        return result

class Node:
    def __init__(self, x, y, ty, th):
        self.x = x
        self.y = y
        self.ty = ty
        self.th = th
    def continuity(self):
        if self.ty == 'o':
            return 4
        elif self.ty in ('c', '[', ']'):
            return 2
        else:
            return 0

def mod_2pi(th):
    u = th / (2 * pi)
    return 2 * pi * (u - floor(u + 0.5))

def setup_path(path):
    segs = []
    nodes = []
    nsegs = len(path)
    if path[0][2] == '{':
        nsegs -= 1
    for i in range(nsegs):
        i1 = (i + 1) % len(path)
        x0, y0, t0 = path[i]
        x1, y1, t1 = path[i1]
        s = Seg(hypot(y1 - y0, x1 - x0), atan2(y1 - y0, x1 - x0))
        segs.append(s)
    for i in range(len(path)):
        x0, y0, t0 = path[i]

        if t0 in ('{', '}', 'v'):
            th = 0
        else:
            s0 = segs[(i + len(path) - 1) % len(path)]
            s1 = segs[i]
            th = mod_2pi(s1.th - s0.th)

        n = Node(x0, y0, t0, th)
        nodes.append(n)
    return segs, nodes

def count_vec(nodes):
    jincs = []
    n = 0
    for i in range(len(nodes)):
        i1 = (i + 1) % len(nodes)
        t0 = nodes[i].ty
        t1 = nodes[i1].ty
        if t0 in ('{', '}', 'v', '[') and t1 in ('{', '}', 'v', ']'):
            jinc = 0
        elif t0 in ('{', '}', 'v', '[') and t1 == 'c':
            jinc = 1
        elif t0 == 'c' and t1 in ('{', '}', 'v', ']'):
            jinc = 1
        elif t0 == 'c' and t1 == 'c':
            jinc = 2
        else:
            jinc = 4
        jincs.append(jinc)
        n += jinc
    return n, jincs

thscale, k0scale, k1scale, k2scale = 1, 1, 1, 1

def inversedot_woodbury(m, v):
    a = zeros((n, 11), Float)
    for i in range(n):
        for j in range(max(-7, -i), min(4, n - i)):
            a[i, j + 7] = m[i, i + j]
    print a
    al, indx, d = band.bandec(a, 7, 3)
    VtZ = identity(4, Float)
    Z = zeros((n, 4), Float)
    for i in range(4):
        u = zeros(n, Float)
        for j in range(4):
            u[j] = m[j, n - 4 + i]
        band.banbks(a, 7, 3, al, indx, u)
        for k in range(n):
            Z[k, i] = u[k]
        #Z[:,i] = u
        for j in range(4):
            VtZ[j, i] += u[n - 4 + j]
    print Z
    print VtZ
    H = la.inverse(VtZ)
    print H
    band.banbks(a, 7, 3, al, indx, v)
    return(v - dot(Z, dot(H, v[n - 4:])))

def inversedot(m, v):
    return dot(la.inverse(m), v)
    n, nn = m.shape
    if 1:
        for i in range(n):
            sys.stdout.write('% ')
            for j in range(n):
                if m[i, j] > 0: sys.stdout.write('+ ')
                elif m[i, j] < 0: sys.stdout.write('- ')
                else: sys.stdout.write('  ')
            sys.stdout.write('\n')

    cyclic = False
    for i in range(4):
        for j in range(n - 4, n):
            if m[i, j] != 0:
                cyclic = True
    print '% cyclic:', cyclic
    if not cyclic:
        a = zeros((n, 11), Float)
        for i in range(n):
            for j in range(max(-5, -i), min(6, n - i)):
                a[i, j + 5] = m[i, i + j]
        for i in range(n):
            sys.stdout.write('% ')
            for j in range(11):
                if a[i, j] > 0: sys.stdout.write('+ ')
                elif a[i, j] < 0: sys.stdout.write('- ')
                else: sys.stdout.write('  ')
            sys.stdout.write('\n')
        al, indx, d = band.bandec(a, 5, 5)
        print a
        band.banbks(a, 5, 5, al, indx, v)
        return v
    else:
        #return inversedot_woodbury(m, v)
        bign = 3 * n
        a = zeros((bign, 11), Float)
        u = zeros(bign, Float)
        for i in range(bign):
            u[i] = v[i % n]
            for j in range(-7, 4):
                a[i, j + 7] = m[i % n, (i + j + 7 * n) % n]
        #print a
        if 1:
            for i in range(bign):
                sys.stdout.write('% ')
                for j in range(11):
                    if a[i, j] > 0: sys.stdout.write('+ ')
                    elif a[i, j] < 0: sys.stdout.write('- ')
                    else: sys.stdout.write('  ')
                sys.stdout.write('\n')
        #print u
        al, indx, d = band.bandec(a, 5, 5)
        band.banbks(a, 5, 5, al, indx, u)
        #print u
        return u[n + 2: 2 * n + 2]

def iter(segs, nodes):
    n, jincs = count_vec(nodes)
    print '%', jincs
    v = zeros(n, Float)
    m = zeros((n, n), Float)
    for i in range(len(segs)):
        segs[i].set_ends_from_ks()
    j = 0
    j0 = 0
    for i in range(len(segs)):
        i1 = (i + 1) % len(nodes)
        t0 = nodes[i].ty
        t1 = nodes[i1].ty
        seg = segs[i]

        derivs = seg.compute_pderivs()
        print '%derivs:', derivs

        jinc = jincs[i]   # the number of params on this seg
        print '%', t0, t1, jinc, j0

        # The constraints are laid out as follows:
        #   constraints that cross the node on the left
        #   constraints on the left side
        #   constraints on the right side
        #   constraints that cross the node on the right

        jj = j0    # the index into the constraint row we're writing
        jthl, jk0l, jk1l, jk2l = -1, -1, -1, -1
        jthr, jk0r, jk1r, jk2r = -1, -1, -1, -1

        # constraints crossing left

        if t0 == 'o':
            jthl = jj + 0
            jk0l = jj + 1
            jk1l = jj + 2
            jk2l = jj + 3
            jj += 4
        elif t0 in ('c', '[', ']'):
            jthl = jj + 0
            jk0l = jj + 1
            jj += 2

        # constraints on left

        if t0 in ('[', 'v', '{') and jinc == 4:
            jk1l = jj
            jj += 1
        if t0 in ('[', 'v', '{', 'c') and jinc == 4:
            jk2l = jj
            jj += 1

        # constraints on right

        if t1 in (']', 'v', '}') and jinc == 4:
            jk1r = jj
            jj += 1
        if t1 in (']', 'v', '}', 'c') and jinc == 4:
            jk2r = jj
            jj += 1

        # constraints crossing right

        jj %= n
        j1 = jj

        if t1 == 'o':
            jthr = jj + 0
            jk0r = jj + 1
            jk1r = jj + 2
            jk2r = jj + 3
            jj += 4
        elif t1 in ('c', '[', ']'):
            jthr = jj + 0
            jk0r = jj + 1
            jj += 2

        print '%', jthl, jk0l, jk1l, jk2l, jthr, jk0r, jk1r, jk2r

        if jthl >= 0:
            v[jthl] += thscale * (nodes[i].th - seg.endl[0])
            if jinc == 1:
                m[jthl][j] += derivs[0][0][0]
            elif jinc == 2:
                m[jthl][j + 1] += derivs[0][0][0]
                m[jthl][j] += derivs[1][0][0]
            elif jinc == 4:
                m[jthl][j + 2] += derivs[0][0][0]
                m[jthl][j + 3] += derivs[1][0][0]
                m[jthl][j + 0] += derivs[2][0][0]
                m[jthl][j + 1] += derivs[3][0][0]
        if jk0l >= 0:
            v[jk0l] += k0scale * seg.endl[1]
            if jinc == 1:
                m[jk0l][j] -= derivs[0][0][1]
            elif jinc == 2:
                m[jk0l][j + 1] -= derivs[0][0][1]
                m[jk0l][j] -= derivs[1][0][1]
            elif jinc == 4:
                m[jk0l][j + 2] -= derivs[0][0][1]
                m[jk0l][j + 3] -= derivs[1][0][1]
                m[jk0l][j + 0] -= derivs[2][0][1]
                m[jk0l][j + 1] -= derivs[3][0][1]
        if jk1l >= 0:
            v[jk1l] += k1scale * seg.endl[2]
            m[jk1l][j + 2] -= derivs[0][0][2]
            m[jk1l][j + 3] -= derivs[1][0][2]
            m[jk1l][j + 0] -= derivs[2][0][2]
            m[jk1l][j + 1] -= derivs[3][0][2]
        if jk2l >= 0:
            v[jk2l] += k2scale * seg.endl[3]
            m[jk2l][j + 2] -= derivs[0][0][3]
            m[jk2l][j + 3] -= derivs[1][0][3]
            m[jk2l][j + 0] -= derivs[2][0][3]
            m[jk2l][j + 1] -= derivs[3][0][3]

        if jthr >= 0:
            v[jthr] -= thscale * seg.endr[0]
            if jinc == 1:
                m[jthr][j] += derivs[0][1][0]
            elif jinc == 2:
                m[jthr][j + 1] += derivs[0][1][0]
                m[jthr][j + 0] += derivs[1][1][0]
            elif jinc == 4:
                m[jthr][j + 2] += derivs[0][1][0]
                m[jthr][j + 3] += derivs[1][1][0]
                m[jthr][j + 0] += derivs[2][1][0]
                m[jthr][j + 1] += derivs[3][1][0]
        if jk0r >= 0:
            v[jk0r] -= k0scale * seg.endr[1]
            if jinc == 1:
                m[jk0r][j] += derivs[0][1][1]
            elif jinc == 2:
                m[jk0r][j + 1] += derivs[0][1][1]
                m[jk0r][j + 0] += derivs[1][1][1]
            elif jinc == 4:
                m[jk0r][j + 2] += derivs[0][1][1]
                m[jk0r][j + 3] += derivs[1][1][1]
                m[jk0r][j + 0] += derivs[2][1][1]
                m[jk0r][j + 1] += derivs[3][1][1]
        if jk1r >= 0:
            v[jk1r] -= k1scale * seg.endr[2]
            m[jk1r][j + 2] += derivs[0][1][2]
            m[jk1r][j + 3] += derivs[1][1][2]
            m[jk1r][j + 0] += derivs[2][1][2]
            m[jk1r][j + 1] += derivs[3][1][2]
        if jk2r >= 0:
            v[jk2r] -= k2scale * seg.endr[3]
            m[jk2r][j + 2] += derivs[0][1][3]
            m[jk2r][j + 3] += derivs[1][1][3]
            m[jk2r][j + 0] += derivs[2][1][3]
            m[jk2r][j + 1] += derivs[3][1][3]

        j += jinc
        j0 = j1
    #print m
    dk = inversedot(m, v)
    dkmul = 1
    j = 0
    for i in range(len(segs)):
        jinc = jincs[i]
        if jinc == 1:
            segs[i].ks[0] += dkmul * dk[j]
        elif jinc == 2:
            segs[i].ks[0] += dkmul * dk[j + 1]
            segs[i].ks[1] += dkmul * dk[j + 0]
        elif jinc == 4:
            segs[i].ks[0] += dkmul * dk[j + 2]
            segs[i].ks[1] += dkmul * dk[j + 3]
            segs[i].ks[2] += dkmul * dk[j + 0]
            segs[i].ks[3] += dkmul * dk[j + 1]
        j += jinc

    norm = 0.
    for i in range(len(dk)):
        norm += dk[i] * dk[i]
    return sqrt(norm)


def plot_path(segs, nodes, tol = 1.0, show_cpts = False):
    if show_cpts:
        cpts = []
    j = 0
    cmd = 'moveto'
    for i in range(len(segs)):
        i1 = (i + 1) % len(nodes)
        n0 = nodes[i]
        n1 = nodes[i1]
        x0, y0, t0 = n0.x, n0.y, n0.ty
        x1, y1, t1 = n1.x, n1.y, n1.ty
        ks = segs[i].ks
        abs_ks = abs(ks[0]) + abs(ks[1] / 2) + abs(ks[2] / 8) + abs(ks[3] / 48)
        n_subdiv = int(ceil(.001 + tol * abs_ks))
        n_subhalf = (n_subdiv + 1) / 2
        if n_subdiv > 1:
            n_subdiv = n_subhalf * 2
        ksp = (ks[0] * .5, ks[1] * .25, ks[2] * .125, ks[3] * .0625)
        pside = poly3.int_3spiro_poly(ksp, n_subhalf)
        ksm = (ks[0] * -.5, ks[1] * .25, ks[2] * -.125, ks[3] * .0625)
        mside = poly3.int_3spiro_poly(ksm, n_subhalf)
        mside.reverse()
        for j in range(len(mside)):
            mside[j] = (-mside[j][0], -mside[j][1])
        if n_subdiv > 1:
            pts = mside + pside[1:]
        else:
            pts = mside[:1] + pside[1:]
        chord_th = atan2(y1 - y0, x1 - x0)
        chord_len = hypot(y1 - y0, x1 - x0)
        rot = chord_th - atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0])
        scale = chord_len / hypot(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0])
        u, v = scale * cos(rot), scale * sin(rot)
        xt = x0 - u * pts[0][0] + v * pts[0][1]
        yt = y0 - u * pts[0][1] - v * pts[0][0]
        s = -.5
        for x, y in pts:
            xp, yp = xt + u * x - v * y, yt + u * y + v * x
            thp = (((ks[3]/24 * s + ks[2]/6) * s + ks[1] / 2) * s + ks[0]) * s + rot
            up, vp = scale / (1.5 * n_subdiv) * cos(thp), scale / (1.5 * n_subdiv) * sin(thp)
            if s == -.5:
                if cmd == 'moveto':
                    print xp, yp, 'moveto'
                    cmd = 'curveto'
            else:
                if show_cpts:
                    cpts.append((xlast + ulast, ylast + vlast))
                    cpts.append((xp - up, yp - vp))
                print xlast + ulast, ylast + vlast, xp - up, yp - vp, xp, yp, 'curveto'
            xlast, ylast, ulast, vlast = xp, yp, up, vp
            s += 1. / n_subdiv
        if t1 == 'v':
            j += 2
        else:
            j += 1
    print 'stroke'
    if show_cpts:
        for x, y in cpts:
            print 'gsave 0 0 1 setrgbcolor', x, y, 'translate circle fill grestore'

def plot_ks(segs, nodes, xo, yo, xscale, yscale):
    j = 0
    cmd = 'moveto'
    x = xo
    for i in range(len(segs)):
        i1 = (i + 1) % len(nodes)
        n0 = nodes[i]
        n1 = nodes[i1]
        x0, y0, t0 = n0.x, n0.y, n0.ty
        x1, y1, t1 = n1.x, n1.y, n1.ty
        ks = segs[i].ks
        chord, ch_th = poly3.integ_chord(ks)
        l = chord/segs[i].chord
        k0 = l * poly3.eval_cubic(ks[0], ks[1], .5 * ks[2], 1./6 * ks[3], -.5)
        print x, yo + yscale * k0, cmd
        cmd = 'lineto'
        k3 = l * poly3.eval_cubic(ks[0], ks[1], .5 * ks[2], 1./6 * ks[3], .5)
        k1 = k0 + l/3 * (ks[1] - 0.5 * ks[2] + .125 * ks[3])
        k2 = k3 - l/3 * (ks[1] + 0.5 * ks[2] + .125 * ks[3])
        print x + xscale / l / 3., yo + yscale * k1
        print x + 2 * xscale / l / 3., yo + yscale * k2
        print x + xscale / l, yo + yscale * k3, 'curveto'
        x += xscale / l
        if t1 == 'v':
            j += 2
        else:
            j += 1
    print 'stroke'
    print xo, yo, 'moveto', x, yo, 'lineto stroke'

def plot_nodes(nodes, segs):
    for i in range(len(nodes)):
        n = nodes[i]
        print 'gsave', n.x, n.y, 'translate'
        if n.ty in ('c', '[', ']'):
            th = segs[i].th - segs[i].endl[0]
            if n.ty == ']': th += pi
            print 180 * th / pi, 'rotate'
        if n.ty == 'o':
            print 'circle fill'
        elif n.ty == 'c':
            print '3 4 poly fill'
        elif n.ty in ('v', '{', '}'):
            print '45 rotate 3 4 poly fill'
        elif n.ty in ('[', ']'):
            print '0 -3 moveto 0 0 3 90 270 arc fill'
        else:
            print '5 3 poly fill'
        print 'grestore'

def prologue():
    print '/ss 2 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    print '/poly {'
    print '    dup false exch {'
    print '        0 3 index 2 index { lineto } { moveto } ifelse pop true'
    print '        360.0 2 index div rotate'
    print '    } repeat pop pop pop'
    print '} bind def'

def run_path(path, show_iter = False, n = 10, xo = 36, yo = 550, xscale = .25, yscale = 2000, pl_nodes = True):
    segs, nodes = setup_path(path)
    print '.5 setlinewidth'
    for i in range(n):
        if i == n - 1:
            print '0 0 0 setrgbcolor 1 setlinewidth'
        elif i == 0:
            print '1 0 0 setrgbcolor'
        elif i == 1:
            print '0 0.5 0 setrgbcolor'
        elif i == 2:
            print '0.3 0.3 0.3 setrgbcolor'
        norm = iter(segs, nodes)
        print '% norm =', norm
        if show_iter or i == n - 1:
            #print '1 0 0 setrgbcolor'
            #plot_path(segs, nodes, tol = 5)
            #print '0 0 0 setrgbcolor'
            plot_path(segs, nodes, tol = 1.0)
            plot_ks(segs, nodes, xo, yo, xscale, yscale)
    if pl_nodes:
        plot_nodes(nodes, segs)

if __name__ == '__main__':
    if 1:
        path = [(100, 350, 'o'), (225, 350, 'o'), (350, 450, 'o'),
                (450, 400, 'o'), (315, 205, 'o'), (300, 200, 'o'),
                (285, 205, 'o')]

    if 1:
        path = [(100, 350, 'o'), (175, 375, '['), (250, 375, ']'), (325, 425, '['),
                (325, 450, ']'),
                (400, 475, 'o'), (350, 200, 'c')]

    if 0:
        ecc, ty, ty1 = 0.56199, 'c', 'c'
        ecc, ty, ty1 = 0.49076, 'o', 'o',
        ecc, ty, ty1 = 0.42637, 'o', 'c'
        path = [(300 - 200 * ecc, 300, ty), (300, 100, ty1),
                (300 + 200 * ecc, 300, ty), (300, 500, ty1)]

    # difficult path #3
    if 0:
        path = [(100, 300, '{'), (225, 350, 'o'), (350, 500, 'o'),
                (450, 500, 'o'), (450, 450, 'o'), (300, 200, '}')]

    if 0:
        path = [(100, 100, '{'), (200, 180, 'v'), (250, 215, 'o'),
                (300, 200, 'o'), (400, 100, '}')]

    if 0:
        praw = [
        (134, 90, 'o'),
        (192, 68, 'o'),
        (246, 66, 'o'),
        (307, 107, 'o'),
        (314, 154, '['),
        (317, 323, ']'),
        (347, 389, 'o'),
        (373, 379, 'v'),
        (386, 391, 'v'),
        (365, 409, 'o'),
        (335, 419, 'o'),
        (273, 390, 'v'),
        (251, 405, 'o'),
        (203, 423, 'o'),
        (102, 387, 'o'),
        (94, 321, 'o'),
        (143, 276, 'o'),
        (230, 251, 'o'),
        (260, 250, 'v'),
        (260, 220, '['),
        (258, 157, ']'),
        (243, 110, 'o'),
        (159, 99, 'o'),
        (141, 121, 'o'),
        (156, 158, 'o'),
        (121, 184, 'o'),
        (106, 117, 'o')]
        if 0:
            praw = [
            (275, 56, 'o'),
            (291, 75, 'v'),
            (312, 61, 'o'),
            (344, 50, 'o'),
            (373, 72, 'o'),
            (356, 91, 'o'),
            (334, 81, 'o'),
            (297, 85, 'v'),
            (306, 116, 'o'),
            (287, 180, 'o'),
            (236, 213, 'o'),
            (182, 212, 'o'),
            (157, 201, 'v'),
            (149, 209, 'o'),
            (143, 230, 'o'),
            (162, 246, 'c'),
            (202, 252, 'o'),
            (299, 260, 'o'),
            (331, 282, 'o'),
            (341, 341, 'o'),
            (308, 390, 'o'),
            (258, 417, 'o'),
            (185, 422, 'o'),
            (106, 377, 'o'),
            (110, 325, 'o'),
            (133, 296, 'o'),
            (147, 283, 'v'),
            (117, 238, 'o'),
            (133, 205, 'o'),
            (147, 191, 'v'),
            (126, 159, 'o'),
            (128, 94, 'o'),
            (167, 50, 'o'),
            (237, 39, 'o')]
            
        path = []
        for x, y, ty in praw:
            #if ty == 'o': ty = 'c'
            path.append((x, 550 - y, ty))

    if 0:
        path = [(100, 300, 'o'), (300, 100, 'o'), (300, 500, 'o')]

    if 0:
        # Woodford data set
        ty = 'o'
        praw = [(0, 0, '{'), (1, 1.9, ty), (2, 2.7, ty), (3, 2.6, ty),
                (4, 1.6, ty), (5, .89, ty), (6, 1.2, '}')]
        path = []
        for x, y, t in praw:
            path.append((100 + 80 * x, 100 + 80 * y, t))

    if 0:
        ycen = 32
        yrise = 0
        path = []
        ty = '{'
        for i in range(10):
            path.append((50 + i * 30, 250 + (10 - i) * yrise, ty))
            ty = 'o'
        path.append((350, 250 + ycen, ty))
        for i in range(1, 10):
            path.append((350 + i * 30, 250 + i * yrise, ty))
        path.append((650, 250 + 10 * yrise, '}'))

    prologue()

    run_path(path, show_iter = True, n=5)
