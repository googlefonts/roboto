/*
ppedit - A pattern plate editor for Spiro splines.
Copyright (C) 2007 Raph Levien

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

*/
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "bezctx_intf.h"

/* The computation of fresnel integrals is adapted from: */

/*
Cephes Math Library Release 2.1:  December, 1988
Copyright 1984, 1987, 1988 by Stephen L. Moshier
Direct inquiries to 30 Frost Street, Cambridge, MA 02140
*/

double polevl( double x, double coef[], int N )
{
double ans;
int i;
double *p;

p = coef;
ans = *p++;
i = N;

do
	ans = ans * x  +  *p++;
while( --i );

return( ans );
}

/*							p1evl()	*/
/*                                          N
 * Evaluate polynomial when coefficient of x  is 1.0.
 * Otherwise same as polevl.
 */

double p1evl( double x, double coef[], int N )
{
double ans;
double *p;
int i;

p = coef;
ans = x + *p++;
i = N-1;

do
	ans = ans * x  + *p++;
while( --i );

return( ans );
}

static double sn[6] = {
-2.99181919401019853726E3,
 7.08840045257738576863E5,
-6.29741486205862506537E7,
 2.54890880573376359104E9,
-4.42979518059697779103E10,
 3.18016297876567817986E11,
};
static double sd[6] = {
/* 1.00000000000000000000E0,*/
 2.81376268889994315696E2,
 4.55847810806532581675E4,
 5.17343888770096400730E6,
 4.19320245898111231129E8,
 2.24411795645340920940E10,
 6.07366389490084639049E11,
};

static double cn[6] = {
-4.98843114573573548651E-8,
 9.50428062829859605134E-6,
-6.45191435683965050962E-4,
 1.88843319396703850064E-2,
-2.05525900955013891793E-1,
 9.99999999999999998822E-1,
};
static double cd[7] = {
 3.99982968972495980367E-12,
 9.15439215774657478799E-10,
 1.25001862479598821474E-7,
 1.22262789024179030997E-5,
 8.68029542941784300606E-4,
 4.12142090722199792936E-2,
 1.00000000000000000118E0,
};
static double fn[10] = {
  4.21543555043677546506E-1,
  1.43407919780758885261E-1,
  1.15220955073585758835E-2,
  3.45017939782574027900E-4,
  4.63613749287867322088E-6,
  3.05568983790257605827E-8,
  1.02304514164907233465E-10,
  1.72010743268161828879E-13,
  1.34283276233062758925E-16,
  3.76329711269987889006E-20,
};
static double fd[10] = {
/*  1.00000000000000000000E0,*/
  7.51586398353378947175E-1,
  1.16888925859191382142E-1,
  6.44051526508858611005E-3,
  1.55934409164153020873E-4,
  1.84627567348930545870E-6,
  1.12699224763999035261E-8,
  3.60140029589371370404E-11,
  5.88754533621578410010E-14,
  4.52001434074129701496E-17,
  1.25443237090011264384E-20,
};
static double gn[11] = {
  5.04442073643383265887E-1,
  1.97102833525523411709E-1,
  1.87648584092575249293E-2,
  6.84079380915393090172E-4,
  1.15138826111884280931E-5,
  9.82852443688422223854E-8,
  4.45344415861750144738E-10,
  1.08268041139020870318E-12,
  1.37555460633261799868E-15,
  8.36354435630677421531E-19,
  1.86958710162783235106E-22,
};
static double gd[11] = {
/*  1.00000000000000000000E0,*/
  1.47495759925128324529E0,
  3.37748989120019970451E-1,
  2.53603741420338795122E-2,
  8.14679107184306179049E-4,
  1.27545075667729118702E-5,
  1.04314589657571990585E-7,
  4.60680728146520428211E-10,
  1.10273215066240270757E-12,
  1.38796531259578871258E-15,
  8.39158816283118707363E-19,
  1.86958710162783236342E-22,
};

#ifndef M_PI
#define M_PI            3.14159265358979323846  /* pi */
#endif
#ifndef M_PI_2
#define M_PI_2          1.57079632679489661923  /* pi/2 */
#endif

int fresnl( xxa, ssa, cca )
double xxa, *ssa, *cca;
{
double f, g, cc, ss, c, s, t, u;
double x, x2;

x = fabs(xxa);
x2 = x * x;
if( x2 < 2.5625 )
	{
	t = x2 * x2;
	ss = x * x2 * polevl( t, sn, 5)/p1evl( t, sd, 6 );
	cc = x * polevl( t, cn, 5)/polevl(t, cd, 6 );
	goto done;
	}





#if 0
/* Note by RLL: the cutoff here seems low to me; perhaps it should be
   eliminated altogether. */
if( x > 36974.0 )
	{
	cc = 0.5;
	ss = 0.5;
	goto done;
	}
#endif

/*		Asymptotic power series auxiliary functions
 *		for large argument
 */
	x2 = x * x;
	t = M_PI * x2;
	u = 1.0/(t * t);
	t = 1.0/t;
	f = 1.0 - u * polevl( u, fn, 9)/p1evl(u, fd, 10);
	g = t * polevl( u, gn, 10)/p1evl(u, gd, 11);

	t = M_PI_2 * x2;
	c = cos(t);
	s = sin(t);
	t = M_PI * x;
	cc = 0.5  +  (f * s  -  g * c)/t;
	ss = 0.5  -  (f * c  +  g * s)/t;

done:
if( xxa < 0.0 )
	{
	cc = -cc;
	ss = -ss;
	}

*cca = cc;
*ssa = ss;
return(0);
}

/*
  End section adapted from Cephes math library. The following code is
  by Raph Levien.
*/

void eval_cornu(double t, double *ps, double *pc)
{
    double s, c;
    double rspio2 = 0.7978845608028653; /* 1 / sqrt(pi/2) */
    double spio2 = 1.2533141373155; /* sqrt(pi/2) */

    fresnl(t * rspio2, &s, &c);
    *ps = s * spio2;
    *pc = c * spio2;
}

double mod_2pi(double th) {
    double u = th * (1 / (2 * M_PI));
    return 2 * M_PI * (u - floor(u + 0.5));
}

void fit_cornu_half(double th0, double th1,
		    double *pt0, double *pt1,
		    double *pk0, double *pk1)
{
    int i;
    const int max_iter = 21;
    double t0, t1, t_m;
    double tl, tr, t_est;
    double s0, c0, s1, c1;
    /* This implementation uses bisection, which is simple but almost
       certainly not the fastest converging. If time is of the essence,
       use something like Newton-Raphson. */

    if (fabs(th0 + th1) < 1e-6) {
	th0 += 1e-6;
	th1 += 1e-6;
    }
    t_est = 0.29112 * (th1 + th0) / sqrt(th1 - th0);
    tl = t_est * .9;
    tr = t_est * 2;
    for (i = 0; i < max_iter; i++) {
	double dt;
	double chord_th;

	t_m = .5 * (tl + tr);
	dt = (th0 + th1) / (4 * t_m);
	t0 = t_m - dt;
	t1 = t_m + dt;
	eval_cornu(t0, &s0, &c0);
	eval_cornu(t1, &s1, &c1);
	chord_th = atan2(s1 - s0, c1 - c0);
	if (mod_2pi(chord_th - t0 * t0 - th0) < 0)
	    tl = t_m;
	else
	    tr = t_m;
    }
    *pt0 = t0;
    *pt1 = t1;
    if (pk0 || pk1) {
	double chordlen = hypot(s1 - s0, c1 - c0);
	if (pk0) *pk0 = t0 * chordlen;
	if (pk1) *pk1 = t1 * chordlen;
    }
}

/* Most of the time, this should give a fairly tight, yet conservative,
   (meaning it won't underestimate) approximation of the maximum error
   between a Cornu spiral segment and its quadratic Bezier fit.
*/
double
est_cornu_error(double t0, double t1)
{
    double t, u, est;

    if (t0 < 0 || t1 < 0) {
	t0 = -t0;
	t1 = -t1;
    }
    if (t1 < 0) {
	fprintf(stderr, "unexpected t1 sign\n");
    }
    if (t1 < t0) {
	double tmp = t0;
	t0 = t1;
	t1 = tmp;
    }
    if (fabs(t0) < 1e-9) {
	est = t1 * t1 * t1;
	est *= .017256 - .0059 - est * t1;
    } else {
	t = t1 - t0;
	t *= t;
	t *= t;
	est = t * fabs(t0 + t1 - 1.22084) / (t0 + t1);
	u = t0 + t1 + .6;
	u = u * u * u;
	est *= .014 * (.6 * u + 1);
	est += t * (t1 - t0) * .004;
    }
    return est;
}

void
affine_pt(const double aff[6], double x, double y, double *px, double *py) {
    *px = x * aff[0] + y * aff[2] + aff[4];
    *py = x * aff[1] + y * aff[3] + aff[5];
}

void
affine_multiply(double dst[6], const double src1[6], const double src2[6])
{
    double d0, d1, d2, d3, d4, d5;
    d0 = src1[0] * src2[0] + src1[1] * src2[2];
    d1 = src1[0] * src2[1] + src1[1] * src2[3];
    d2 = src1[2] * src2[0] + src1[3] * src2[2];
    d3 = src1[2] * src2[1] + src1[3] * src2[3];
    d4 = src1[4] * src2[0] + src1[5] * src2[2] + src2[4];
    d5 = src1[4] * src2[1] + src1[5] * src2[3] + src2[5];
    dst[0] = d0;
    dst[1] = d1;
    dst[2] = d2;
    dst[3] = d3;
    dst[4] = d4;
    dst[5] = d5;
}

void
fit_quadratic(double x0, double y0, double th0,
	      double x1, double y1, double th1,
	      double quad[6]) {
    double th;
    double s0, c0, s1, c1;
    double det, s, c;

    th = atan2(y1 - y0, x1 - x0);
    s0 = sin(th0 - th);
    c0 = cos(th0 - th);
    s1 = sin(th - th1);
    c1 = cos(th - th1);
    det = 1 / (s0 * c1 + s1 * c0);
    s = s0 * s1 * det;
    c = c0 * s1 * det;
    quad[0] = x0;
    quad[1] = y0;
    quad[2] = x0 + (x1 - x0) * c - (y1 - y0) * s;
    quad[3] = y0 + (y1 - y0) * c + (x1 - x0) * s;
    quad[4] = x1;
    quad[5] = y1;
}

void
cornu_seg_to_quad(double t0, double t1, const double aff[6], bezctx *bc)
{
    double x0, y0;
    double x1, y1;
    double th0 = t0 * t0;
    double th1 = t1 * t1;
    double quad[6];
    double qx1, qy1, qx2, qy2;

    eval_cornu(t0, &y0, &x0);
    eval_cornu(t1, &y1, &x1);
    fit_quadratic(x0, y0, th0, x1, y1, th1, quad);
    affine_pt(aff, quad[2], quad[3], &qx1, &qy1);
    affine_pt(aff, quad[4], quad[5], &qx2, &qy2);
    bezctx_quadto(bc, qx1, qy1, qx2, qy2);
}

void
cornu_seg_to_bpath(double t0, double t1, const double aff[6],
		   bezctx *bc, double tol)
{
    double tm;

    if ((t0 < 0 && t1 > 0) || (t1 < 0 && t0 > 0))
	tm = 0;
    else {
	if (fabs(t0 * t0 - t1 * t1) < 1.5 &&
	    est_cornu_error(t0, t1) < tol) {
	    cornu_seg_to_quad(t0, t1, aff, bc);
	    return;
	}
#if 0
	if (fabs(t0 - t1) < 1e-6) {
	  printf("DIVERGENCE!\007\n");
	  return;

	}
#endif
	tm = (t0 + t1) * .5;
    }

    cornu_seg_to_bpath(t0, tm, aff, bc, tol);
    cornu_seg_to_bpath(tm, t1, aff, bc, tol);
}

void
cornu_to_bpath(const double xs[], const double ys[], const double ths[], int n,
	       bezctx *bc, double tol, int closed, int kt0, int n_kt)
{
    int i;

    for (i = 0; i < n - 1 + closed; i++) {
	double x0 = xs[i], y0 = ys[i];
	int ip1 = (i + 1) % n;
	double x1 = xs[ip1], y1 = ys[ip1];
	double th = atan2(y1 - y0, x1 - x0);
	double th0 = mod_2pi(ths[i] - th);
	double th1 = mod_2pi(th - ths[ip1]);
	double t0, t1;
	double s0, c0, s1, c1;
	double chord_th, chordlen, rot, scale;
	double aff[6], aff2[6];
	double flip = -1;

	th1 += 1e-6;
	if (th1 < th0) {
	    double tmp = th0;
	    th0 = th1;
	    th1 = tmp;
	    flip = 1;
	}
	fit_cornu_half(th0, th1, &t0, &t1, NULL, NULL);
	if (flip == 1) {
	    double tmp = t0;
	    t0 = t1;
	    t1 = tmp;
	}
	eval_cornu(t0, &s0, &c0);
	s0 *= flip;
	eval_cornu(t1, &s1, &c1);
	s1 *= flip;
	chord_th = atan2(s1 - s0, c1 - c0);
	chordlen = hypot(s1 - s0, c1 - c0);
	rot = th - chord_th;
	scale = hypot(y1 - y0, x1 - x0) / chordlen;
	aff[0] = 1;
	aff[1] = 0;
	aff[2] = 0;
	aff[3] = flip;
	aff[4] = -c0;
	aff[5] = -s0;
	aff2[0] = scale * cos(rot);
	aff2[1] = scale * sin(rot);
	aff2[2] = -aff2[1];
	aff2[3] = aff2[0];
	aff2[4] = x0;
	aff2[5] = y0;
	affine_multiply(aff, aff, aff2);
	bezctx_mark_knot(bc, (kt0 + i) % n_kt);
	cornu_seg_to_bpath(t0, t1, aff, bc, tol / scale);
    }
}

/* fit arc to pts (0, 0), (x, y), and (1, 0), return th tangent to
   arc at (x, y) */
double fit_arc(double x, double y) {
    return atan2(y - 2 * x * y, y * y + x - x * x);
}

void
local_ths(const double xs[], const double ys[], double ths[], int n,
	  int closed)
{
    int i;

    for (i = 1 - closed; i < n - 1 + closed; i++) {
	int im1 = (i + n - 1) % n;
	double x0 = xs[im1];
	double y0 = ys[im1];
	double x1 = xs[i];
	double y1 = ys[i];
	int ip1 = (i + 1) % n;
	double x2 = xs[ip1];
	double y2 = ys[ip1];
	double dx = x2 - x0;
	double dy = y2 - y0;
	double ir2 = dx * dx + dy * dy;
	double x = ((x1 - x0) * dx + (y1 - y0) * dy) / ir2;
	double y = ((y1 - y0) * dx - (x1 - x0) * dy) / ir2;
	if (dx == 0.0 && dy == 0.0)
	  ths[i] = 0.0;
	else
	  ths[i] = fit_arc(x, y) + atan2(dy, dx);
    }
}

void
endpoint_ths(const double xs[], const double ys[], double ths[], int n)
{
    ths[0] = 2 * atan2(ys[1] - ys[0], xs[1] - xs[0]) - ths[1];
    ths[n - 1] = 2 * atan2(ys[n - 1] - ys[n - 2], xs[n - 1] - xs[n-2]) - ths[n - 2]; 
}

void
tweak_ths(const double xs[], const double ys[], double ths[], int n,
	  double delt, int closed)
{
    double *dks = (double *)malloc(sizeof(double) * n);
    int i;
    double first_k0, last_k1;

    for (i = 0; i < n - 1 + closed; i++) {
	double x0 = xs[i];
	double y0 = ys[i];
	int ip1 = (i + 1) % n;
	double x1 = xs[ip1];
	double y1 = ys[ip1];
	double th, th0, th1;
	double t0, t1, k0, k1;
	double s0, c0, s1, c1;
	double scale;
	double flip = -1;

	if (x0 == x1 && y0 == y1) {
#ifdef VERBOSE
	  printf("Overlapping points (i=%d)\n", i);
#endif
	  /* Very naughty, casting off the constness like this. */
	  ((double*) xs)[i] = x1 = x1 + 1e-6;
	}

	th = atan2(y1 - y0, x1 - x0);
	th0 = mod_2pi(ths[i] - th);
	th1 = mod_2pi(th - ths[ip1]);

	th1 += 1e-6;
	if (th1 < th0) {
	    double tmp = th0;
	    th0 = th1;
	    th1 = tmp;
	    flip = 1;
	}
	fit_cornu_half(th0, th1, &t0, &t1, &k0, &k1);
	if (flip == 1) {
	    double tmp = t0;
	    t0 = t1;
	    t1 = tmp;

	    tmp = k0;
	    k0 = k1;
	    k1 = tmp;
	}
	eval_cornu(t0, &s0, &c0);
	eval_cornu(t1, &s1, &c1);
	scale = 1 / hypot(y1 - y0, x1 - x0);
	k0 *= scale;
	k1 *= scale;
	if (i > 0) dks[i] = k0 - last_k1;
	else first_k0 = k0;
	last_k1 = k1;
    }
    if (closed)
      dks[0] = first_k0 - last_k1;
    for (i = 1 - closed; i < n - 1 + closed; i++) {
	int im1 = (i + n - 1) % n;
	double x0 = xs[im1];
	double y0 = ys[im1];
	double x1 = xs[i];
	double y1 = ys[i];
	int ip1 = (i + 1) % n;
	double x2 = xs[ip1];
	double y2 = ys[ip1];
	double chord1 = hypot(x1 - x0, y1 - y0);
	double chord2 = hypot(x2 - x1, y2 - y1);
	ths[i] -= delt * dks[i] * chord1 * chord2 / (chord1 + chord2);
    }
    free(dks);
}

void test_cornu(void)
{
#if 0
    int i;
    for (i = -10; i < 100; i++) {
	double t = 36974 * 1.2533141373155 + i * .1;
	double s, c;
	eval_cornu(t, &s, &c);
	printf("%g %g %g\n", t, s, c);
    }
#else
    double t0, t1;
    fit_cornu_half(0, 1, &t0, &t1, 0, 0);
    printf("%g %g\n", t0, t1);
#endif
}
