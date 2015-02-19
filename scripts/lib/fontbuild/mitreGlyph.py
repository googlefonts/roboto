"""Mitre Glyph: 

mitreSize : Length of the segment created by the mitre. The default is 4.
maxAngle :  Maximum angle in radians at which nodes will be mitred. The default is .9 (about 50 degrees).
            Works for both inside and outside angles

"""

import math
from robofab.objects.objectsRF import RPoint, RSegment

def getTangents(contours):
    tmap = []
    for c in contours:
        clen = len(c)
        for i in range(clen):
            n = c[i]
            p = RPoint(n.points[-1].x, n.points[-1].y)
            nn = c[(i + 1) % clen]
            pn = c[(clen + i - 1) % clen]
            if nn.type == 'curve':
                np = RPoint(nn.points[1].x,nn.points[1].y)
            else:
                np = RPoint(nn.points[-1].x,nn.points[-1].y)
            if n.type == 'curve':
                pp = RPoint(n.points[2].x,n.points[2].y)
            else:
                pp = RPoint(pn.points[-1].x,pn.points[-1].y)
            nVect = RPoint(-p.x + np.x, -p.y + np.y)
            pVect = RPoint(-p.x + pp.x, -p.y + pp.y)
            tmap.append((pVect,nVect))
    return tmap    

def normalizeVector(p):
    m = getMagnitude(p);
    if m != 0:
        return p*(1/m)
    else:
        return RPoint(0,0)

def getMagnitude(p):
    return math.sqrt(p.x*p.x + p.y*p.y)
    
def getDistance(v1,v2):
    return getMagnitude(RPoint(v1.x - v2.x, v1.y - v2.y))

def getAngle(v1,v2):
    angle = math.atan2(v1.y,v1.x) - math.atan2(v2.y,v2.x)
    return (angle + (2*math.pi)) % (2*math.pi)
    
def angleDiff(a,b):
    return math.pi - abs((abs(a - b) % (math.pi*2)) - math.pi)

def getAngle2(v1,v2):
    return abs(angleDiff(math.atan2(v1.y, v1.x), math.atan2(v2.y, v2.x)))

def getMitreOffset(n,v1,v2,mitreSize=4,maxAngle=.9):
    
    # dont mitre if segment is too short
    if abs(getMagnitude(v1)) < mitreSize * 2 or abs(getMagnitude(v2)) < mitreSize * 2:
        return
    angle = getAngle2(v2,v1)
    v1 = normalizeVector(v1)
    v2 = normalizeVector(v2)
    if v1.x == v2.x and v1.y == v2.y:
        return
    
    
    # only mitre corners sharper than maxAngle
    if angle > maxAngle:
        return
    
    radius = mitreSize / abs(getDistance(v1,v2))
    offset1 = RPoint(round(v1.x * radius), round(v1.y * radius))
    offset2 = RPoint(round(v2.x * radius), round(v2.y * radius))
    return offset1, offset2

def mitreGlyph(g,mitreSize,maxAngle):
    if g == None:
        return
    
    tangents = getTangents(g.contours)
    nid = -1
    for c in g.contours:
        nodes = []
        needsMitring = False
        for n in c:
            nid += 1
            v1, v2 = tangents[nid]
            off = getMitreOffset(n,v1,v2,mitreSize,maxAngle)
            n1 = n.copy()
            if off != None:
                offset1, offset2 = off
                n2 = RSegment('line', [(n.points[-1].x + offset2.x,
                                        n.points[-1].y + offset2.y)])
                n1.points[0].x += offset1.x
                n1.points[0].y += offset1.y
                nodes.append(n1)
                nodes.append(n2)
                needsMitring = True
            else:
                nodes.append(n1)
        if needsMitring:
            while len(c):
                c.removeSegment(0)
            for n in nodes:
                c.appendSegment(
                    n.type, [(p.x, p.y) for p in n.points], n.smooth)
