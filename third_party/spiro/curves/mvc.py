from math import *
import array
import sys
import random

def run_mvc(k, k1, k2, k3, C, n = 100, do_print = False):
    cmd = 'moveto'
    result = array.array('d')
    cost = 0
    th = 0
    x = 0
    y = 0
    dt = 1.0 / n
    for i in range(n):
        k4 = -k * (k * k2 - .5 *  k1 * k1 + C)

        cost += dt * k1 * k1
        x += dt * cos(th)
        y += dt * sin(th)
        th += dt * k

        k += dt * k1
        k1 += dt * k2
        k2 += dt * k3
        k3 += dt * k4
        result.append(k)
        if do_print: print 400 + 400 * x, 500 + 400 * y, cmd
        cmd = 'lineto'
    return result, cost, x, y, th

def run_mec_cos(k, lam1, lam2, n = 100, do_print = False):
    cmd = 'moveto'
    result = array.array('d')
    cost = 0
    th = 0
    x = 0
    y = 0
    dt = 1.0 / n
    for i in range(n):
        k1 = lam1 * cos(th) + lam2 * sin(th)

        cost += dt * k * k
        x += dt * cos(th)
        y += dt * sin(th)
        th += dt * k

        k += dt * k1
        result.append(k)
        if do_print: print 400 + 400 * x, 500 + 400 * y, cmd
        cmd = 'lineto'
    return result, cost, x, y, th

def descend(params, fnl):
    delta = 1
    for i in range(100):
        best = fnl(params, i, True)
        bestparams = params
        for j in range(2 * len(params)):
            ix = j / 2
            sign = 1 - 2 * (ix & 1)
            newparams = params[:]
            newparams[ix] += delta * sign
            new = fnl(newparams, i)
            if (new < best):
                bestparams = newparams
                best = new
        if (bestparams == params):
            delta *= .5
        print '%', params, delta
        sys.stdout.flush()
        params = bestparams
    return bestparams

def descend2(params, fnl):
    delta = 20
    for i in range(5):
        best = fnl(params, i, True)
        bestparams = params
        for j in range(100000):
            newparams = params[:]
            for ix in range(len(params)):
                newparams[ix] += delta * (2 * random.random() - 1)
            new = fnl(newparams, i)
            if (new < best):
                bestparams = newparams
                best = new
        if (bestparams == params):
            delta *= .5
        params = bestparams
        print '%', params, best, delta
        sys.stdout.flush()
    return bestparams

def desc_eval(params, dfdp, fnl, i, x):
    newparams = params[:]
    for ix in range(len(params)):
        newparams[ix] += x * dfdp[ix]
    return fnl(newparams, i)

def descend3(params, fnl):
    dp = 1e-6
    for i in range(1000):
        base = fnl(params, i, True)
        dfdp = []
        for ix in range(len(params)):
            newparams = params[:]
            newparams[ix] += dp
            new = fnl(newparams, i)
            dfdp.append((new - base) / dp)
        print '% dfdp = ', dfdp
        xr = 0.
        yr = base
        xm = -1e-3
        ym = desc_eval(params, dfdp, fnl, i, xm)
        if ym > yr:
            while ym > yr:
                xl, yl = xm, ym
                xm = .618034 * xl
                ym = desc_eval(params, dfdp, fnl, i, xm)
        else:
            xl = 1.618034 * xm
            yl = desc_eval(params, dfdp, fnl, i, xl)
            while ym > yl:
                xm, ym = xl, yl
                xl = 1.618034 * xm
                yl = desc_eval(params, dfdp, fnl, i, xl)

        # We have initial bracket; ym < yl and ym < yr

        x0, x3 = xl, xr
        if abs(xr - xm) > abs(xm - xl):
            x1, y1 = xm, ym
            x2 = xm + .381966 * (xr - xm)
            y2 = desc_eval(params, dfdp, fnl, i, x2)
        else:
            x2, y2 = xm, ym
            x1 = xm + .381966 * (xl - xm)
            y1 = desc_eval(params, dfdp, fnl, i, x1)
        for j in range(30):
            if y2 < y1:
                x0, x1, x2 = x1, x2, x2 + .381966 * (x3 - x2)
                y0, y1 = y1, y2
                y2 = desc_eval(params, dfdp, fnl, i, x2)
            else:
                x1, x2, x3 = x1 + .381966 * (x0 - x1), x1, x2
                y1 = desc_eval(params, dfdp, fnl, i, x1)
        if y1 < y2:
            xbest = x1
            ybest = y1
        else:
            xbest = x2
            ybest = y2
        for ix in range(len(params)):
            params[ix] += xbest * dfdp[ix]
        print '%', params, xbest, ybest
        sys.stdout.flush()
    return params

def mk_mvc_fnl(th0, th1):
    def fnl(params, i, do_print = False):
        k, k1, k2, k3, C = params
        ks, cost, x, y, th = run_mvc(k, k1, k2, k3, C, 100)
        cost *= hypot(y, x) ** 3
        actual_th0 = atan2(y, x)
        actual_th1 = th - actual_th0
        if do_print: print '%', x, y, actual_th0, actual_th1, cost
        err = (th0 - actual_th0) ** 2 + (th1 - actual_th1) ** 2
        multiplier = 1000
        return cost + err * multiplier
    return fnl

def mk_mec_fnl(th0, th1):
    def fnl(params, i, do_print = False):
        k, lam1, lam2 = params
        ks, cost, x, y, th = run_mec_cos(k, lam1, lam2)
        cost *= hypot(y, x)
        actual_th0 = atan2(y, x)
        actual_th1 = th - actual_th0
        if do_print: print '%', x, y, actual_th0, actual_th1, cost
        err = (th0 - actual_th0) ** 2 + (th1 - actual_th1) ** 2
        multiplier = 10
        return cost + err * multiplier
    return fnl

#ks, cost, x, y, th = run_mvc(0, 10, -10, 10, 200)
#print '%', cost, x, y
#print 'stroke showpage'

def mvc_test():
    fnl = mk_mvc_fnl(-pi, pi/4)
    params = [0, 0, 0, 0, 0]
    params = descend3(params, fnl)
    k, k1, k2, k3, C = params
    run_mvc(k, k1, k2, k3, C, 100, True)
    print 'stroke showpage'
    print '%', params

def mec_test():
    th0, th1 = pi/2, pi/2
    fnl = mk_mec_fnl(th0, th1)
    params = [0, 0, 0]
    params = descend2(params, fnl)
    k, lam1, lam2 = params
    run_mec_cos(k, lam1, lam2, 1000, True)
    print 'stroke showpage'
    print '%', params

mvc_test()
