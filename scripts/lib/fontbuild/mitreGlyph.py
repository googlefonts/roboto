"""Mitre Glyph: 

mitreSize : Length of the segment created by the mitre. The default is 4.
maxAngle :  Maximum angle in radians at which nodes will be mitred. The default is .9 (about 50 degrees).
            Works for both inside and outside angles

"""

import math

def getContours(g):
    nLength = len(g.nodes)
    contours = []
    cid = -1
    for i in range(nLength):
        n = g.nodes[i]
        if n.type == nMOVE:
            cid += 1
            contours.append([])
        contours[cid].append(n)
    return contours

def getTangents(contours):
    tmap = []
    for c in contours:
        clen = len(c)
        for i in range(clen):
            n = c[i]
            p = Point(n.x, n.y)
            nn = c[(i + 1) % clen]
            pn = c[(clen + i - 1) % clen]
            if nn.type == nCURVE:
                np = Point(nn[1].x,nn[1].y)
            else:
                np = Point(nn.x,nn.y)    
            if n.type == nCURVE:
                pp = Point(n[2].x,n[2].y)
            else:
                pp = Point(pn.x,pn.y)
            nVect = Point(-p.x + np.x, -p.y + np.y)
            pVect = Point(-p.x + pp.x, -p.y + pp.y)
            tmap.append((pVect,nVect))
    return tmap    

def normalizeVector(p):
    m = getMagnitude(p);
    if m != 0:
        return p*(1/m)
    else:
        return Point(0,0)

def getMagnitude(p):
    return math.sqrt(p.x*p.x + p.y*p.y)
    
def getDistance(v1,v2):
    return getMagnitude(Point(v1.x - v2.x, v1.y - v2.y))

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
    offset1 = Point(round(v1.x * radius), round(v1.y * radius))
    offset2 = Point(round(v2.x * radius), round(v2.y * radius))
    return offset1, offset2

def mitreGlyph(g,mitreSize,maxAngle):
    if g == None:
        return
    
    contours = getContours(g)
    tangents = getTangents(contours)
    nodes = []
    needsMitring = False
    nid = -1
    for c in contours:
        for n in c:
            nid += 1
            v1, v2 = tangents[nid]
            off = getMitreOffset(n,v1,v2,mitreSize,maxAngle)
            n1 = Node(n)
            if off != None:
                offset1, offset2 = off
                n2 = Node(nLINE, Point(n.x + offset2.x, n.y + offset2.y))
                n1[0].x += offset1.x
                n1[0].y += offset1.y
                nodes.append(n1)
                nodes.append(n2)
                needsMitring = True
            else:
                nodes.append(n1)
    if needsMitring:
        g.Clear()
        g.Insert(nodes)
