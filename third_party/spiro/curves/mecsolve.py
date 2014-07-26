from math import *
import array
import sys
import random

import numarray as N
import numarray.linear_algebra as la

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

# One step of 4th-order Runge-Kutta numerical integration - update y in place
def rk4(y, dydx, x, h, derivs):
    hh = h * .5
    h6 = h * (1./6)
    xh = x + hh
    yt = []
    for i in range(len(y)):
	yt.append(y[i] + hh * dydx[i])
    dyt = derivs(xh, yt)
    for i in range(len(y)):
	yt[i] = y[i] + hh * dyt[i]
    dym = derivs(xh, yt)
    for i in range(len(y)):
	yt[i] = y[i] + h * dym[i]
	dym[i] += dyt[i]
    dyt = derivs(x + h, yt)
    for i in range(len(y)):
	y[i] += h6 * (dydx[i] + dyt[i] + 2 * dym[i])

def run_elastica_half(sp, k0, lam1, lam2, n):
    def mec_derivs(x, ys):
	th, k = ys[2], ys[3]
	dx, dy = cos(th), sin(th)
	return [dx, dy, k, lam1 * dx + lam2 * dy, k * k]
    ys = [0, 0, 0, k0, 0]
    xyk = [(ys[0], ys[1], ys[3])]
    n = max(1, int(sp * n))
    h = float(sp) / n
    s = 0
    for i in range(n):
	dydx = mec_derivs(s, ys)
	rk4(ys, dydx, s, h, mec_derivs)
	xyk.append((ys[0], ys[1], ys[3]))
    return xyk, ys[2], ys[4]

def run_elastica(sm, sp, k0, lam1, lam2, n = 100):
    xykm, thm, costm = run_elastica_half(-sm, k0, -lam1, lam2, n)
    xykp, thp, costp = run_elastica_half(sp, k0, lam1, lam2, n)
    xyk = []
    for i in range(1, len(xykm)):
	x, y, k = xykm[i]
	xyk.append((-x, y, k))
    xyk.reverse()
    xyk.extend(xykp)
    x = xyk[-1][0] - xyk[0][0]
    y = xyk[-1][1] - xyk[0][1]
    th = thm + thp
    sth, cth = sin(thm), cos(thm)
    x, y = x * cth - y * sth, x * sth + y * cth
    result = []
    maxk = 0
    for xt, yt, kt in xyk:
        maxk = max(maxk, kt)
        result.append((xt, yt, kt))
    cost = costm + costp
    return result, cost, x, y, th

def run_mec_cos_pos(k, lam1, lam2, n = 1000):
    cost = 0
    th = 0
    x = 0
    y = 0
    dt = 1.0 / n
    result = [(0, 0)]
    for i in range(n):
        k1 = lam1 * cos(th) + lam2 * sin(th)

        cost += dt * k * k
        x += dt * cos(th)
        y += dt * sin(th)
        th += dt * k

        k += dt * k1
        result.append((x, y))
    return result, cost, x, y, th

def run_mec_cos(k, lam1, lam2, n = 1000):
    resp, costp, xp, yp, thp = run_mec_cos_pos(k*.5, lam1*.25, lam2*.25, n)
    resm, costm, xm, ym, thm = run_mec_cos_pos(k*.5, lam1*-.25, lam2*.25, n)
    cost = (costp + costm) * .5
    x, y = xp + xm, yp - ym
    th = thp + thm
    sth, cth = .5 * sin(thm), .5 * cos(thm)
    x, y = x * cth - y * sth, x * sth + y * cth
    result = []
    for i in range(1, n):
        xt, yt = resm[n - i - 1]
        result.append((-xt * cth - yt * sth, -xt * sth + yt * cth))
    for i in range(n):
        xt, yt = resp[i]
        result.append((xt * cth - yt * sth, xt * sth + yt * cth))
    return result, cost, x, y, th

def cross_prod(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]

def solve_mec(constraint_fnl):
    delta = 1e-3
    params = [pi, 0, 0]
    for i in range(20):
        k, lam1, lam2 = params
        xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
        #print i * .05, 'setgray'
        #plot(xys)
        c1c, c2c, costc = constraint_fnl(cost, x, y, th)
        print '% constraint_fnl =', c1c, c2c, 'cost =', costc

        dc1s = []
        dc2s = []
        for j in range(len(params)):
            params1 = N.array(params)
            params1[j] += delta
            k, lam1, lam2 = params1
            xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
            c1p, c2p, costp = constraint_fnl(cost, x, y, th)
            params1 = N.array(params)
            params1[j] -= delta
            k, lam1, lam2 = params1
            xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
            c1m, c2m, costm = constraint_fnl(cost, x, y, th)
            dc1s.append((c1p - c1m) / (2 * delta))
            dc2s.append((c2p - c2m) / (2 * delta))
        xp = cross_prod(dc1s, dc2s)
        xp = N.divide(xp, sqrt(N.dot(xp, xp))) # Normalize to unit length

        print '% dc1s =', dc1s
        print '% dc2s =', dc2s
        print '% xp =', xp
        
        # Compute second derivative wrt orthogonal vec
        params1 = N.array(params)
        for j in range(len(params)):
            params1[j] += delta * xp[j]
        k, lam1, lam2 = params1
        xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
        c1p, c2p, costp = constraint_fnl(cost, x, y, th)
        print '% constraint_fnl+ =', c1p, c2p, 'cost =', costp
        params1 = N.array(params)
        for j in range(len(params)):
            params1[j] -= delta * xp[j]
        k, lam1, lam2 = params1
        xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
        c1m, c2m, costm = constraint_fnl(cost, x, y, th)
        print '% constraint_fnl- =', c1m, c2m, 'cost =', costm
        d2cost = (costp + costm - 2 * costc) / (delta * delta)
        dcost = (costp - costm) / (2 * delta)

        print '% dcost =', dcost, 'd2cost =', d2cost
        if d2cost < 0: d2cost = .1
        # Make Jacobian matrix to invert
        jm = N.array([dc1s, dc2s, [x * d2cost for x in xp]])
        #print jm
        ji = la.inverse(jm)
        #print ji

        dp = N.dot(ji, [c1c, c2c, dcost])
        print '% dp =', dp
        print '% [right]=', [c1c, c2c, dcost]
        params -= dp * .1
        print '%', params
        sys.stdout.flush()
    return params

def solve_mec_3constr(constraint_fnl, n = 30, initparams = None):
    delta = 1e-3
    if initparams:
        params = N.array(initparams)
    else:
        params = [3.14, 0, 0]
    for i in range(n):
        k, lam1, lam2 = params
        xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
        c1c, c2c, c3c = constraint_fnl(cost, x, y, th)
        print '% constraint_fnl =', c1c, c2c, c3c

        dc1s = []
        dc2s = []
        dc3s = []
        for j in range(len(params)):
            params1 = N.array(params)
            params1[j] += delta
            k, lam1, lam2 = params1
            xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
            c1p, c2p, c3p = constraint_fnl(cost, x, y, th)
            params1 = N.array(params)
            params1[j] -= delta
            k, lam1, lam2 = params1
            xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
            c1m, c2m, c3m = constraint_fnl(cost, x, y, th)
            dc1s.append((c1p - c1m) / (2 * delta))
            dc2s.append((c2p - c2m) / (2 * delta))
            dc3s.append((c3p - c3m) / (2 * delta))

        # Make Jacobian matrix to invert
        jm = N.array([dc1s, dc2s, dc3s])
        #print jm
        ji = la.inverse(jm)

        dp = N.dot(ji, [c1c, c2c, c3c])
        if i < n/2: scale = .25
        else: scale = 1
        params -= scale * dp
        print '%', params
    return params

def mk_ths_fnl(th0, th1):
    def fnl(cost, x, y, th):
        actual_th0 = atan2(y, x)
        actual_th1 = th - actual_th0
        print '% x =', x, 'y =', y, 'hypot =', hypot(x, y)
        return th0 - actual_th0, th1 - actual_th1, cost
    return fnl

def mk_y_fnl(th0, th1, ytarg):
    def fnl(cost, x, y, th):
        actual_th0 = atan2(y, x)
        actual_th1 = th - actual_th0
        return th0 - actual_th0, th1 - actual_th1, ytarg - hypot(x, y)
    return fnl

def solve_mec_nested_inner(th0, th1, y, fnl):
    innerfnl = mk_y_fnl(th0, th1, y)
    params = [th0 + th1, 1e-6, 1e-6]
    params = solve_mec_3constr(innerfnl, 10, params)
    k, lam1, lam2 = params
    xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2, 100)
    c1, c2, c3 = fnl(cost, x, y, th)
    return c3, params

# Solve (th0, th1) mec to minimize fnl; use solve_mec_3constr as inner loop
# Use golden section search
def solve_mec_nested(th0, th1, fnl):
    R = .61803399
    C = 1 - R
    ax, cx = .6, .85
    bx = .5 * (ax + cx)

    x0, x3 = ax, cx
    if abs(cx - bx) > abs(bx - ax):
        x1, x2 = bx, bx + C * (cx - bx)
    else:
        x1, x2 = bx - C * (bx - ax), bx
    f1, p = solve_mec_nested_inner(th0, th1, x1, fnl)
    f2, p = solve_mec_nested_inner(th0, th1, x2, fnl)
    for i in range(10):
        print '%', x0, x1, x2, x3, ':', f1, f2
        if f2 < f1:
            x0, x1, x2 = x1, x2, R * x2 + C * x3
            f1 = f2
            f2, p = solve_mec_nested_inner(th0, th1, x2, fnl)
        else:
            x1, x2, x3 = R * x1 + C * x0, x1, x2
            f2 = f1
            f1, p = solve_mec_nested_inner(th0, th1, x1, fnl)
    if f1 < f2:
        x = x1
    else:
        x = x2
    cc, p = solve_mec_nested_inner(th0, th1, x, fnl)
    return p

def plot(xys):
    cmd = 'moveto'
    for xy in xys:
        print 306 + 200 * xy[0], 396 - 200 * xy[1], cmd
        cmd = 'lineto'
    print 'stroke'

def mec_test():
    th0, th1 = 0, pi / 4
    fnl = mk_ths_fnl(th0, th1)
    params = solve_mec_nested(th0, th1, fnl)
    k, lam1, lam2 = params
    xys, cost, x, y, th = run_mec_cos(k, lam1, lam2, 1000)
    plot(xys)
    print '% run_mec_cos:', cost, x, y, th
    print '1 0 0 setrgbcolor'
    xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2)
    print '%', xys
    plot(xys)
    print '% run_elastica:', cost, x, y, th
    print 'showpage'
    print '%', params

def lenfig():
    print '306 720 translate'
    th0, th1 = pi / 2, pi / 2
    for i in range(1, 10):
	y = .1 * i + .003
	fnl = mk_y_fnl(th0, th1, y)
	params = solve_mec_3constr(fnl)
	k, lam1, lam2 = params
	print 'gsave 0.5 dup scale -306 -396 translate'
	xys, cost, x, y, th = run_elastica(-2, 2, k, lam1, lam2, 100)
        print 'gsave [2] 0 setdash'
	plot(xys)
        print 'grestore'
	xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2, 100)
	plot(xys)
	print 'grestore'
        print '% y =', y, 'params =', params
        if lam2 < 0:
            mymaxk = k
        else:
            mymaxk = sqrt(k * k + 4 * lam2)
        lam = abs(lam2) / (mymaxk * mymaxk)
        print '-200 0 moveto /Symbol 12 selectfont (l) show'
        print '/Times-Roman 12 selectfont ( = %.4g) show' % lam
	print '0 -70 translate'
    print 'showpage'

def lenplot(figno, th0, th1):
    result = []
    if figno in (1, 2):
	imax = 181
    elif figno == 3:
	imax = 191
    for i in range(1, imax):
        yy = .005 * i
        if figno in (1, 2) and i == 127:
            yy = 2 / pi
	if figno == 3 and i == 165:
	    yy = .8270
	fnl = mk_y_fnl(th0, th1, yy)
	params = solve_mec_3constr(fnl)
	k, lam1, lam2 = params
        xys, cost, x0, y0, th = run_elastica(-.5, .5, k, lam1, lam2, 100)
        if lam2 < 0:
            mymaxk = k
        else:
            mymaxk = sqrt(k * k + 4 * lam2)
        lam = abs(lam2) / (mymaxk * mymaxk)
        result.append((yy, lam, cost))
    return result

def lengraph(figno):
    if figno in (1, 2):
        eps_prologue(15, 47, 585, 543)
	th0, th1 = pi / 2, pi / 2
	yscale = 900
	ytic = .05
	ymax = 10
    elif figno == 3:
        eps_prologue(15, 47, 585, 592)
	th0, th1 = pi / 3, pi / 3
	yscale = 500
	ytic = .1
	ymax = 10
    x0 = 42
    xscale = 7.5 * 72
    y0 = 72
    print '/Times-Roman 12 selectfont'
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    print '.5 setlinewidth'
    print x0, y0, 'moveto', xscale, '0 rlineto 0', yscale * ytic * ymax, 'rlineto', -xscale, '0 rlineto closepath stroke'
    for i in range(0, 11):
        print x0 + .1 * i * xscale, y0, 'moveto 0 6 rlineto stroke'
        print x0 + .1 * i * xscale, y0 + ytic * ymax * yscale, 'moveto 0 -6 rlineto stroke'
        print x0 + .1 * i * xscale, y0 - 12, 'moveto'
        print '(%.1g) dup stringwidth exch -.5 mul exch rmoveto show' % (.1 * i)
    for i in range(0, 11):
        print x0, y0 + ytic * i * yscale, 'moveto 6 0 rlineto stroke'
        print x0 + xscale, y0 + ytic * i * yscale, 'moveto -6 0 rlineto stroke'
        print x0 - 3, y0 + ytic * i * yscale - 3.5, 'moveto'
        print '(%.2g) dup stringwidth exch neg exch rmoveto show' % (ytic * i)
    print x0 + .25 * xscale, y0 - 24, 'moveto (chordlen / arclen) show'
    print x0 - 14, y0 + ytic * ymax * yscale + 10, 'moveto /Symbol 12 selectfont (l) show'
    if figno in (1, 2):
	print x0 + 2 / pi * xscale, y0 - 18, 'moveto'
	print '(2/p) dup stringwidth exch -.5 mul exch rmoveto show'
    print 'gsave [3] 0 setdash'
    print x0, y0 + .25 * yscale, 'moveto', xscale, '0 rlineto stroke'
    if figno == 3:
	print x0, y0 + .5 * yscale, 'moveto', xscale, '0 rlineto stroke'
	xinterest = .81153
	print x0 + xinterest * xscale, y0, 'moveto 0', yscale * .5, 'rlineto stroke'
    print 'grestore'
    print '.75 setlinewidth'
    if 1:
	if figno in (1, 2):
	    costscale = .01 * yscale
	elif figno == 3:
	    costscale = .0187 * yscale
        lenresult = lenplot(figno, th0, th1)
        cmd = 'moveto'
        for x, y, cost in lenresult:
            print x0 + xscale * x, y0 + yscale * y, cmd
            cmd = 'lineto'
        print 'stroke'
	if figno in (2, 3):
            cmd = 'moveto'
            for x, y, cost in lenresult:
                print x0 + xscale * x, y0 + costscale * cost, cmd
                cmd = 'lineto'
            print 'stroke'
            cmd = 'moveto'
            for x, y, cost in lenresult:
                print x0 + xscale * x, y0 + costscale * x * cost, cmd
                cmd = 'lineto'
            print 'stroke'
            print '/Times-Roman 12 selectfont'
	    if figno == 2:
		xlm, ylm = .75, 7
		xls, yls = .42, 15
	    elif figno == 3:
		xlm, ylm = .6, 3
		xls, yls = .37, 15
            print x0 + xscale * xlm, y0 + costscale * ylm, 'moveto'
            print '(MEC cost) show'
            print x0 + xscale * xls, y0 + costscale * yls, 'moveto'
            print '(SIMEC cost) show'
    if figno == 1:
        minis = [(.05, 5, -5),
             (.26, -40, 10),
             (.4569466, -5, -10),
             (.55, 35, 12),
             
             (.6026, -60, 45),
             (.6046, -60, 15),
             (.6066, -60, -15),
             
             (.6213, -22, 10),
             (.6366198, 15, 22),
             (.66, 20, 10),
             (.9, 0, -10)]
    elif figno == 2:
        minis = [(.4569466, -5, -10),
             (.6366198, 15, 22)]
    elif figno == 3:
	minis = [(.741, 55, -10),
		 (.81153, -30, 20),
		 (.8270, 20, 30)]

    for yy, xo, yo in minis:
	fnl = mk_y_fnl(th0, th1, yy)
	params = solve_mec_3constr(fnl)
	k, lam1, lam2 = params
        if lam2 < 0:
            mymaxk = k
        else:
            mymaxk = sqrt(k * k + 4 * lam2)
        lam = abs(lam2) / (mymaxk * mymaxk)
        x = x0 + xscale * yy
        y = y0 + yscale * lam
	print 'gsave %g %g translate circle fill' % (x, y)
        print '%g %g translate 0.15 dup scale' % (xo, yo)
        print '-306 -396 translate'
        print '2 setlinewidth'
        if yy < .6 or yy > .61:
            s = 2
        elif yy == .6046:
            s = 2.8
        else:
            s = 5
	xys, cost, x, y, th = run_elastica(-s, s, k, lam1, lam2, 100)
        print 'gsave [10] 0 setdash'
	plot(xys)
        print 'grestore 6 setlinewidth'
	xys, cost, x, y, th = run_elastica(-.5, .5, k, lam1, lam2, 100)
	plot(xys)
	print 'grestore'
        
    print 'showpage'
    eps_trailer()

def draw_axes(x0, y0, xscale, yscale, xmax, ymax, nx, ny):
    print '.5 setlinewidth'
    print '/Times-Roman 12 selectfont'
    print x0, y0, 'moveto', xscale * xmax, '0 rlineto 0', yscale * ymax, 'rlineto', -xscale * xmax, '0 rlineto closepath stroke'
    xinc = (xmax * xscale * 1.) / nx
    yinc = (ymax * yscale * 1.) / ny
    for i in range(0, nx + 1):
        if i > 0 and i < nx + 1:
            print x0 + xinc * i, y0, 'moveto 0 6 rlineto stroke'
            print x0 + xinc * i, y0 + ymax * yscale, 'moveto 0 -6 rlineto stroke'
        print x0 + xinc * i, y0 - 12, 'moveto'
        print '(%.2g) dup stringwidth exch -.5 mul exch rmoveto show' % ((i * xmax * 1.) / nx)
    for i in range(0, ny + 1):
        if i > 0 and i < ny + 1:
            print x0, y0 + yinc * i, 'moveto 6 0 rlineto stroke'
            print x0 + xmax * xscale, y0 + yinc * i, 'moveto -6 0 rlineto stroke'
        print x0 - 3, y0 + yinc * i - 3.5, 'moveto'
        print '(%.2g) dup stringwidth exch neg exch rmoveto show' % ((i * ymax * 1.) / ny)
    

def mecchord():
    x0 = 72
    y0 = 72
    thscale = 150
    chscale = 400
    print '.5 setlinewidth'
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    draw_axes(x0, y0, thscale, chscale, 3.2, 1, 16, 10)
    print x0 + 1 * thscale, y0 - 28, 'moveto (angle) show'
    print 'gsave', x0 - 32, y0 + .25 * chscale, 'translate'
    print '90 rotate 0 0 moveto (chordlen / arclen) show'
    print 'grestore'

    cmd = 'moveto'
    for i in range(0, 67):
        s = i * .01
        xys, cost, x, y, th = run_elastica(-s, s, 4, 0, -8, 100)
        #plot(xys)
        if s > 0:
            ch = hypot(x, y) / (2 * s)
        else:
            ch = 1
        print '%', s, x, y, th, ch
        print x0 + thscale * th / 2, y0 + ch * chscale, cmd
        cmd = 'lineto'
    print 'stroke'

    print 'gsave %g %g translate circle fill' % (x0 + thscale * th / 2, y0 + ch * chscale)
    print '-30 15 translate 0.25 dup scale'
    print '-306 -396 translate'
    print '2 setlinewidth'
    plot(xys)
    print 'grestore'

    print 'gsave [2] 0 setdash'
    cmd = 'moveto'
    for i in range(0, 151):
        th = pi * i / 150.
        if th > 0:
            ch = sin(th) / th
        else:
            ch = 1
        print x0 + thscale * th, y0 + ch * chscale, cmd
        cmd = 'lineto'
    print 'stroke'
    print 'grestore'

    k0 = 4 * .4536 / (2 / pi)
    s = pi / (2 * k0)
    xys, cost, x, y, th = run_elastica(-s, s, k0, 0, 0, 100)
    th = pi
    ch = 2 / pi
    print 'gsave %g %g translate circle fill' % (x0 + thscale * th / 2, y0 + ch * chscale)
    print '30 15 translate 0.25 dup scale'
    print '-306 -396 translate'
    print '2 setlinewidth'
    plot(xys)
    print 'grestore'

    print x0 + 1.25 * thscale, y0 + .55 * chscale, 'moveto (MEC) show'
    print x0 + 2.3 * thscale, y0 + .35 * chscale, 'moveto (SIMEC) show'

    print 'showpage'

def trymec(sm, sp):
    xys, thm, cost = run_elastica_half(abs(sm), 0, 1, 0, 10)
    xm, ym, km = xys[-1]
    if sm < 0:
        xm = -xm
        ym = -ym
        thm = -thm
    xys, thp, cost = run_elastica_half(abs(sp), 0, 1, 0, 10)
    xp, yp, kp = xys[-1]
    if sp < 0:
        xp = -xp
        yp = -yp
        thp = -thp
    chth = atan2(yp - ym, xp - xm)
    #print xm, ym, xp, yp, chth, thm, thp
    actual_th0 = chth - thm
    actual_th1 = thp - chth
    return actual_th0, actual_th1

def findmec_old(th0, th1):
    guess_ds = sqrt(6 * (th1 - th0))
    guess_savg = 2 * (th1 + th0) / guess_ds
    sm = .5 * (guess_savg - guess_ds)
    sp = .5 * (guess_savg + guess_ds)
    #sm, sp = th0, th1
    for i in range(1):
        actual_th0, actual_th1 = trymec(sm, sp)
        guess_dth = 1./6 * (sp - sm) ** 2
        guess_avth = .5 * (sp + sm) * (sp - sm)
        guess_th0 = .5 * (guess_avth - guess_dth)
        guess_th1 = .5 * (guess_avth + guess_dth)
        print sm, sp, actual_th0, actual_th1, guess_th0, guess_th1

def mecplots():
    print '2 dup scale'
    print '-153 -296 translate'
    scale = 45
    print '0.25 setlinewidth'
    print 306 - scale * pi/2, 396, 'moveto', 306 + scale * pi/2, 396, 'lineto stroke'
    print 306, 396 - scale * pi/2, 'moveto', 306, 396 + scale * pi/2, 'lineto stroke'
    print '/ss .5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'

    tic = .1
    maj = 5
    r0, r1 = 0, 81

    for i in range(r0, r1, maj):
        sm = i * tic
        cmd = 'moveto'
        for j in range(i, r1):
            sp = j * tic + 1e-3
            th0, th1 = trymec(sm, sp)
            print '%', sm, sp, th0, th1
            print 306 + scale * th0, 396 + scale * th1, cmd
            cmd = 'lineto'
        print 'stroke'
    for j in range(r0, r1, maj):
        sp = j * tic + 1e-3
        cmd = 'moveto'
        for i in range(0, j + 1):
            sm = i * tic
            th0, th1 = trymec(sm, sp)
            print '%', sm, sp, th0, th1
            print 306 + scale * th0, 396 + scale * th1, cmd
            cmd = 'lineto'
        print 'stroke'

    for i in range(r0, r1, maj):
        sm = i * tic
        for j in range(i, r1, maj):
            sp = j * tic + 1e-3
            th0, th1 = trymec(sm, sp)
            print 'gsave'
            print 306 + scale * th0, 596 + scale * th1, 'translate'
            print 'circle fill'
            uscale = 3
            xys, thm, cost = run_elastica_half(abs(sm), 0, 1, 0, 100)
            x0, y0 = xys[-1][0], xys[-1][1]
            if sm < 0:
                x0, y0 = -x0, -y0
            xys, thm, cost = run_elastica_half(abs(sp), 0, 1, 0, 100)
            x1, y1 = xys[-1][0], xys[-1][1]
            if sp < 0:
                x1, y1 = -x1, -y1
            cmd = 'moveto'
            for xy in xys:
                print xy[0] * uscale, xy[1] * uscale, cmd
                cmd = 'lineto'
            print 'stroke'
            print '1 0 0 setrgbcolor'
            print x0 * uscale, y0 * uscale, 'moveto'
            print x1 * uscale, y1 * uscale, 'lineto stroke'
            print 'grestore'

    print 'showpage'

def findmec(th0, th1):
    delta = 1e-3
    if th0 < 0 and th0 - th1 < .1:
        sm = 5.
        sp = 6.
    else:
        sm = 3.
        sp = 5.
    params = [sm, sp]
    lasterr = 1e6
    for i in range(25):
        sm, sp = params
        ath0, ath1 = trymec(sm, sp)
        c1c, c2c = th0 - ath0, th1 - ath1

        err = c1c * c1c + c2c * c2c
        if 0:
            print '%findmec', sm, sp, ath0, ath1, err
            sys.stdout.flush()

        if err < 1e-9:
            return params
        if err > lasterr:
            return None
        lasterr = err


        dc1s = []
        dc2s = []
        for j in range(len(params)):
            params1 = N.array(params)
            params1[j] += delta
            sm, sp = params1
            ath0, ath1 = trymec(sm, sp)
            c1p, c2p = th0 - ath0, th1 - ath1

            params1 = N.array(params)
            params1[j] -= delta
            sm, sp = params1
            ath0, ath1 = trymec(sm, sp)
            c1m, c2m = th0 - ath0, th1 - ath1

            dc1s.append((c1p - c1m) / (2 * delta))
            dc2s.append((c2p - c2m) / (2 * delta))

        jm = N.array([dc1s, dc2s])
        ji = la.inverse(jm)
        dp = N.dot(ji, [c1c, c2c])

        if i < 4:
            scale = .5
        else:
            scale = 1
        params -= scale * dp
        if params[0] < 0: params[0] = 0.
    return params

def mecrange(figtype):
    scale = 130
    eps_prologue(50, 110, 570, 630)
    print -50, 0, 'translate'
    print '0.5 setlinewidth'
    thlmin, thlmax = -pi/2, 2.4
    thrmin, thrmax = -2.2, pi / 2 + .2
    print 306 + scale * thlmin, 396, 'moveto', 306 + scale * thlmax, 396, 'lineto stroke'
    print 306, 396 + scale * thrmin, 'moveto', 306, 396 + scale * thrmax, 'lineto stroke'

    print 'gsave [2] 0 setdash'
    print 306, 396 + scale * pi / 2, 'moveto'
    print 306 + scale * thlmax, 396 + scale * pi / 2, 'lineto stroke'
    print 306 + scale * thlmin, 396 - scale * pi / 2, 'moveto'
    print 306 + scale * thlmax, 396 - scale * pi / 2, 'lineto stroke'
    print 306 + scale * pi / 2, 396 + scale * thrmin, 'moveto'
    print 306 + scale * pi / 2, 396 + scale * thrmax, 'lineto stroke'
    print 'grestore'

    print 306 + 3, 396 + scale * thrmax - 10, 'moveto'
    print '/Symbol 12 selectfont (q) show'
    print 0, -2, 'rmoveto'
    print '/Times-Italic 9 selectfont (right) show'

    print 306 - 18, 396 + scale * pi / 2 - 4, 'moveto'
    print '/Symbol 12 selectfont (p/2) show'
    print 306 + scale * 2.2, 396 - scale * pi / 2 + 2, 'moveto'
    print '/Symbol 12 selectfont (-p/2) show'

    print 306 + scale * pi/2 + 2, 396 + scale * thrmax - 10, 'moveto'
    print '/Symbol 12 selectfont (p/2) show'

    print 306 + scale * 2.2, 396 + 6, 'moveto'
    print '/Symbol 12 selectfont (q) show'
    print 0, -2, 'rmoveto'
    print '/Times-Italic 9 selectfont (left) show'

    print '/ss 0.8 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    cmd = 'moveto'
    for i in range(0, 201):
        th = (i * .005 - .75 )* pi
        rmin = 1.5
        rmax = 2.5
        for j in range(20):
            r = (rmin + rmax) * .5
            th0 = r * cos(th)
            th1 = r * sin(th)
            if findmec(th0, th1) == None:
                rmax = r
            else:
                rmin = r
        r = (rmin + rmax) * .5
        th0 = r * cos(th)
        th1 = r * sin(th)
        print '%', r, th, th0, th1
        print 306 + scale * th0, 396 + scale * th1, cmd
        cmd = 'lineto'
        sys.stdout.flush()
    print 'stroke'
    sys.stdout.flush()
        
    for i in range(-11, 12):
        for j in range(-11, i + 1):
            th0, th1 = i * .196, j * .196
            print '%', th0, th1
            params = findmec(th0, th1)
            if params != None:
                sm, sp = params
                print 'gsave'
                print 306 + scale * th0, 396 + scale * th1, 'translate'
                uscale = 22
                k0, lam1, lam2 = justify_mec(sm, sp)
                xys, cost, x, y, th = run_elastica(-.5, .5, k0, lam1, lam2)
                cmdm = 'moveto'
                dx = xys[-1][0] - xys[0][0]
                dy = xys[-1][1] - xys[0][1]
                ch = hypot(dx, dy)
                chth = atan2(dy, dx)
                if figtype == 'mecrange':
                    print 'circle fill'
                    s = uscale * sin(chth) / ch
                    c = uscale * cos(chth) / ch
                    h = -xys[0][0] * s + xys[0][1] * c
                    for xy in xys:
                        print xy[0] * c + xy[1] * s, h + xy[0] * s - xy[1] * c, cmdm
                        cmdm = 'lineto'
                elif figtype == 'mecrangek':
                    ds = 1. / (len(xys) - 1)
                    sscale = 13. / ch
                    kscale = 3 * ch
                    print 'gsave .25 setlinewidth'
                    print sscale * -.5, 0, 'moveto', sscale, 0, 'rlineto stroke'
                    print 'grestore'
                    for l in range(len(xys)):
                        print sscale * (ds * l - 0.5), kscale * xys[l][2], cmdm
                        cmdm = 'lineto'
                print 'stroke'
                print 'grestore'
            sys.stdout.flush()
    print 'showpage'
    eps_trailer()

# given sm, sp in [0, 1, 0] mec, return params for -0.5..0.5 segment
def justify_mec(sm, sp):
    sc = (sm + sp) * 0.5
    xys, thc, cost = run_elastica_half(sc, 0, 1, 0, 100)
    print '% sc =', sc, 'thc =', thc
    k0, lam1, lam2 = xys[-1][2], cos(thc), -sin(thc)
    ds = sp - sm
    k0 *= ds
    lam1 *= ds * ds
    lam2 *= ds * ds
    return [k0, lam1, lam2]

import sys
figname = sys.argv[1]
if len(figname) > 4 and figname[-4:] == '.pdf': figname = figname[:-4]
if figname in ('lengraph1', 'lengraph2', 'lengraph3'):
    lengraph(int(figname[-1]))
    #mec_test()
    #lenfig()
elif figname == 'mecchord':
    mecchord()
elif figname in ('mecrange', 'mecrangek'):
    mecrange(figname)
elif figname == 'mecplots':
    mecplots()
elif figname == 'findmec':
    findmec(-.1, -.1)
    findmec(-.2, -.2)

