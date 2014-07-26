from math import *
import cornu

def mod_2pi(th):
    u = th / (2 * pi)
    return 2 * pi * (u - floor(u + 0.5))

# Given clothoid k(s) = k0 + k1 s, compute th1 - th0 of chord from s = -.5
# to .5.
def compute_dth(k0, k1):
    if k1 < 0:
        return -compute_dth(k0, -k1)
    elif k1 == 0:
        return 0
    sqrk1 = sqrt(2 * k1)
    t0 = (k0 - .5 * k1) / sqrk1
    t1 = (k0 + .5 * k1) / sqrk1
    (y0, x0) = cornu.eval_cornu(t0)
    (y1, x1) = cornu.eval_cornu(t1)
    chord_th = atan2(y1 - y0, x1 - x0)
    return mod_2pi(t1 * t1 - chord_th) - mod_2pi(chord_th - t0 * t0)

def compute_chord(k0, k1):
    if k1 == 0:
        if k0 == 0:
            return 1
        else:
            return sin(k0 * .5) / (k0 * .5)
    sqrk1 = sqrt(2 * abs(k1))
    t0 = (k0 - .5 * k1) / sqrk1
    t1 = (k0 + .5 * k1) / sqrk1
    (y0, x0) = cornu.eval_cornu(t0)
    (y1, x1) = cornu.eval_cornu(t1)
    return hypot(y1 - y0, x1 - x0) / abs(t1 - t0)

# Given th0 and th1 at endpoints (measured from chord), return k0
# and k1 such that the clothoid k(s) = k0 + k1 s, evaluated from
# s = -.5 to .5, has the tangents given
def solve_clothoid(th0, th1, verbose = False):
    k0 = th0 + th1

    # initial guess
    k1 = 6 * (th1 - th0)
    error = (th1 - th0) - compute_dth(k0, k1)
    if verbose:
        print k0, k1, error

    k1_old, error_old = k1, error
    # second guess based on d(dth)/dk1 ~ 1/6
    k1 += 6 * error
    error = (th1 - th0) - compute_dth(k0, k1)
    if verbose:
        print k0, k1, error

    # secant method
    for i in range(10):
        if abs(error) < 1e-9: break
        k1_old, error_old, k1 = k1, error, k1 + (k1_old - k1) * error / (error - error_old)
        error = (th1 - th0) - compute_dth(k0, k1)
        if verbose:
            print k0, k1, error

    return k0, k1

if __name__ == '__main__':
    print solve_clothoid(.06, .05, True)
