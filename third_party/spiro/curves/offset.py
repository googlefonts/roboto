# offset curve of piecewise cornu curves

from math import *

import pcorn
from clothoid import mod_2pi

def seg_offset(seg, d):
    th0 = seg.th(0)
    th1 = seg.th(seg.arclen)
    z0 = [seg.z0[0] + d * sin(th0), seg.z0[1] - d * cos(th0)]
    z1 = [seg.z1[0] + d * sin(th1), seg.z1[1] - d * cos(th1)]
    chth = atan2(z1[1] - z0[1], z1[0] - z0[0])
    return [pcorn.Segment(z0, z1, mod_2pi(chth - th0), mod_2pi(th1 - chth))]


def offset(curve, d):
    segs = []
    for seg in curve.segs:
        segs.extend(seg_offset(seg, d))
    return pcorn.Curve(segs)
