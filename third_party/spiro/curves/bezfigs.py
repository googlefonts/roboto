import sys
from math import *

import fromcubic
import tocubic

import cornu

def eps_prologue(x0, y0, x1, y1, draw_box = False):
    print '%!PS-Adobe-3.0 EPSF'
    print '%%BoundingBox:', x0, y0, x1, y1
    print '%%EndComments'
    print '%%EndProlog'
    print '%%Page: 1 1'
    if draw_box:
        print x0, y0, 'moveto', x0, y1, 'lineto', x1, y1, 'lineto', x1, y0, 'lineto closepath stroke'

def eps_trailer():
    print '%%EOF'

def fit_cubic_superfast(z0, z1, arclen, th0, th1, aab):
    chord = hypot(z1[0] - z0[0], z1[1] - z0[1])
    cth0, sth0 = cos(th0), sin(th0)
    cth1, sth1 = -cos(th1), -sin(th1)
    armlen = .66667 * arclen
    a = armlen * aab
    b = armlen - a
    bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
          (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
    return bz

def fit_cubic(z0, z1, arclen, th_fn, fast, aabmin = 0, aabmax = 1.):
    chord = hypot(z1[0] - z0[0], z1[1] - z0[1])
    if (arclen < 1.000001 * chord):
        return [z0, z1], 0
    th0 = th_fn(0)
    th1 = th_fn(arclen)
    imax = 4
    jmax = 10
    if fast:
        imax = 1
        jmax = 0
    for i in range(imax):
        for j in range(jmax + 1):
            if jmax == 0:
                aab = 0.5 * (aabmin + aabmax)
            else:
                aab = aabmin + (aabmax - aabmin) * j / jmax
            if fast == 2:
                bz = fit_cubic_superfast(z0, z1, arclen, th0, th1, aab)
            else:
                bz = tocubic.fit_cubic_arclen(z0, z1, arclen, th0, th1, aab)
            score = tocubic.measure_bz_rk4(bz, arclen, th_fn)
            print '% aab =', aab, 'score =', score
            sys.stdout.flush()
            if j == 0 or score < best_score:
                best_score = score
                best_aab = aab
                best_bz = bz
        daab = .06 * (aabmax - aabmin)
        aabmin = max(0, best_aab - daab)
        aabmax = min(1, best_aab + daab)
        print '%--- best_aab =', best_aab
    return best_bz, best_score

def cornu_to_cubic(t0, t1, figno):
    if figno == 1:
        aabmin = 0
        aabmax = 0.4
    elif figno == 2:
        aabmin = 0.5
        aabmax = 1.
    else:
        aabmin = 0
        aabmax = 1.
    fast = 0
    if figno == 3:
        fast = 1
    elif figno == 4:
        fast = 2
    def th_fn(s):
        return (s + t0) ** 2
    y0, x0 = cornu.eval_cornu(t0)
    y1, x1 = cornu.eval_cornu(t1)
    bz, score = fit_cubic((x0, y0), (x1, y1), t1 - t0, th_fn, fast, aabmin, aabmax)
    return bz, score

def plot_k_of_bz(bz):
    dbz = tocubic.bz_deriv(bz)
    ddbz = tocubic.bz_deriv(dbz)
    cmd = 'moveto'
    ss = [0]
    def arclength_deriv(x, ss):
        dx, dy = tocubic.bz_eval(dbz, x)
        return [hypot(dx, dy)]
    dt = 0.01
    t = 0
    for i in range(101):
        dx, dy = tocubic.bz_eval(dbz, t)
        ddx, ddy = tocubic.bz_eval(ddbz, t)
        k = (ddy * dx - dy * ddx) / (dx * dx + dy * dy) ** 1.5
        print 100 + 500 * ss[0], 100 + 200 * k, cmd
        cmd = 'lineto'

        dsdx = arclength_deriv(t, ss)
        tocubic.rk4(ss, dsdx, t, .01, arclength_deriv)
        t += dt
    print 'stroke'

def plot_k_nominal(s0, s1):
    k0 = 2 * s0
    k1 = 2 * s1
    print 'gsave 0.5 setlinewidth'
    print 100, 100 + 200 * k0, 'moveto'
    print 100 + 500 * (s1 - s0), 100 + 200 * k1, 'lineto'
    print 'stroke grestore'

def simple_bez():
    eps_prologue(95, 126, 552, 508, 0)
    tocubic.plot_prolog()
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    bz, score = cornu_to_cubic(.5, 1.1, 2)
    fromcubic.plot_bzs([[bz]], (-400, 100), 1000, True)
    print 'stroke'
    print '/Times-Roman 12 selectfont'
    print '95 130 moveto ((x0, y0)) show'
    print '360 200 moveto ((x1, y1)) show'
    print '480 340 moveto ((x2, y2)) show'
    print '505 495 moveto ((x3, y3)) show'
    print 'showpage'
    eps_trailer()

def fast_bez(figno):
    if figno == 3:
        y1 = 520
    else:
        y1 = 550
    eps_prologue(95, 140, 552, y1, 0)
    tocubic.plot_prolog()
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    bz, score = cornu_to_cubic(.5, 1.1, figno)
    fromcubic.plot_bzs([[bz]], (-400, 100), 1000, True)
    print 'stroke'
    plot_k_nominal(.5, 1.1)
    plot_k_of_bz(bz)
    print 'showpage'
    eps_trailer()

def bezfig(s1):
    eps_prologue(95, 38, 510, 550, 0)
    #print '0.5 0.5 scale 500 100 translate'
    tocubic.plot_prolog()
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    bz, score = cornu_to_cubic(.5, 0.85, 1)
    fromcubic.plot_bzs([[bz]], (-400, 0), 1000, True)
    print 'stroke'
    plot_k_nominal(.5, 0.85)
    plot_k_of_bz(bz)
    bz, score = cornu_to_cubic(.5, 0.85, 2)
    fromcubic.plot_bzs([[bz]], (-400, 100), 1000, True)
    print 'stroke'
    print 'gsave 0 50 translate'
    plot_k_nominal(.5, .85)
    plot_k_of_bz(bz)
    print 'grestore'
    print 'showpage'

import sys

if __name__ == '__main__':
    figno = int(sys.argv[1])
    if figno == 0:
        simple_bez()
    elif figno == 1:
        bezfig(1.0)
    elif figno == 2:
        bezfig(0.85)
    else:
        fast_bez(figno)
    #fast_bez(4)
