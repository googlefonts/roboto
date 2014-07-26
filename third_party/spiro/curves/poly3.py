# Numerical techniques for solving 3rd order polynomial spline systems

# The standard representation is the vector of derivatives at s=0,
# with -.5 <= s <= 5.
#
# Thus, \kappa(s) = k0 + k1 s + 1/2 k2 s^2 + 1/6 k3 s^3

from math import *

def eval_cubic(a, b, c, d, x):
    return ((d * x + c) * x + b) * x + a

# integrate over s = [0, 1]
def int_3spiro_poly(ks, n):
    x, y = 0, 0
    th = 0
    ds = 1.0 / n
    th1, th2, th3, th4 = ks[0], .5 * ks[1], (1./6) * ks[2], (1./24) * ks[3]
    k0, k1, k2, k3 = ks[0] * ds, ks[1] * ds, ks[2] * ds, ks[3] * ds
    s = 0
    result = [(x, y)]
    for i in range(n):
        sm = s + 0.5 * ds
        th = sm * eval_cubic(th1, th2, th3, th4, sm)
        cth = cos(th)
        sth = sin(th)

        km0 = ((1./6 * k3 * sm + .5 * k2) * sm + k1) * sm + k0
        km1 = ((.5 * k3 * sm + k2) * sm + k1) * ds
        km2 = (k3 * sm + k2) * ds * ds
        km3 = k3 * ds * ds * ds
        #print km0, km1, km2, km3
        u = 1 - km0 * km0 / 24
        v = km1 / 24

        u = 1 - km0 * km0 / 24 + (km0 ** 4 - 4 * km0 * km2 - 3 * km1 * km1) / 1920
        v = km1 / 24 + (km3 - 6 * km0 * km0 * km1) / 1920

        x += cth * u - sth * v
        y += cth * v + sth * u
        result.append((ds * x, ds * y))

        s += ds

    return result

def integ_chord(k, n = 64):
    ks = (k[0] * .5, k[1] * .25, k[2] * .125, k[3] * .0625)
    xp, yp = int_3spiro_poly(ks, n)[-1]
    ks = (k[0] * -.5, k[1] * .25, k[2] * -.125, k[3] * .0625)
    xm, ym = int_3spiro_poly(ks, n)[-1]
    dx, dy = .5 * (xp + xm), .5 * (yp + ym)
    return hypot(dx, dy), atan2(dy, dx)

# Return th0, th1, k0, k1 for given params
def calc_thk(ks):
    chord, ch_th = integ_chord(ks)
    th0 = ch_th - (-.5 * ks[0] + .125 * ks[1] - 1./48 * ks[2] + 1./384 * ks[3])
    th1 = (.5 * ks[0] + .125 * ks[1] + 1./48 * ks[2] + 1./384 * ks[3]) - ch_th
    k0 = chord * (ks[0] - .5 * ks[1] + .125 * ks[2] - 1./48 * ks[3])
    k1 = chord * (ks[0] + .5 * ks[1] + .125 * ks[2] + 1./48 * ks[3])
    #print '%', (-.5 * ks[0] + .125 * ks[1] - 1./48 * ks[2] + 1./384 * ks[3]), (.5 * ks[0] + .125 * ks[1] + 1./48 * ks[2] + 1./384 * ks[3]), ch_th
    return th0, th1, k0, k1

def calc_k1k2(ks):
    chord, ch_th = integ_chord(ks)
    k1l = chord * chord * (ks[1] - .5 * ks[2] + .125 * ks[3])
    k1r = chord * chord * (ks[1] + .5 * ks[2] + .125 * ks[3])
    k2l = chord * chord * chord * (ks[2] - .5 * ks[3])
    k2r = chord * chord * chord * (ks[2] + .5 * ks[3])
    return k1l, k1r, k2l, k2r
    
def plot(ks):
    ksp = (ks[0] * .5, ks[1] * .25, ks[2] * .125, ks[3] * .0625)
    pside = int_3spiro_poly(ksp, 64)
    ksm = (ks[0] * -.5, ks[1] * .25, ks[2] * -.125, ks[3] * .0625)
    mside = int_3spiro_poly(ksm, 64)
    mside.reverse()
    for i in range(len(mside)):
        mside[i] = (-mside[i][0], -mside[i][1])
    pts = mside + pside[1:]
    cmd = "moveto"
    for j in range(len(pts)):
        x, y = pts[j]
        print 306 + 300 * x, 400 + 300 * y, cmd
        cmd = "lineto"
    print "stroke"
    x, y = pts[0]
    print 306 + 300 * x, 400 + 300 * y, "moveto"
    x, y = pts[-1]
    print 306 + 300 * x, 400 + 300 * y, "lineto .5 setlinewidth stroke"
    print "showpage"

def solve_3spiro(th0, th1, k0, k1):
    ks = [0, 0, 0, 0]
    for i in range(5):
        th0_a, th1_a, k0_a, k1_a = calc_thk(ks)
        dth0 = th0 - th0_a
        dth1 = th1 - th1_a
        dk0 = k0 - k0_a
        dk1 = k1 - k1_a
        ks[0] += (dth0 + dth1) * 1.5 + (dk0 + dk1) * -.25
        ks[1] += (dth1 - dth0) * 15 + (dk0 - dk1) * 1.5
        ks[2] += (dth0 + dth1) * -12 + (dk0 + dk1) * 6
        ks[3] += (dth0 - dth1) * 360 + (dk1 - dk0) * 60
        #print '% ks =', ks
    return ks

def iter_spline(pts, ths, ks):
    pass

def solve_vee():
    kss = []
    for i in range(10):
        kss.append([0, 0, 0, 0])
    thl = [0] * len(kss)
    thr = [0] * len(kss)
    k0l = [0] * len(kss)
    k0r = [0] * len(kss)
    k1l = [0] * len(kss)
    k1r = [0] * len(kss)
    k2l = [0] * len(kss)
    k2r = [0] * len(kss)
    for i in range(10):
        for j in range(len(kss)):
            thl[j], thr[j], k0l[j], k0r[j] = calc_thk(kss[j])
            k0l[j], k1r[j], k2l[j], k2r[j] = calc_k1k2(kss[j])
        for j in range(len(kss) - 1):
            dth = thl[j + 1] + thr[j]
            if j == 5: dth += .1
            dk0 = k0l[j + 1] - k0r[j]
            dk1 = k1l[j + 1] - k1r[j]
            dk2 = k2l[j + 1] - k2r[j]


if __name__ == '__main__':
    k0 = pi * 3
    ks = [0, k0, -2 * k0, 0]
    ks = [0, 0, 0, 0.01]
    #plot(ks)
    thk = calc_thk(ks)
    print '%', thk
    
    ks = solve_3spiro(0, 0, 0, 0.001)
    print '% thk =', calc_thk(ks)
    #plot(ks)
    print '%', ks
    print calc_k1k2(ks)
