#! /usr/bin/env python

"""
Converts a cubic bezier curve to a quadratic spline with 
exactly two off curve points.

"""

import numpy
from numpy import array,cross,dot
from fontTools.misc import bezierTools
from FL import *
    
def calcIntersect(a,b,c,d):
    numpy.seterr(all='raise')
    e = b-a
    f = d-c
    p = array([-e[1], e[0]])
    try:
        h = dot((a-c),p) / dot(f,p)
    except:
        print a,b,c,d
        raise
    return c + dot(f,h)

def simpleConvertToQuadratic(p0,p1,p2,p3):
    p = [array(i.x,i.y) for i in [p0,p1,p2,p3]]
    off = calcIntersect(p[0],p[1],p[2],p[3])

# OFFCURVE_VECTOR_CORRECTION = -.015
OFFCURVE_VECTOR_CORRECTION = 0

def convertToQuadratic(p0,p1,p2,p3):
    # TODO: test for accuracy and subdivide further if needed
    p = [(i.x,i.y) for i in [p0,p1,p2,p3]]
    # if p[0][0] == p[1][0] and p[0][0] == p[2][0] and p[0][0] == p[2][0] and p[0][0] == p[3][0]:
    #     return (p[0],p[1],p[2],p[3]) 
    # if p[0][1] == p[1][1] and p[0][1] == p[2][1] and p[0][1] == p[2][1] and p[0][1] == p[3][1]:
    #     return (p[0],p[1],p[2],p[3])     
    seg1,seg2 = bezierTools.splitCubicAtT(p[0], p[1], p[2], p[3], .5)
    pts1 = [array([i[0], i[1]]) for i in seg1]
    pts2 = [array([i[0], i[1]]) for i in seg2]
    on1 = seg1[0]
    on2 = seg2[3]
    try:
        off1 = calcIntersect(pts1[0], pts1[1], pts1[2], pts1[3])
        off2 = calcIntersect(pts2[0], pts2[1], pts2[2], pts2[3])
    except:
        return (p[0],p[1],p[2],p[3])
    off1 = (on1 - off1) * OFFCURVE_VECTOR_CORRECTION + off1
    off2 = (on2 - off2) * OFFCURVE_VECTOR_CORRECTION + off2
    return (on1,off1,off2,on2)

def cubicNodeToQuadratic(g,nid):
    
    node = g.nodes[nid]
    if (node.type != nCURVE):
        print "Node type not curve"
        return
    
    #pNode,junk = getPrevAnchor(g,nid)
    pNode = g.nodes[nid-1] #assumes that a nCURVE type will always be proceeded by another point on the same contour
    points = convertToQuadratic(pNode[0],node[1],node[2],node[0])
    points = [Point(p[0],p[1]) for p in points]
    curve = [ 
              Node(nOFF, points[1]),
              Node(nOFF, points[2]),
              Node(nLINE,points[3]) ]
    return curve

def glyphCurvesToQuadratic(g):

    nodes = []
    for i in range(len(g.nodes)):
        n = g.nodes[i]
        if n.type == nCURVE:
            try:
                newNodes = cubicNodeToQuadratic(g, i)
                nodes = nodes + newNodes
            except Exception:
                print g.name, i
                raise
        else:
            nodes.append(Node(g.nodes[i]))
    g.Clear()
    g.Insert(nodes)
    



