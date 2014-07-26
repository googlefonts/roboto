#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    const char *fn;
    int xs;
    int ys;
    unsigned char *buf;
} pgm;

typedef struct {
    int xs;
    int ys;
    int *sum;
    int *count;
} blendbuf;

static void
die (char *why)
{
  fprintf (stderr, "%s\n", why);
  exit (1);
}

#define MAX_SIZE 65536

pgm *load_pgm(const char *fn)
{
    FILE *fi = fopen(fn, "rb");
    pgm *result;
    char buf[256];
    int xs, ys;
    int depth;

    if (fi == NULL)
	return NULL;

    fgets (buf, sizeof(buf), fi);
    if (buf[0] != 'P' || buf[1] != '5')
	die ("Need pgmraw image on input");

    xs = ys = 0;
    do
	fgets (buf, sizeof(buf), fi);
    while (buf[0] == '#');
    sscanf (buf, "%d %d", &xs, &ys);
    if (xs <= 0 || ys <= 0 || xs > MAX_SIZE || ys > MAX_SIZE)
	die ("Input image size out of range");

    do
	fgets (buf, sizeof(buf), fi);
    while (buf[0] == '#');
    sscanf (buf, "%d", &depth);
    if (depth != 255)
	die ("Only works with depth=255 images");

    result = (pgm *)malloc(sizeof(pgm));

    result->fn = fn;
    result->xs = xs;
    result->ys = ys;
    result->buf = (unsigned char *)malloc(xs * ys);

    fread(result->buf, 1, xs * ys, fi);
    fprintf(stderr, "loaded file %s %dx%d\n", fn, xs, ys);
    fclose(fi);
    return result;
}

int
align_pgms(const pgm *p1, const pgm *p2, int *px, int *py)
{
    int xo, yo;
    int xa, ya;
    int best = 0x7fffffff;

    xa = (p1->xs < p2->xs ? p1->xs : p2->xs) - 20;
    ya = (p1->ys < p2->ys ? p1->ys : p2->ys) - 20;

    for (yo = -10; yo <= 10; yo++)
	for (xo = -10; xo <= 10; xo++) {
	    int sum = 0;
	    int i, j;

	    for (j = 0; j < ya; j++)
		for (i = 0; i < xa; i++) {
		    int g1 = p1->buf[(j + 10) * p1->xs + i + 10];
		    int g2 = p2->buf[(j + 10 - yo) * p2->xs + i - xo + 10];
		    sum += (g1 - g2) * (g1 - g2);
		}
	    if (sum < best) {
		best = sum;
		*px = xo;
		*py = yo;
	    }
	}
    return best;
}

blendbuf *
new_blendbuf(int xs, int ys)
{
    blendbuf *result = (blendbuf *)malloc(sizeof(blendbuf));
    int i;

    result->xs = xs;
    result->ys = ys;
    result->sum = (int *)malloc(sizeof(int) * xs * ys);
    result->count = (int *)malloc(sizeof(int) * xs * ys);
    for (i = 0; i < xs * ys; i++) {
	result->sum[i] = 0;
	result->count[i] = 0;
    }

    return result;
}

void
add_pgm(blendbuf *bb, pgm *p, int xo, int yo)
{
    int i, j;

    for (j = 0; j < p->ys; j++) {
	if (j + yo >= 0 && j + yo < bb->ys) {
	    for (i = 0; i < p->xs; i++) {
		if (i + xo >= 0 && i + xo < bb->xs) {
		    int ix = (j + yo) * bb->xs + i + xo;
		    bb->sum[ix] += p->buf[j * p->xs + i];
		    bb->count[ix]++;
		}
	    }
	}
    }
}

pgm *
pgm_from_blendbuf(blendbuf *bb)
{
    int xs = bb->xs;
    int ys = bb->ys;
    pgm *result = (pgm *)malloc(sizeof(pgm));
    int i, j;

    result->xs = xs;
    result->ys = ys;
    result->buf = (unsigned char *)malloc(xs * ys);

    for (j = 0; j < ys; j++) {
	for (i = 0; i < xs; i++) {
	    int ix = j * xs + i;
	    unsigned char g;
	    if (bb->count[ix])
		g = (bb->sum[ix] + (bb->count[ix] >> 1)) / bb->count[ix];
	    else
		g = 255;
	    result->buf[ix] = g;
	}
    }
    return result;
}

pgm *
pgm_from_blendbuf_enhanced(blendbuf *bb, double sharp, double gamma)
{
    int xs = bb->xs;
    int ys = bb->ys;
    pgm *result = (pgm *)malloc(sizeof(pgm));
    int i, j;
    double ming = 255, maxg = 0;
    double *tmpbuf;

    result->xs = xs;
    result->ys = ys;
    result->buf = (unsigned char *)malloc(xs * ys);

    tmpbuf = (double *)malloc(xs * ys * sizeof(double));

    for (j = 0; j < ys; j++) {
	for (i = 0; i < xs; i++) {
	    int ix = j * xs + i;
	    double g;
	    if (bb->count[ix]) {
		g = ((double)bb->sum[ix]) / bb->count[ix];
		if (g < ming) ming = g;
		if (g > maxg) maxg = g;
	    } else
		g = 255.0;
	    tmpbuf[ix] = g;
	}
    }
    for (j = 0; j < ys; j++) {
	for (i = 0; i < xs; i++) {
	    int ix = j * xs + i;
	    double g;
	    if (bb->count[ix]) {
		int u, v;
		int cnt = 0;
		double sum = 0;

		for (v = -1; v <= 1; v++) {
		    for (u = -1; u <= 1; u++) {
			if (i + u >= 0 && i + u < xs &&
			    j + v >= 0 && j + v < ys &&
			    bb->count[(j + v) * xs + i + u]) {
			    sum += tmpbuf[(j + v) * xs + i + u];
			    cnt += 1;
			}
		    }
		}

		g = (1 + sharp) * tmpbuf[ix] - sharp * sum / cnt;
		g = (g - ming) / (maxg - ming);
		if (g < 0) g = 0;
		if (g > 1) g = 1;
		g = pow(g, gamma);
	    } else
		g = 1;
	    result->buf[ix] = (int)(255 * g + 0.5);
	}
    }
    free(tmpbuf);
    return result;
}

void
print_pgm(pgm *p, FILE *f)
{
    fprintf(f, "P5\n%d %d\n255\n", p->xs, p->ys);
    fwrite(p->buf, 1, p->xs * p->ys, f);
}

void
threshold(pgm *p)
{
    int i;

    for (i = 0; i < p->xs * p->ys; i++)
	p->buf[i] = p->buf[i] > 128 ? 1 : 0;
}

int 
classify(pgm **pgmlist, int n_pgm)
{
    int *class = (int *)malloc(sizeof(int) * n_pgm);
    int n_class = 0;
    int i, j;
    int tshift = 4;

    for (i = 0; i < n_pgm; i++)
	class[i] = -1;

    for (i = 0; i < n_pgm; i++) {
	pgm *pi = pgmlist[i];

	if (class[i] == -1) {
	    class[i] = n_class++;
	    for (j = i + 1; j < n_pgm; j++) {
		pgm *pj = pgmlist[j];
		int xo, yo;
		int score;

		if (abs(pi->xs - pj->xs) < 10 &&
		    abs(pi->ys - pj->ys) < 10) {
		    score = align_pgms(pi, pj, &xo, &yo);
		    if (score < ((pi->xs - 20) * (pi->ys - 20)) >> tshift) {
			class[j] = class[i];
		    }
		}
	    }
	}
	printf("%s: class%d\n", pi->fn, class[i]);
	fflush(stdout);
    }
    free(class);
    return 0;
}


static int
intcompar(const void *a, const void *b) {
    return *((int *)a) - *((int *)b);
}

int
do_blend(pgm **pgmlist, int n_pgm, int n_passes, float thresh)
{
    blendbuf *bb;
    int pass;
    int i;
    pgm *base = pgmlist[0];
    int *scores, *scores2, *xos, *yos;

    scores = (int *)malloc(n_pgm * sizeof(int));
    scores2 = (int *)malloc(n_pgm * sizeof(int));
    xos = (int *)malloc(n_pgm * sizeof(int));
    yos = (int *)malloc(n_pgm * sizeof(int));

    for (pass = 0; pass < n_passes; pass++) {
	int scorethresh;

	bb = new_blendbuf(base->xs, base->ys);
	for (i = 0; i < n_pgm; i++) {
	    int xo, yo;
	    int score = align_pgms(base, pgmlist[i], &xo, &yo);
	    fprintf(stderr, "%s: score = %d, offset = %d, %d\n",	
		pgmlist[i]->fn, score, xo, yo);
	    scores[i] = score;
	    xos[i] = xo;
	    yos[i] = yo;
	}

	if (pass == 0) {
	    scorethresh = 0x7fffffff;
	} else {
	    memcpy(scores2, scores, n_pgm * sizeof(int));
	    qsort(scores2, n_pgm, sizeof(int), intcompar);
	    scorethresh = scores2[(int)(thresh * n_pgm)];
	}

	for (i = 0; i < n_pgm; i++) {
	    if (pass > 0)
		fprintf(stderr, "%s: score = %d %s\n",
			pgmlist[i]->fn, scores[i],
			scores[i] <= scorethresh ? "ok" : "-");
	    if (scores[i] <= scorethresh)
		add_pgm(bb, pgmlist[i], xos[i], yos[i]);
	}

	if (pass == n_passes - 1)
	    base = pgm_from_blendbuf_enhanced(bb, 5, 0.5);
	else
	    base = pgm_from_blendbuf(bb);
	if (pass != n_passes - 1)
	    fprintf(stderr, "\n");
    }

    free(scores);
    free(xos);
    free(yos);
    print_pgm(base, stdout);
    return 0;
}

int
main(int argc, char **argv)
{
    int i;
    int n_pgm = 0;
    pgm **pgmlist = (pgm **)malloc(sizeof(pgm *) * argc - 1);
    int do_class = 0;
    int n_pass = 2;
    float thresh = 0.90;

    for (i = 1; i < argc; i++) {
	if (!strcmp(argv[i], "-c"))
	    do_class = 1;
	else
	    pgmlist[n_pgm++] = load_pgm(argv[i]);
    }

    if (do_class) {
	for (i = 0; i < n_pgm; i++)
	    threshold(pgmlist[i]);
	return classify(pgmlist, n_pgm);
    } else {
	return do_blend(pgmlist, n_pgm, n_pass, thresh);
    }

    return 0;
}
