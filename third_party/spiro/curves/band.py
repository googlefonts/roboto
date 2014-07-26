# A little solver for band-diagonal matrices. Based on NR Ch 2.4.

from math import *

from Numeric import *

do_pivot = True

def bandec(a, m1, m2):
    n, m = a.shape
    mm = m1 + m2 + 1
    if m != mm:
        raise ValueError('Array has width %d expected %d' % (m, mm))
    al = zeros((n, m1), Float)
    indx = zeros(n, Int)

    for i in range(m1):
        l = m1 - i
        for j in range(l, mm): a[i, j - l] = a[i, j]
        for j in range(mm - l, mm): a[i, j] = 0

    d = 1.

    l = m1
    for k in range(n):
        dum = a[k, 0]
        pivot = k
        if l < n: l += 1
        if do_pivot:
            for j in range(k + 1, l):
                if abs(a[j, 0]) > abs(dum):
                    dum = a[j, 0]
                    pivot = j
        indx[k] = pivot
        if dum == 0.: a[k, 0] = 1e-20
        if pivot != k:
            d = -d
            for j in range(mm):
                tmp = a[k, j]
                a[k, j] = a[pivot, j]
                a[pivot, j] = tmp
        for i in range(k + 1, l):
            dum = a[i, 0] / a[k, 0]
            al[k, i - k - 1] = dum
            for j in range(1, mm):
                a[i, j - 1] = a[i, j] - dum * a[k, j]
            a[i, mm - 1] = 0.
    return al, indx, d

def banbks(a, m1, m2, al, indx, b):
    n, m = a.shape
    mm = m1 + m2 + 1
    l = m1
    for k in range(n):
        i = indx[k]
        if i != k:
            tmp = b[k]
            b[k] = b[i]
            b[i] = tmp
        if l < n: l += 1
        for i in range(k + 1, l):
            b[i] -= al[k, i - k - 1] * b[k]
    l = 1
    for i in range(n - 1, -1, -1):
        dum = b[i]
        for k in range(1, l):
            dum -= a[i, k] * b[k + i]
        b[i] = dum / a[i, 0]
        if l < mm: l += 1

if __name__ == '__main__':
    a = zeros((10, 3), Float)
    for i in range(10):
        a[i, 0] = 1
        a[i, 1] = 2
        a[i, 2] = 1
    print a
    al, indx, d = bandec(a, 1, 1)
    print a
    print al
    print indx
    b = zeros(10, Float)
    b[5] = 1
    banbks(a, 1, 1, al, indx, b)
    print b
