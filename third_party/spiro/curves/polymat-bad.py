from Numeric import *
import LinearAlgebra as la
import sys

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
print ''
for j in range(n + 1):
    for k in range(4):
        print '%7.2f' % mi[j * 4 + k][(n / 2) * 4 + 2],
    print ''
