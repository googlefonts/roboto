# Convert piecewise cubic into piecewise clothoid representation.

from math import *

import clothoid
import pcorn
import tocubic

import offset

def read_bz(f):
    result = []
    for l in f.xreadlines():
        s = l.split()
        if len(s) > 0:
            cmd = s[-1]
            #print s[:-1], cmd
            if cmd == 'm':
                sp = []
                result.append(sp)
                curpt = [float(x) for x in s[0:2]]
                startpt = curpt
            elif cmd == 'l':
                newpt = [float(x) for x in s[0:2]]
                sp.append((curpt, newpt))
                curpt = newpt
            elif cmd == 'c':
                c1 = [float(x) for x in s[0:2]]
                c2 = [float(x) for x in s[2:4]]
                newpt = [float(x) for x in s[4:6]]
                sp.append((curpt, c1, c2, newpt))
                curpt = newpt
    return result

def plot_bzs(bzs, z0, scale, fancy = False):
    for sp in bzs:
        for i in range(len(sp)):
            bz = sp[i]
            tocubic.plot_bz(bz, z0, scale, i == 0)
        print 'stroke'
        if fancy:
            for i in range(len(sp)):
                bz = sp[i]

                x0, y0 = z0[0] + scale * bz[0][0], z0[1] + scale * bz[0][1]
                print 'gsave', x0, y0, 'translate circle fill grestore'
                if len(bz) == 4:
                    x1, y1 = z0[0] + scale * bz[1][0], z0[1] + scale * bz[1][1]
                    x2, y2 = z0[0] + scale * bz[2][0], z0[1] + scale * bz[2][1]
                    x3, y3 = z0[0] + scale * bz[3][0], z0[1] + scale * bz[3][1]
                    print 'gsave 0.5 setlinewidth', x0, y0, 'moveto'
                    print x1, y1, 'lineto stroke'
                    print x2, y2, 'moveto'
                    print x3, y3, 'lineto stroke grestore'
                    print 'gsave', x1, y1, 'translate 0.75 dup scale circle fill grestore'
                    print 'gsave', x2, y2, 'translate 0.75 dup scale circle fill grestore'
                    print 'gsave', x3, y3, 'translate 0.75 dup scale circle fill grestore'
            
        

def measure_bz_cloth(seg, bz, n = 100):
    bz_arclen = tocubic.bz_arclength_rk4(bz)
    arclen_ratio = seg.arclen / bz_arclen
    dbz = tocubic.bz_deriv(bz)
    
    def measure_derivs(x, ys):
        dx, dy = tocubic.bz_eval(dbz, x)
        ds = hypot(dx, dy)
        s = ys[0] * arclen_ratio
        dscore = ds * (tocubic.mod_2pi(atan2(dy, dx) - seg.th(s)) ** 2)
        #print s, atan2(dy, dx),  seg.th(s)
        return [ds, dscore]
    dt = 1./n
    t = 0
    ys = [0, 0]
    for i in range(n):
        dydx = measure_derivs(t, ys)
        tocubic.rk4(ys, dydx, t, dt, measure_derivs)
        t += dt
    return ys[1]

def cubic_bz_to_pcorn(bz, thresh):
    dx = bz[3][0] - bz[0][0]
    dy = bz[3][1] - bz[0][1]
    dx1 = bz[1][0] - bz[0][0]
    dy1 = bz[1][1] - bz[0][1]
    dx2 = bz[3][0] - bz[2][0]
    dy2 = bz[3][1] - bz[2][1]
    chth = atan2(dy, dx)
    th0 = tocubic.mod_2pi(chth - atan2(dy1, dx1))
    th1 = tocubic.mod_2pi(atan2(dy2, dx2) - chth)
    seg = pcorn.Segment(bz[0], bz[3], th0, th1)
    err = measure_bz_cloth(seg, bz)
    if err < thresh:
        return [seg]
    else:
        # de Casteljau
        x01, y01 = 0.5 * (bz[0][0] + bz[1][0]), 0.5 * (bz[0][1] + bz[1][1])
        x12, y12 = 0.5 * (bz[1][0] + bz[2][0]), 0.5 * (bz[1][1] + bz[2][1])
        x23, y23 = 0.5 * (bz[2][0] + bz[3][0]), 0.5 * (bz[2][1] + bz[3][1])
        xl2, yl2 = 0.5 * (x01 + x12), 0.5 * (y01 + y12)
        xr1, yr1 = 0.5 * (x12 + x23), 0.5 * (y12 + y23)
        xm, ym = 0.5 * (xl2 + xr1), 0.5 * (yl2 + yr1)
        bzl = [bz[0], (x01, y01), (xl2, yl2), (xm, ym)]
        bzr = [(xm, ym), (xr1, yr1), (x23, y23), bz[3]]
        segs = cubic_bz_to_pcorn(bzl, 0.5 * thresh)
        segs.extend(cubic_bz_to_pcorn(bzr, 0.5 * thresh))
        return segs

def bzs_to_pcorn(bzs, thresh = 1e-9):
    result = []
    for sp in bzs:
        rsp = []
        for bz in sp:
            if len(bz) == 2:
                dx = bz[1][0] - bz[0][0]
                dy = bz[1][1] - bz[0][1]
                th = atan2(dy, dx)
                rsp.append(pcorn.Segment(bz[0], bz[1], 0, 0))
            else:
                rsp.extend(cubic_bz_to_pcorn(bz, thresh))
        result.append(rsp)
    return result

def plot_segs(segs):
    for i in range(len(segs)):
        seg = segs[i]
        if i == 0:
            print seg.z0[0], seg.z0[1], 'moveto'
        print seg.z1[0], seg.z1[1], 'lineto'
    print 'stroke'
    for i in range(len(segs)):
        seg = segs[i]
        if i == 0:
            print 'gsave', seg.z0[0], seg.z0[1], 'translate circle fill grestore'
        print 'gsave', seg.z1[0], seg.z1[1], 'translate circle fill grestore'

import sys

def test_to_pcorn():
    C1 = 0.55228
    bz = [(100, 100), (100 + 400 * C1, 100), (500, 500 - 400 * C1), (500, 500)]
    for i in range(0, 13):
        thresh = .1 ** i
        segs = cubic_bz_to_pcorn(bz, thresh)
        plot_segs(segs)
        print >> sys.stderr, thresh, len(segs)
        print '0 20 translate'

if __name__ == '__main__':
    f = file(sys.argv[1])
    bzs = read_bz(f)
    rsps = bzs_to_pcorn(bzs, 1)
    #print rsps
    tocubic.plot_prolog()
    print 'grestore'
    print '1 -1 scale 0 -720 translate'
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    tot = 0
    for segs in rsps:
        curve = pcorn.Curve(segs)
        #curve = offset.offset(curve, 10)
        print '%', curve.arclen
        print '%', curve.sstarts
        if 0:
            print 'gsave 1 0 0 setrgbcolor'
            cmd = 'moveto'
            for i in range(100):
                s = i * .01 * curve.arclen
                x, y = curve.xy(s)
                th = curve.th(s)
                sth = 5 * sin(th)
                cth = 5 * cos(th)
                print x, y, cmd
                cmd = 'lineto'
            print 'closepath stroke grestore'
        for i in range(100):
            s = i * .01 * curve.arclen
            x, y = curve.xy(s)
            th = curve.th(s)
            sth = 5 * sin(th)
            cth = 5 * cos(th)
            if 0:
                print x - cth, y - sth, 'moveto'
                print x + cth, y + sth, 'lineto stroke'
        if 1:
            for s in curve.find_breaks():
                print 'gsave 0 1 0 setrgbcolor'
                x, y = curve.xy(s)
                print x, y, 'translate 2 dup scale circle fill'
                print 'grestore'
        #plot_segs(segs)

        print 'gsave 0 0 0 setrgbcolor'
        optim = 3
        thresh = 1e-2
        new_bzs = tocubic.pcorn_curve_to_bzs(curve, optim, thresh)
        tot += len(new_bzs)
        plot_bzs([new_bzs], (0, 0), 1, True)
        print 'grestore'
    print 'grestore'
    print '/Helvetica 12 selectfont'
    print '36 720 moveto (thresh=%g optim=%d) show' % (thresh, optim)
    print '( tot segs=%d) show' % tot
    print 'showpage'

    #plot_bzs(bzs, (100, 100), 1)
