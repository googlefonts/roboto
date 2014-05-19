from curveFitPen import fitGlyph,segmentGlyph
import numpy as np
from numpy.linalg import norm
import math
from scipy.sparse.linalg import cg

def glyphToMesh(g):
    points = []
    edges = {}
    offset = 0
    for c in g.contours:
        if len(c) < 2:
            continue
        for i,prev,next in rangePrevNext(len(c)):
            points.append((c[i].points[0].x, c[i].points[0].y))
            edges[i + offset] = np.array([prev + offset, next + offset], dtype=int)
        offset += len(c)
    return np.array(points), edges

def meshToGlyph(points, g):
    g1 = g.copy()
    j = 0
    for c in g1.contours:
        if len(c) < 2:
            continue
        for i in range(len(c)):
            c[i].points[0].x = points[j][0]
            c[i].points[0].y = points[j][1]
            j += 1
    return g1

def italicize(glyph, angle=12, stemWidth=180, xoffset=-50):
    ga,subsegments = segmentGlyph(glyph,25)
    va, e  = glyphToMesh(ga)
    n = len(va)
    grad = mapEdges(lambda a,(p,n): normalize(p-a), va, e)
    cornerWeights = mapEdges(lambda a,(p,n): normalize(p-a).dot(normalize(a-n)), grad, e)[:,0].reshape((-1,1))
    smooth = np.ones((n,1)) * .02
    smooth[cornerWeights < .6] = 5
    # smooth[cornerWeights >= .9999] = 2
    out = va.copy()
    if stemWidth > 100:
        out = skewMesh(poisson(skewMesh(out, angle * 2), grad, e, smooth=smooth), -angle * 2)
        out = copyMeshDetails(va, out, e, 6)
    # return meshToGlyph(out,ga)
    normals = edgeNormals(out, e)
    center = va + normals * stemWidth * .4
    if stemWidth > 100:
        center[:, 0] = va[:, 0]
    centerSkew = skewMesh(center.dot(np.array([[.97,0],[0,1]])), angle * .7)
    # centerSkew = skewMesh(center, angle * .7)
    out = out + (centerSkew - center)
    out = copyMeshDetails(skewMesh(va, angle * .7), out, e, 12)
    out = skewMesh(out, angle * .3)
    out[:,0] += xoffset
    # out[:,1] = va[:,1]
    gOut = meshToGlyph(out, ga)
    # gOut.width *= .97
    gOut.width += 10
    # return gOut
    return fitGlyph(glyph, gOut, subsegments)

def poisson(v, grad, e, smooth=1, P=None, distance=None):
    n = len(v)
    if distance == None:
        distance = mapEdges(lambda a,(p,n): norm(p - a), v, e)
    if (P == None):
        P = mP(v,e)
        P += np.identity(n) * smooth
    f = v.copy()
    for i,(prev,next) in e.iteritems():
        f[i] = (grad[next] * distance[next] - grad[i] * distance[i])
    out = v.copy()
    f += v * smooth
    for i in range(len(out[0,:])):
        out[:,i] = cg(P, f[:,i])[0]
    return out

def mP(v,e):
    n = len(v)
    M = np.zeros((n,n))
    for i, edges in e.iteritems():
        w = -2 / float(len(edges))
        for index in edges:
            M[i,index] = w
        M[i,i] = 2
    return M

def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v/n
    
def mapEdges(func,v,e,*args):
    b = v.copy()
    for i, edges in e.iteritems():
        b[i] = func(v[i], [v[j] for j in edges], *args)
    return b
    
def getNormal(a,b,c):
    "Assumes TT winding direction"
    p = np.roll(normalize(b - a), 1)
    n = -np.roll(normalize(c - a), 1)
    p[1] *= -1
    n[1] *= -1
    # print p, n, normalize((p + n) * .5)
    return normalize((p + n) * .5)

def edgeNormals(v,e):
    "Assumes a mesh where each vertex has exactly least two edges"
    return mapEdges(lambda a,(p,n) : getNormal(a,p,n),v,e)

def rangePrevNext(count):
    c = np.arange(count,dtype=int)
    r = np.vstack((c, np.roll(c, 1), np.roll(c, -1)))
    return r.T

def skewMesh(v,angle):
    slope = np.tanh([math.pi * angle / 180])
    return v.dot(np.array([[1,0],[slope,1]]))


from scipy.ndimage.filters import gaussian_filter1d as gaussian

def labelConnected(e):
    label = 0
    labels = np.zeros((len(e),1))
    for i,(prev,next) in e.iteritems():
        labels[i] = label
        if next <= i:
            label += 1
    return labels

def copyGradDetails(a,b,e,scale=15):
    n = len(a)
    labels = labelConnected(e)
    out = a.astype(float).copy()
    for i in range(labels[-1]+1):
        mask = (labels==i).flatten()
        out[mask,:] = gaussian(b[mask,:], scale, mode="wrap", axis=0) + a[mask,:] - gaussian(a[mask,:], scale, mode="wrap", axis=0)
    return out

def copyMeshDetails(va,vb,e,scale=5,smooth=.01):
    gradA = mapEdges(lambda a,(p,n): normalize(p-a), va, e)
    gradB = mapEdges(lambda a,(p,n): normalize(p-a), vb, e)
    grad = copyGradDetails(gradA, gradB, e, scale)
    return poisson(vb, grad, e, smooth=smooth)