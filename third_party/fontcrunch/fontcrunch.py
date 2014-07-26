# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Contributor: Raph Levien

from fontTools import ttLib
from fontTools.ttLib.tables import _g_l_y_f
import fromcubic
import tocubic
import pcorn
import math
import md5

import sys
import os

def lerppt(t, p0, p1):
	return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))

def glyph_to_bzs(g):
	bzs = []
	for i in range(g.numberOfContours):
		beg = 0 if i == 0 else g.endPtsOfContours[i - 1] + 1
		end = g.endPtsOfContours[i] + 1
		n = end - beg
		pts = g.coordinates[beg:end]
		flags = g.flags[beg:end]
		bz = []
		for j in range(n):
			x1, y1 = pts[(j+1) % n]
			if flags[j] and flags[(j+1) % n]:
				bz.append((pts[j], (x1, y1)))
			elif not flags[j]:
				if flags[j - 1]:
					x0, y0 = pts[j - 1]
				else:
					x0, y0 = lerppt(0.5, pts[j - 1], pts[j])
				if not flags[(j+1) % n]:
					x1, y1 = lerppt(0.5, (x1, y1), pts[j])
				if pts[j] == (x0, y0) or pts[j] == (x1, y1):
					# degenerate quad, treat as line
					bz.append(((x0, y0), (x1, y1)))
				else:
					bz.append(((x0, y0), pts[j], (x1, y1)))
		bzs.append(bz)
	return bzs

# convert all quadratics to cubics
def raise_to_cubic(bzs):
	result = []
	for sp in bzs:
		r = []
		for bz in sp:
			if len(bz) == 3:
				r.append((bz[0], lerppt(2./3, bz[0], bz[1]), lerppt(2./3, bz[2], bz[1]), bz[2]))
			else:
				r.append(bz)
		result.append(r)
	return result

def plot(bzs):
	tocubic.plot_prolog()
	print '/ss 1.5 def'
	print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
	fromcubic.plot_bzs(bzs, (100, 100), 0.25, fancy = True)
	print 'showpage'

def getbreaks(curve):
	extrema = curve.find_extrema()
	extrema.extend(curve.find_breaks())
	extrema.append(0)
	extrema.append(curve.arclen)
	extrema.sort()
	result = []
	for i in range(len(extrema)):
		if i == 0 or extrema[i] > extrema[i-1] + 0.1:
			result.append(extrema[i])
	print result
	return result

class Pt:
	def __init__(self, curve, s):
		self.s = s
		x, y = curve.xy(s)
		self.xy = (round(x), round(y))
		self.th = curve.th(s)

class MiniState:
	def __init__(self, score, sp):
		self.score = score
		self.sp = sp
	def combine(self, score, bz):
		newscore = self.score + score + penalty * (len(bz) - 1)
		if len(bz) == 3 and len(self.sp):
			lastbz = self.sp[-1]
			if len(lastbz) == 3:
				if lerppt(0.5, lastbz[1], bz[1]) == bz[0]:
					newscore -= penalty
		return MiniState(newscore, self.sp + [bz])

class State:
	def __init__(self, base):
		self.base = base  # a MiniState
		self.map = {}

penalty = 0.05

def measure_bz(curve, s0, s1, bz):
	bz_arclen = tocubic.bz_arclength_rk4(bz)
	if bz_arclen == 0: return 1e9
	arclen_scale = (s1 - s0) / bz_arclen
	def th_fn(s):
		return curve.th(s0 + arclen_scale * s, s == 0)
	return tocubic.measure_bz_rk4(bz, bz_arclen, th_fn)

def measure_line(curve, st, pt0, pt1):
	bz = (pt0.xy, pt1.xy)
	return st.combine(measure_bz(curve, pt0.s, pt1.s, bz), bz)

def intersect(xy0, th0, xy1, th1):
	x0, y0 = xy0
	x1, y1 = xy1
	dx0 = math.cos(th0)
	dy0 = math.sin(th0)
	dx1 = math.cos(th1)
	dy1 = math.sin(th1)
	det = dx0 * dy1 - dy0 * dx1
	if abs(det) < 1e-6: return None
	det = 1 / det
	a = y0 * dx0 - x0 * dy0
	b = y1 * dx1 - x1 * dy1
	x = (a * dx1 - b * dx0) * det
	y = (a * dy1 - b * dy0) * det
	return (x, y)

def measure_quad(curve, st, pt0, pt1):
	xy = intersect(pt0.xy, pt0.th, pt1.xy, pt1.th)
	if xy is None: return None
	x, y = xy
	x = round(x)
	y = round(y)
	bz = (pt0.xy, (x, y), pt1.xy)
	return st.combine(measure_bz(curve, pt0.s, pt1.s, bz), bz)

class Thcache:
	mult = 1
	def __init__(self, curve, s0, s1):
		self.s0 = s0
		self.s1 = s1
		self.ths1 = curve.th(s1, False)
		self.vals = []
		scale = 1.0 / self.mult
		for i in range(int(self.mult * (s1 - s0)) + 2):
			s = min(s1, s0 + i * scale)
			self.vals.append(curve.th(s, i == 0))
	def th(self, s, ds):
		if s > self.s1: return self.ths1
		s = self.mult * (s - self.s0)
		bucket = int(s)
		v0 = self.vals[bucket]
		v1 = self.vals[bucket + 1]
		return v0 + (s - bucket) * (v1 - v0)

# produce an optimized sequence of quadratics from s0 to s1 of the curve
def optimize_run(curve, s0, s1):
	print s0, s1
	n = int(round(1 * (s1 - s0)))
	pts = []
	for i in range(n + 1):
		pts.append(Pt(curve, s0 + (s1 - s0) * i / n))
	cache = Thcache(curve, s0, s1)
	states = [MiniState(0, [])]
	newst = measure_line(cache, states[0], pts[0], pts[n])
	bestst = newst
	newst = measure_quad(cache, states[0], pts[0], pts[n])
	if newst and newst.score < bestst.score:
		bestst = newst
	if bestst.score <= 3 * penalty:
		return bestst.sp
	# Quick scan for two-quad sections
	# Note, could do line+quad and quad+line too, but less likely to win
	for i in range(1, n):
		st1 = measure_quad(cache, states[0], pts[0], pts[i])
		if st1:
			st2 = measure_quad(cache, st1, pts[i], pts[n])
			if st2 and st2.score < bestst.score:
				bestst = st2
	if bestst.score <= 4 * penalty:
		return bestst.sp
	for i in range(1, n + 1):
		best = 1e9
		badcount = 0
		for j in range(i - 1, -1, -1):
			newst = measure_line(cache, states[j], pts[j], pts[i])
			if newst and newst.score < best:
				best, bestst = newst.score, newst
			newst = measure_quad(cache, states[j], pts[j], pts[i])
			if newst and newst.score < best:
				best, bestst = newst.score, newst
			if newst is None or newst.score - states[j].score > 10 * penalty:
				badcount += 1
				if badcount == 20:
					break
			else:
				badcount = 0
		states.append(bestst)
	return states[n].sp

def optimize(bzs):
	result = []
	for sp in fromcubic.bzs_to_pcorn(bzs):
		r = []
		curve = pcorn.Curve(sp)
		breaks = getbreaks(curve)
		for i in range(len(breaks) - 1):
			r.extend(optimize_run(curve, breaks[i], breaks[i + 1]))
		result.append(r)
	return result

def plot_tt_raw(bzs, fancy = True):
	x0 = 100
	y0 = 100
	scale = 0.25
	fromcubic.plot_bzs(raise_to_cubic(bzs), (x0, y0), scale)
	if fancy:
		for sp in bzs:
			for i in range(len(sp)):
				lastbz = sp[i - 1]
				bz = sp[i]
				if len(bz) != 3 or len(lastbz) != 3 or lerppt(0.5, lastbz[1], bz[1]) != bz[0]:
					x, y = bz[0]
					print 'gsave %f %f translate circle fill grestore' % (x * scale + x0, y * scale + y0)
				if len(bz) == 3:
					x, y = bz[1]
					print 'gsave %f %f translate circle stroke grestore' % (x * scale + x0, y * scale + y0)

def plot_tt(bzs, orig = None, style = 'redcyan'):
	tocubic.plot_prolog()
	print '/ss 2 def'
	print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
	if style == 'redcyan':
		print 'true setoverprint true setoverprintmode'
	x0 = 100
	y0 = 100
	scale = 0.25
	if orig:
		print '0 1 1 0 setcmykcolor'
		fancy = (style == 'redcyan')
		plot_tt_raw(orig, fancy)
	if style == 'redcyan':
		print '1 0 0 0 setcmykcolor'
	elif style == 'redblack':
		print '0 0 0 1 setcmykcolor'
	plot_tt_raw(bzs)
	print 'showpage'

def segment_sp(sp):
	bks = set()

	# direction changes
	xsg = 0
	ysg = 0
	for i in range(2 * len(sp)):
		imod = i % len(sp)
		xsg1 = sp[imod][-1][0] - sp[imod][0][0]
		ysg1 = sp[imod][-1][1] - sp[imod][0][1]
		if xsg * xsg1 < 0 or ysg * ysg1 < 0:
			bks.add(imod)
			xsg = xsg1
			ysg = ysg1
		else:
			if xsg == 0: xsg = xsg1
			if ysg == 0: ysg = ysg1

	# angle breaks
	for i in range(len(sp)):
		dx0 = sp[i-1][-1][0] - sp[i-1][-2][0]
		dy0 = sp[i-1][-1][1] - sp[i-1][-2][1]
		dx1 = sp[i][1][0] - sp[i][0][0]
		dy1 = sp[i][1][1] - sp[i][0][1]
		bend = dx1 * dy0 - dx0 * dy1
		if (dx0 == 0 and dy0 == 0) or (dx1 == 0 and dy1 == 0):
			bks.add(i)
		else:
			bend = bend / (math.hypot(dx0, dy0) * math.hypot(dx1, dy1))
			# for small angles, bend is in units of radians
			if abs(bend) > 0.02:
				bks.add(i)

	return sorted(bks)

def seg_to_string(sp, bk0, bk1):
	if bk1 < bk0:
		bk1 += len(sp)
	res = []
	for i in range(bk0, bk1):
		bz = sp[i % len(sp)]
		if len(bz) == 2:
			# just represent lines as quads
			bz = (bz[0], lerppt(0.5, bz[0], bz[1]), bz[1])
		res.append(' '.join(['%g' % z for xy in bz for z in xy]) + '\n')
	return ''.join(res)

USE_SUBDIRS = True

# get filename, ensuring directory exists
def seg_fn(segstr):
	fn = md5.new(segstr).hexdigest()[:16]
	if USE_SUBDIRS:
		dirname = fn[:2]
		if not os.path.exists(dirname):
			os.mkdir(dirname)
		fn = dirname + '/' + fn[2:]
	fn += '.bz'
	return fn

def gen_segs(glyph):
	bzs = glyph_to_bzs(glyph)
	for sp in bzs:
		bks = segment_sp(sp)
		for i in range(len(bks)):
			bk0, bk1 = bks[i], bks[(i + 1) % len(bks)]
			if bk1 != (bk0 + 1) % len(sp) or len(sp[bk0]) != 2:
				segstr = seg_to_string(sp, bk0, bk1)
				fn = seg_fn(segstr)
				file(fn, 'w').write(segstr)

def generate(fn):
	f = ttLib.TTFont(fn)
	glyf = f['glyf']
	for name, g in glyf.glyphs.iteritems():
		print 'generating', name
		gen_segs(g)

def read_bzs(fn):
	result = []
	for l in file(fn):
		z = [float(z) for z in l.split()]
		bz = ((z[0], z[1]), (z[2], z[3]), (z[4], z[5]))
		if bz[1] == lerppt(0.5, bz[0], bz[2]):
			bz = (bz[0], bz[2])
		result.append(bz)
	return result

def pt_to_int(pt):
	# todo: should investigate non-int points
	return (int(round(pt[0])), int(round(pt[1])))

def bzs_to_glyph(bzs, glyph):
	coordinates = []
	flags = []
	endPtsOfContours = []
	for sp in bzs:
		for i in range(len(sp)):
			lastbz = sp[i - 1]
			bz = sp[i]
			if len(bz) != 3 or len(lastbz) != 3 or lerppt(0.5, lastbz[1], bz[1]) != bz[0]:
				coordinates.append(pt_to_int(bz[0]))
				flags.append(1)
			if len(bz) == 3:
				coordinates.append(pt_to_int(bz[1]))
				flags.append(0)
		endPtsOfContours.append(len(coordinates) - 1)
	glyph.coordinates = _g_l_y_f.GlyphCoordinates(coordinates)
	glyph.flags = flags
	glyph.endPtsOfContours = endPtsOfContours

def repack_glyph(glyph):
	bzs = glyph_to_bzs(glyph)
	newbzs = []
	for sp in bzs:
		bks = segment_sp(sp)
		newsp = []
		for i in range(len(bks)):
			bk0, bk1 = bks[i], bks[(i + 1) % len(bks)]
			if bk1 != (bk0 + 1) % len(sp) or len(sp[bk0]) != 2:
				segstr = seg_to_string(sp, bk0, bk1)
				fn = seg_fn(segstr) + 'opt'
				newsp.extend(read_bzs(fn))
			else:
				newsp.append(sp[bk0])
		newbzs.append(newsp)
	bzs_to_glyph(newbzs, glyph)
	plot_tt(newbzs, bzs, style = 'redblack')

def repack(fn, newfn):
	f = ttLib.TTFont(fn)
	glyf = f['glyf']
	for name, g in glyf.glyphs.iteritems():
		if not g.isComposite():
			repack_glyph(g)
	if newfn:
		f.save(newfn)

def main(argv):
	if argv[1] == 'gen':
		generate(sys.argv[2])
	elif argv[1] == 'pack':
		repack(sys.argv[2], sys.argv[3] if len(argv) >= 3 else None)

main(sys.argv)
