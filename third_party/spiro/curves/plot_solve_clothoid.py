import clothoid
from math import *

print '%!PS-Adobe'

def integ_spiro(k0, k1, k2, k3, n = 4):
    th1 = k0
    th2 = .5 * k1
    th3 = (1./6) * k2
    th4 = (1./24) * k3
    ds = 1. / n
    ds2 = ds * ds
    ds3 = ds2 * ds
    s = .5 * ds - .5

    k0 *= ds
    k1 *= ds
    k2 *= ds
    k3 *= ds

    x = 0
    y = 0

    for i in range(n):
	if n == 1:
	    km0 = k0
	    km1 = k1 * ds
	    km2 = k2 * ds2
        else:
	    km0 = (((1./6) * k3 * s + .5 * k2) * s + k1) * s + k0
	    km1 = ((.5 * k3 * s + k2) * s + k1) * ds
	    km2 = (k3 * s + k2) * ds2
	km3 = k3 * ds3

	t1_1 = km0
	t1_2 = .5 * km1
	t1_3 = (1./6) * km2
	t1_4 = (1./24) * km3
	t2_2 = t1_1 * t1_1
	t2_3 = 2 * (t1_1 * t1_2)
	t2_4 = 2 * (t1_1 * t1_3) + t1_2 * t1_2
	t2_5 = 2 * (t1_1 * t1_4 + t1_2 * t1_3)
	t2_6 = 2 * (t1_2 * t1_4) + t1_3 * t1_3
	t2_7 = 2 * (t1_3 * t1_4)
	t2_8 = t1_4 * t1_4
	t3_4 = t2_2 * t1_2 + t2_3 * t1_1
	t3_6 = t2_2 * t1_4 + t2_3 * t1_3 + t2_4 * t1_2 + t2_5 * t1_1
	t3_8 = t2_4 * t1_4 + t2_5 * t1_3 + t2_6 * t1_2 + t2_7 * t1_1
	t3_10 = t2_6 * t1_4 + t2_7 * t1_3 + t2_8 * t1_2
	t4_4 = t2_2 * t2_2
	t4_5 = 2 * (t2_2 * t2_3)
	t4_6 = 2 * (t2_2 * t2_4) + t2_3 * t2_3
	t4_7 = 2 * (t2_2 * t2_5 + t2_3 * t2_4)
	t4_8 = 2 * (t2_2 * t2_6 + t2_3 * t2_5) + t2_4 * t2_4
	t4_9 = 2 * (t2_2 * t2_7 + t2_3 * t2_6 + t2_4 * t2_5)
	t4_10 = 2 * (t2_2 * t2_8 + t2_3 * t2_7 + t2_4 * t2_6) + t2_5 * t2_5
	t5_6 = t4_4 * t1_2 + t4_5 * t1_1
	t5_8 = t4_4 * t1_4 + t4_5 * t1_3 + t4_6 * t1_2 + t4_7 * t1_1
	t5_10 = t4_6 * t1_4 + t4_7 * t1_3 + t4_8 * t1_2 + t4_9 * t1_1
	t6_6 = t4_4 * t2_2
	t6_7 = t4_4 * t2_3 + t4_5 * t2_2
	t6_8 = t4_4 * t2_4 + t4_5 * t2_3 + t4_6 * t2_2
	t6_9 = t4_4 * t2_5 + t4_5 * t2_4 + t4_6 * t2_3 + t4_7 * t2_2
	t6_10 = t4_4 * t2_6 + t4_5 * t2_5 + t4_6 * t2_4 + t4_7 * t2_3 + t4_8 * t2_2
	t7_8 = t6_6 * t1_2 + t6_7 * t1_1
	t7_10 = t6_6 * t1_4 + t6_7 * t1_3 + t6_8 * t1_2 + t6_9 * t1_1
	t8_8 = t6_6 * t2_2
	t8_9 = t6_6 * t2_3 + t6_7 * t2_2
	t8_10 = t6_6 * t2_4 + t6_7 * t2_3 + t6_8 * t2_2
	t9_10 = t8_8 * t1_2 + t8_9 * t1_1
	t10_10 = t8_8 * t2_2
        u = 1
        u -= (1./24) * t2_2 + (1./160) * t2_4 + (1./896) * t2_6 + (1./4608) * t2_8
        u += (1./1920) * t4_4 + (1./10752) * t4_6 + (1./55296) * t4_8 + (1./270336) * t4_10
        u -= (1./322560) * t6_6 + (1./1658880) * t6_8 + (1./8110080) * t6_10
        u += (1./92897280) * t8_8 + (1./454164480) * t8_10
        u -= 2.4464949595157930e-11 * t10_10
        v = (1./12) * t1_2 + (1./80) * t1_4
        v -= (1./480) * t3_4 + (1./2688) * t3_6 + (1./13824) * t3_8 + (1./67584) * t3_10
        v += (1./53760) * t5_6 + (1./276480) * t5_8 + (1./1351680) * t5_10
        v -= (1./11612160) * t7_8 + (1./56770560) * t7_10
        v += 2.4464949595157932e-10 * t9_10
	if n == 1:
	    x = u
	    y = v
        else:
	    th = (((th4 * s + th3) * s + th2) * s + th1) * s
	    cth = cos(th)
	    sth = sin(th)

	    x += cth * u - sth * v
	    y += cth * v + sth * u
	    s += ds
    return [x * ds, y * ds]

count_iter = 0

# Given th0 and th1 at endpoints (measured from chord), return k0
# and k1 such that the clothoid k(s) = k0 + k1 s, evaluated from
# s = -.5 to .5, has the tangents given
def solve_clothoid(th0, th1, verbose = False):
    global count_iter

    k1_old = 0
    e_old = th1 - th0
    k0 = th0 + th1
    k1 = 6 * (1 - ((.5 / pi) * k0) ** 3) * e_old

    # secant method
    for i in range(10):
	x, y = integ_spiro(k0, k1, 0, 0)
        e = (th1 - th0) + 2 * atan2(y, x) - .25 * k1
	count_iter += 1
        if verbose:
            print k0, k1, e
        if abs(e) < 1e-9: break
        k1_old, e_old, k1 = k1, e, k1 + (k1_old - k1) * e / (e - e_old)

    return k0, k1

def plot_by_thp():
    count = 0
    for i in range(11):
	thp = i * .1
	print .5 + .05 * i, .5, .5, 'setrgbcolor'
	print '.75 setlinewidth'
	cmd = 'moveto'
	for j in range(-40, 41):
	    thm = j * .02
	    k0, k1 = solve_clothoid(thp - thm, thp + thm, True)
	    count += 1
	    k1 = min(40, max(-40, k1))
	    print 306 + 75 * thm, 396 - 10 * k1, cmd
	    cmd = 'lineto'
	print 'stroke'
	print '% count_iter = ', count_iter, 'for', count

def plot_by_thm():
    print '.75 setlinewidth'
    print 36, 396 - 350, 'moveto'
    print 0, 700, 'rlineto stroke'
    for i in range(-10, 10):
	if i == 0: wid = 636
	else: wid = 5
	print 36, 396 - 10 * i, 'moveto', wid, '0 rlineto stroke'
    cmd = 'moveto'
    thm = -.1
    for i in range(41):
	thp = i * .1
	k0, k1 = solve_clothoid(thp - thm, thp + thm)
	print 36 + 150 * thp, 396 - 100 * k1, cmd
	cmd = 'lineto'
    print 'stroke'
    print '0 0 1 setrgbcolor'
    cmd = 'moveto'
    for i in range(41):
	thp = i * .1
	k1 = 12 * thm * cos(.5 * thp)
	k1 = 12 * thm * (1 - (thp / pi) ** 3)
	print 36 + 150 * thp, 396 - 100 * k1, cmd
	cmd = 'lineto'
    print 'stroke'

plot_by_thp()
