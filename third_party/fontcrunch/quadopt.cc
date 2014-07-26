/*
 * Copyright 2014 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Contributor: Raph Levien
 */

#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
#include <algorithm>

using std::vector;

#define HALF_STEP 1

class Point {
public:
	Point() : x(0), y(0) { }
	Point(double x, double y) : x(x), y(y) { }
	double x, y;
};

bool operator==(const Point& p0, const Point& p1) {
	return p0.x == p1.x && p0.y == p1.y;
}

std::ostream& operator<<(std::ostream& os, const Point& p) {
	os << "(" << p.x << ", " << p.y << ")";
	return os;
}

double dist(Point p0, Point p1) {
	return std::hypot(p0.x - p1.x, p0.y - p1.y);
}

double dist2(Point p0, Point p1) {
	double dx = p0.x - p1.x;
	double dy = p0.y - p1.y;
	return dx * dx + dy * dy;
}

Point lerp(double t, Point p0, Point p1) {
	return Point(p0.x + t * (p1.x - p0.x), p0.y + t * (p1.y - p0.y));
}

Point unitize(Point p) {
	double scale = 1/std::hypot(p.x, p.y);
	return Point(p.x * scale, p.y * scale);
}

Point round(Point p) {
	return Point(std::round(p.x), std::round(p.y));
}

class Quad {
public:
	Quad() : p() { }
	Quad(Point p0, Point p1, Point p2) : p() {
		p[0] = p0;
		p[1] = p1;
		p[2] = p2;
	}
	Point p[3];
	double arclen() const;
	Point eval(double t) const;
	bool isLine() const;
	void print(std::ostream& o) const {
		o << p[0].x << " " << p[0].y << " " << p[1].x << " " << p[1].y << " "
			<< p[2].x << " " << p[2].y << std::endl;
	}
};

bool Quad::isLine() const {
	return p[1] == lerp(0.5, p[0], p[2]);
}

// One step of a 4th-order Runge-Kutta numerical integration
template <size_t n, typename F>
void rk4(double y[n], double x, double h, F& derivs) {
	double dydx[n];
	double dyt[n];
	double dym[n];
	double yt[n];
	derivs(dydx, x, y);
	double hh = h * .5;
	double h6 = h * (1./6);
	for (size_t i = 0; i < n; i++) {
		yt[i] = y[i] + hh * dydx[i];
	}
	derivs(dyt, x + hh, yt);
	for (size_t i = 0; i < n; i++) {
		yt[i] = y[i] + hh * dyt[i];
	}
	derivs(dym, x + hh, yt);
	for (size_t i = 0; i < n; i++) {
		yt[i] = y[i] + h * dym[i];
		dym[i] += dyt[i];
	}
	derivs(dyt, x + h, yt);
	for (size_t i = 0; i < n; i++) {
		y[i] += h6 * (dydx[i] + dyt[i] + 2 * dym[i]);
	}
}

class ArclenFunctor {
public:
	ArclenFunctor(const Quad& q)
			: dx0(2 * (q.p[1].x - q.p[0].x))
			, dx1(2 * (q.p[2].x - q.p[1].x))
			, dy0(2 * (q.p[1].y - q.p[0].y))
			, dy1(2 * (q.p[2].y - q.p[1].y)) { }
	void operator()(double dydx[1], double t, const double y[1]) {
		Point p(deriv(t));
		dydx[0] = std::hypot(p.x, p.y);
	}
	Point deriv(double t) const {
		return Point(dx0 + t * (dx1 - dx0), dy0 + t * (dy1 - dy0));
	}
private:
	double dx0, dy0, dx1, dy1;
};

double Quad::arclen() const {
	ArclenFunctor derivs(*this);
	const int n = 10;
	double dt = 1./n;
	double t = 0;
	double y[1] = { 0 };
	for (int i = 0; i < n; i++) {
		rk4<1>(y, t, dt, derivs);
		t += dt;
	}
	return y[0];
}

Point Quad::eval(double t) const {
	Point p01(lerp(t, p[0], p[1]));
	Point p12(lerp(t, p[1], p[2]));
	return lerp(t, p01, p12);
}

class Thetas {
public:
	void init(const vector<Quad>& qs);
	Point xy(double s) const;
	Point dir(double s) const;
	double arclen;
private:
	vector<Point> xys;
	vector<Point> dirs;
};

void Thetas::init(const vector<Quad>& qs) {
	xys.clear();
	dirs.clear();
	double s = 0;
	int ix = 0;
	Point lastxy;
	Point lastd;
	double lasts = -1;
	for (size_t i = 0; i < qs.size(); i++) {
		const Quad& q = qs[i];
		ArclenFunctor derivs(q);
		const int n = 100;
		double dt = 1./n;
		double t = 0;
		double y[1];
		y[0] = s;
		for (int j = 0; j < n; j++) {
			Point thisxy(q.eval(t));
			Point thisd(derivs.deriv(t));
			while (ix <= y[0]) {
				double u = (ix - lasts) / (y[0] - lasts);
				xys.push_back(lerp(u, lastxy, thisxy));
				dirs.push_back(unitize(lerp(u, lastd, thisd)));
				ix++;
			}
			lasts = y[0];
			rk4<1>(y, t, dt, derivs);
			t += dt;
			lastxy = thisxy;
			lastd = thisd;
		}
		s = y[0];
	}
	const Quad& q = qs[qs.size() - 1];
	Point thisxy(q.p[2]);
	Point thisd(ArclenFunctor(q).deriv(1));
	while (ix <= s + 1) {
		double u = (ix - lasts) / (s - lasts);
		xys.push_back(lerp(u, lastxy, thisxy));
		dirs.push_back(unitize(lerp(u, lastd, thisd)));
		ix++;
	}
	arclen = s;
}

Point Thetas::xy(double s) const {
	int bucket = (int)s;
	double frac = s - bucket;
	return lerp(frac, xys[bucket], xys[bucket + 1]);
}

Point Thetas::dir(double s) const {
	int bucket = (int)s;
	double frac = s - bucket;
	return lerp(frac, dirs[bucket], dirs[bucket + 1]);
}

#define NORM_LEVEL 2

// L1 angle norm, 2, L2 angle norm, 0.05
// L1 distance norm, 200
double penalty = 1;
double dist_factor = .005;
double angle_factor = 5;


class MeasureFunctor {
public:
	MeasureFunctor(const Thetas& curve, double s0, double ss, const ArclenFunctor& af,
			Quad q)
		: curve(curve), s0(s0), ss(ss), af(af), q(q) { }
	void operator()(double dydx[2], double t, const double y[2]) {
		Point dxy(af.deriv(t));
		dydx[0] = std::hypot(dxy.x, dxy.y);

		// distance error
		Point curvexy = curve.xy(s0 + y[0] * ss);
#if NORM_LEVEL == 1
		double disterr = dist(q.eval(t), curvexy);
#endif
#if NORM_LEVEL == 2
		double disterr = dist2(q.eval(t), curvexy);
#endif
		disterr *= dydx[0];

		// angle error
		Point dir = curve.dir(s0 + y[0] * ss);
		double angleerr = dir.x * dxy.y - dir.y * dxy.x;
#if NORM_LEVEL == 1
		angleerr = std::abs(angleerr);
#endif
#if NORM_LEVEL == 2
		angleerr = (angleerr * angleerr) / dydx[0];
#endif

		dydx[1] = dist_factor * disterr + angle_factor * angleerr;
	}
private:
	const Thetas& curve;
	double s0;
	double ss;
	const ArclenFunctor& af;
	Quad q;
};

// measure how closely the quad fits the section of curve, using L1 norm
// of angle mismatch
double measureQuad(const Thetas& curve, double s0, double s1, const Quad& q) {
	ArclenFunctor derivs(q);
	double ss = (s1 - s0) / q.arclen();
	MeasureFunctor err(curve, s0, ss, derivs, q);
	const int n = 10;
	double dt = 1./n;
	double t = 0;
	double y[2] = { 0, 0 };
	for (int i = 0; i < n; i++) {
		rk4<2>(y, t, dt, err);
		t += dt;
	}
	return y[1];
}

struct Break {
	Break(double s, Point xy, Point dir) : s(s), xy(xy), dir(dir) { }
	double s;
	Point xy;
	Point dir;
};

struct Statelet {
	void combine(const Statelet* prev, double score, Quad q);
	const Statelet* prev;
	double score;
	Quad q;
};

void Statelet::combine(const Statelet* newprev, double newscore, Quad newq) {
	prev = newprev;
	double pmul = 2;
	if (newq.isLine()) {
		pmul = 1;
	} else if (newprev != 0 && !newprev->q.isLine()
			&& lerp(0.5, newprev->q.p[1], newq.p[1]) == newq.p[0]) {
		pmul = 1;
	}
	score = (newprev == 0 ? 0 : newprev->score) + penalty * pmul + newscore;
	q = newq;
}

struct State {
	void combine(const State* prev, double score, Quad q);
	vector<Statelet> sts;
	bool init;
};

void State::combine(const State* prev, double score, Quad q) {
	const Statelet* prevsl = prev->sts.empty() ? 0 : &prev->sts[0];
	if (prevsl == 0 && !prev->init) {
		return;
	}
	Statelet sl;
	sl.combine(prevsl, score, q);
	if (sts.empty()) {
		sts.push_back(sl);
	} else {
		if (sl.score < sts[0].score) {
			sts[0] = sl;
		}
	}
}

bool isInt(double x) {
	return x == (int) x;
}

bool okForHalf(const State* prev, Quad q) {
	if (isInt(q.p[0].x) && isInt(q.p[0].y)) {
		return true;
	}
	if (q.isLine()) {
		return false;
	}
	const Statelet* prevsl = prev->sts.empty() ? 0 : &prev->sts[0];

	if (prevsl == 0 || prevsl->q.isLine()) {
		return false;
	}
	return lerp(0.5, prevsl->q.p[1], q.p[1]) == q.p[0];
}

void findBreaks(vector<Break>* breaks, const Thetas& curve) {
	breaks->clear();
	double lastd;
	int n = round(10 * curve.arclen);
	for (int i = 0; i <= n; i++) {
		double s = curve.arclen * i / n;
		Point origp = curve.xy(s);
#if HALF_STEP
		Point p(.5 * std::round(2 * origp.x), .5 * std::round(2 * origp.y));
#else
		Point p = round(origp);
#endif
		double d = dist(p, origp);
		if (i == 0 || !(p == (*breaks)[breaks->size() - 1].xy)) {
			Break bk(s, p, curve.dir(s));
			breaks->push_back(bk);
			lastd = d;
		} else if (d < lastd) {
			(*breaks)[breaks->size() - 1] = Break(s, p, curve.dir(s));
			lastd = d;
		}
	}
}

bool intersect(Point* result, Point p0, Point dir0, Point p1, Point dir1) {
	double det = dir0.x * dir1.y - dir0.y * dir1.x;
	if (std::abs(det) < 1e-6) return false;
	det = 1 / det;
	double a = p0.y * dir0.x - p0.x * dir0.y;
	double b = p1.y * dir1.x - p1.x * dir1.y;
	result->x = (a * dir1.x - b * dir0.x) * det;
	result->y = (a * dir1.y - b * dir0.y) * det;
	return true;
}

void tryQuad(const State* prev, State* st, const Thetas& curve,
	const Break& bk0, const Break& bk1, const Quad& q) {
	double score = measureQuad(curve, bk0.s, bk1.s, q);
	st->combine(prev, score, q);
}

void tryLineQuad(const State* prev, State* st, const Thetas& curve,
	const Break& bk0, const Break& bk1) {
	if (isInt(bk0.xy.x) && isInt(bk0.xy.y)) {
		Quad line(bk0.xy, lerp(0.5, bk0.xy, bk1.xy), bk1.xy);
		tryQuad(prev, st, curve, bk0, bk1, line);
	}
	Point pmid;
	if (intersect(&pmid, bk0.xy, bk0.dir, bk1.xy, bk1.dir)) {
		Quad q(bk0.xy, round(pmid), bk1.xy);
		if (okForHalf(prev, q)) {
			tryQuad(prev, st, curve, bk0, bk1, q);
		}
	}
}

vector<Quad> optimize(const Thetas& curve) {
	vector<Break> breaks;
	findBreaks(&breaks, curve);
	int n = breaks.size() - 1;
	vector<State> states;
	states.resize(n + 1);
	states[0].init = true;
	tryLineQuad(&states[0], &states[n], curve, breaks[0], breaks[n]);
	if (states[n].sts[0].score <= 3 * penalty) {
		goto done;
	}
	for (int i = 1; i < n; i++) {
		tryLineQuad(&states[0], &states[i], curve, breaks[0], breaks[i]);
		tryLineQuad(&states[i], &states[n], curve, breaks[i], breaks[n]);
	}
	if (states[n].sts[0].score <= 4 * penalty) {
		goto done;
	}
	for (int i = 1; i <= n; i++) {
		for (int j = i - 1; j >= 0; j--) {
			tryLineQuad(&states[j], &states[i], curve, breaks[j], breaks[i]);
		}
	}
done:
	vector<Quad> result;
	for (const Statelet* sl = &states[n].sts[0]; sl != 0; sl = sl->prev) {
		result.push_back(sl->q);
	}
	std::reverse(result.begin(), result.end());
	return result;
}

void readBzs(vector<Quad>* result, std::istream& is) {
	double x0, y0, x1, y1, x2, y2;
	while (is >> x0 >> y0 >> x1 >> y1 >> x2 >> y2) {
		result->push_back(Quad(Point(x0, y0), Point(x1, y1), Point(x2, y2)));
	}
	// Round the endpoints, they must be on integers
	(*result)[0].p[0] = round((*result)[0].p[0]);
	Quad* lastq = &(*result)[(*result).size()];
	lastq->p[2] = round(lastq->p[2]);
}

int main(int argc, char** argv) {
	if (argc != 3) {
		std::cerr << "usage: quadopt in out\n";
		return 1;
	}
#if 0
	Quad q(Point(100, 0), Point(0, 0), Point(0, 100));
	std::cout.precision(8);
	std::cout << q.arclen() << "\n";
#endif
	vector<Quad> bzs;
	std::ifstream is;
	is.open(argv[1]);
	readBzs(&bzs, is);
	Thetas thetas;
	thetas.init(bzs);
#if 0
	for (int i = 0; i < thetas.arclen; i++) {
		Point xy = thetas.dir(i);
		std::cout << xy.x << " " << xy.y << std::endl;
	}
#endif
	vector<Quad> optbzs = optimize(thetas);
	std::ofstream os;
	os.open(argv[2]);
	for (size_t i = 0; i < optbzs.size(); i++) {
		optbzs[i].print(os);
	}
	return 0;
}
