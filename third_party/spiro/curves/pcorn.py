# Utilities for piecewise cornu representation of curves

from math import *

import clothoid
import cornu

class Segment:
    def __init__(self, z0, z1, th0, th1):
        self.z0 = z0
        self.z1 = z1
        self.th0 = th0
        self.th1 = th1
        self.compute()
    def __repr__(self):
        return '[' + `self.z0` + `self.z1` + ' ' + `self.th0` + ' ' + `self.th1` + ']'
    def compute(self):
        dx = self.z1[0] - self.z0[0]
        dy = self.z1[1] - self.z0[1]
        chord = hypot(dy, dx)
        chth = atan2(dy, dx)
        k0, k1 = clothoid.solve_clothoid(self.th0, self.th1)
        charc = clothoid.compute_chord(k0, k1)

        self.chord = chord
        self.chth = chth
        self.k0, self.k1 = k0, k1
        self.charc = charc
        self.arclen = chord / charc
        self.thmid = self.chth - self.th0 + 0.5 * self.k0 - 0.125 * self.k1

        self.setup_xy_fresnel()

    def setup_xy_fresnel(self):
        k0, k1 = self.k0, self.k1
        if k1 == 0: k1 = 1e-6 # hack
        if k1 != 0:
            sqrk1 = sqrt(2 * abs(k1))
            t0 = (k0 - .5 * k1) / sqrk1
            t1 = (k0 + .5 * k1) / sqrk1
            (y0, x0) = cornu.eval_cornu(t0)
            (y1, x1) = cornu.eval_cornu(t1)
            chord_th = atan2(y1 - y0, x1 - x0)
            chord = hypot(y1 - y0, x1 - x0)
            scale = self.chord / chord
            if k1 >= 0:
                th = self.chth - chord_th
                self.mxx = scale * cos(th)
                self.myx = scale * sin(th)
                self.mxy = -self.myx
                self.myy = self.mxx
            else:
                th = self.chth + chord_th
                self.mxx = scale * cos(th)
                self.myx = scale * sin(th)
                self.mxy = self.myx
                self.myy = -self.mxx
                # rotate -chord_th, flip top/bottom, rotate self.chth
            self.x0 = self.z0[0] - (self.mxx * x0 + self.mxy * y0)
            self.y0 = self.z0[1] - (self.myx * x0 + self.myy * y0)

    def th(self, s):
        u = s / self.arclen - 0.5
        return self.thmid + (0.5 * self.k1 * u + self.k0) * u

    def xy(self, s):
        # using fresnel integrals; polynomial approx might be better
        u = s / self.arclen - 0.5
        k0, k1 = self.k0, self.k1
        if k1 == 0: k1 = 1e-6 # hack
        if k1 != 0:
            sqrk1 = sqrt(2 * abs(k1))
            t = (k0 + u * k1) / sqrk1
            (y, x) = cornu.eval_cornu(t)
            return [self.x0 + self.mxx * x + self.mxy * y,
                    self.y0 + self.myx * x + self.myy * y]

    def find_extrema(self):
        # find solutions of th(s) = 0 mod pi/2
        # todo: find extra solutions when there's an inflection
        th0 = self.thmid + 0.125 * self.k1 - 0.5 * self.k0
        th1 = self.thmid + 0.125 * self.k1 + 0.5 * self.k0
        twooverpi = 2 / pi
        n0 = int(floor(th0 * twooverpi))
        n1 = int(floor(th1 * twooverpi))
        if th1 > th0: signum = 1
        else: signum = -1
        result = []
        for i in range(n0, n1, signum):
            th = pi/2 * (i + 0.5 * (signum + 1))
            a = .5 * self.k1
            b = self.k0
            c = self.thmid - th
            if a == 0:
                u1 = -c/b
                u2 = 1000
            else:
                sqrtdiscrim = sqrt(b * b - 4 * a * c)
                u1 = (-b - sqrtdiscrim) / (2 * a)
                u2 = (-b + sqrtdiscrim) / (2 * a)
            if u1 >= -0.5 and u1 < 0.5:
                result.append(self.arclen * (u1 + 0.5))
            if u2 >= -0.5 and u2 < 0.5:
                result.append(self.arclen * (u2 + 0.5))
        return result

class Curve:
    def __init__(self, segs):
        self.segs = segs
        self.compute()
    def compute(self):
        arclen = 0
        sstarts = []
        for seg in self.segs:
            sstarts.append(arclen)
            arclen += seg.arclen

        self.arclen = arclen
        self.sstarts = sstarts
    def th(self, s, deltas = False):
        u = s / self.arclen
        s = self.arclen * (u - floor(u))
        if s == 0 and not deltas: s = self.arclen
        i = 0
        while i < len(self.segs) - 1:
            # binary search would make a lot of sense here
            snext = self.sstarts[i + 1] 
            if s < snext or (not deltas and s == snext):
                break
            i += 1
        return self.segs[i].th(s - self.sstarts[i])
    def xy(self, s):
        u = s / self.arclen
        s = self.arclen * (u - floor(u))
        i = 0
        while i < len(self.segs) - 1:
            # binary search would make a lot of sense here
            if s <= self.sstarts[i + 1]:
                break
            i += 1
        return self.segs[i].xy(s - self.sstarts[i])
    def find_extrema(self):
        result = []
        for i in range(len(self.segs)):
            seg = self.segs[i]
            for s in seg.find_extrema():
                result.append(s + self.sstarts[i])
        return result
    def find_breaks(self):
        result = []
        for i in range(len(self.segs)):
            pseg = self.segs[(i + len(self.segs) - 1) % len(self.segs)]
            seg = self.segs[i]
            th = clothoid.mod_2pi(pseg.chth + pseg.th1 - (seg.chth - seg.th0))
            print '% pseg', pseg.chth + pseg.th1, 'seg', seg.chth - seg.th0
            pisline = pseg.k0 == 0 and pseg.k1 == 0
            sisline = seg.k0 == 0 and seg.k1 == 0
            if fabs(th) > 1e-3 or (pisline and not sisline) or (sisline and not pisline):
                result.append(self.sstarts[i])
        return result
