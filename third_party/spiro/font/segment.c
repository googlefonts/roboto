#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))

typedef struct {
    int x0;
    int x1;
    int y0;
    int y1;
    double xmom;
    double ymom;
    int area;
} seg;

typedef struct {
    int x0;
    int x1;
} run;

void
find_runs(run *result, const unsigned char *buf, unsigned char thresh, int xs)
{
    int x;
    int j = 0;

    for (x = 0; x < xs;) {
	int x0, x1;
	for (x0 = x; x0 < xs; x0++)
	    if (buf[x0] < thresh)
		break;
	if (x0 == xs)
	    break;
	for (x1 = x0 + 1; x1 < xs; x1++)
	    if (buf[x1] >= thresh)
		break;
	result[j].x0 = x0;
	result[j].x1 = x1;
	j++;
	x = x1 + 1;
    }
    result[j].x0 = 0;
    result[j].x1 = 0;
}

void
print_rect(const seg *r)
{
    printf("%d %d %d %d %g rect\n", r->x0, r->y0, r->x1, r->y1,
	   r->area / (1.0 * (r->x1 - r->x0) * (r->y1 - r->y0)));
    printf("%g %g ci\n", r->xmom / r->area, r->ymom / r->area);
}

void
merge_runs(seg *buf, const run *new_runs, int y)
{
    int bi, ni;
    int bs;
    int bi0;
    int flag;

    for (bs = 0; buf[bs].x1; bs++);

    bi = 0;
    flag = 1;
    for (ni = 0; new_runs[ni].x1; ni++) {
	int run_len = new_runs[ni].x1 - new_runs[ni].x0;

	bi0 = bi;
	for (; bi < bs && buf[bi].x1 <= new_runs[ni].x0; bi++) {
	    if (flag) {
		buf[bi].y1 = y;
		print_rect(&buf[bi]);
	    } else {
		bi0 = bi + 1;
		flag = 1;
	    }
	}
	if (bi > bi0) {
	    memmove(&buf[bi0], &buf[bi], (bs - bi) * sizeof(seg));
	    bs += bi0 - bi;
	}
	bi = bi0;
	if (bi < bs && buf[bi].x0 < new_runs[ni].x1) {
	    double xmom = buf[bi].xmom;
	    double ymom = buf[bi].ymom;
	    int area = buf[bi].area;
	    int y0 = buf[bi].y0;

	    for (bi = bi + 1; bi < bs && buf[bi].x0 < new_runs[ni].x1; bi++) {
		y0 = MIN(y0, buf[bi].y0);
		xmom += buf[bi].xmom;
		ymom += buf[bi].ymom;
		area += buf[bi].area;
	    }
	    buf[bi0].x0 = MIN(buf[bi0].x0, new_runs[ni].x0);
	    buf[bi0].x1 = MAX(buf[bi - 1].x1, new_runs[ni].x1);
	    buf[bi0].y0 = y0;
	    buf[bi0].xmom = xmom + run_len * .5 * (new_runs[ni].x0 + new_runs[ni].x1);
	    buf[bi0].ymom = ymom + run_len * y;
	    buf[bi0].area = area + run_len;
	    if (bi > bi0 + 1) {
		memmove(&buf[bi0 + 1], &buf[bi], (bs - bi) * sizeof(seg));
		bs += bi0 + 1 - bi;
	    }
	    bi = bi0;
	    flag = 0;
	} else {
	    memmove(&buf[bi + 1], &buf[bi], (bs - bi) * sizeof(seg));
	    bs++;
	    buf[bi].x0 = new_runs[ni].x0;
	    buf[bi].x1 = new_runs[ni].x1;
	    buf[bi].y0 = y;
	    buf[bi].xmom = run_len * .5 * (new_runs[ni].x0 + new_runs[ni].x1);
	    buf[bi].ymom = run_len * y;
	    buf[bi].area = run_len;
	    bi++;
	    flag = 1;
	}
    }
    bi0 = bi;
    for (; bi < bs; bi++) {
	if (flag) {
	    buf[bi].y1 = y;
	    print_rect(&buf[bi]);
	} else {
	    bi0 = bi + 1;
	    flag = 1;
	}
    }
    buf[bi0].x0 = 0;
    buf[bi0].x1 = 0;
}

static void
die (char *why)
{
  fprintf (stderr, "%s\n", why);
  exit (1);
}

#define MAX_SIZE 65536

int
main (int argc, char **argv)
{
  FILE *fi = stdin;
  FILE *fo = stdout;
  char buf[256];
  int xs, ys;
  int depth;
  unsigned char *imgbuf;
  seg *segs;
  run *runs;
  int y;

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

  runs = (run *)malloc(((xs + 3) >> 1) * sizeof(run));
  segs = (seg *)malloc(((xs + 3) >> 1) * sizeof(seg));
  imgbuf = (unsigned char *)malloc (xs);
  segs[0].x0 = 0;
  segs[0].x1 = 0;
  for (y = 0; y < ys; y++) {
      fread (imgbuf, 1, xs, fi);
      find_runs(runs, imgbuf, 160, xs);
      merge_runs(segs, runs, y);
  }

  free(imgbuf);
  free(runs);
  free(segs);

  return 0;
}
