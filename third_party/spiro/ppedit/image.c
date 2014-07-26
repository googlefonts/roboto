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
#include <stdio.h>
#include <string.h>
#include "zmisc.h"
#include "image.h"

/* An image loaded into memory. */
struct _image {
    unsigned char *buf;
    int width;
    int height;
    int rowstride;
};

static image *
load_ppm_file(FILE *f, char **reason)
{
    image *result;
    char line[256];
    int xs, ys;
    int depth;
    int n;

    fseek(f, 0, SEEK_SET);
    fgets(line, sizeof(line), f);
    do {
	fgets(line, sizeof(line), f);
    } while (line[0] == '#');
    n = sscanf(line, "%d %d", &xs, &ys);
    if (n != 2) {
	*reason = "Error reading ppmraw size line";
	fclose(f);
	return NULL;
    }
    do {
	fgets(line, sizeof(line), f);
    } while (line[0] == '#');
    n = sscanf(line, "%d", &depth);
    if (n != 1) {
	*reason = "Error reading ppmraw depth line";
	fclose(f);
	return NULL;
    }
    result = znew(image, 1);
    result->rowstride = 3 * xs;
    result->buf = zalloc(ys * result->rowstride);
    result->width = xs;
    result->height = ys;
    fread(result->buf, 1, ys * result->rowstride, f);
    fclose(f);
    return result;
}

image *
load_image_file(const char *fn, char **reason)
{
    FILE *f = fopen(fn, "rb");
    unsigned char buf[256];
    int n;

    if (f == NULL) {
	*reason = "Error opening file";
	return NULL;
    }
    n = fread(buf, 1, sizeof(buf), f);
    if (n < 4) {
	*reason = "Short file";
	fclose(f);
	return NULL;
    }
    if (buf[0] != 'P' || buf[1] != '6') {
	*reason = "Unrecognized magic";
	fclose(f);
	return NULL;
    }
    return load_ppm_file(f, reason);
}

void
free_image(image *im)
{
    zfree(im->buf);
    zfree(im);
}

void
render_image(image *im, const double affine[6],
	     unsigned char *buf, int rowstride, int x0, int y0, int x1, int y1)
{
    int y;
    unsigned char *dest_line = buf;
    int src_x0 = x0;

    for (y = y0; y < y1; y++) {
	int src_y = y;

	if (src_y >= 0 && src_y < im->height) {
	    unsigned char *img_line = im->buf + src_y * im->rowstride;
	    int left_pad = -src_x0;
	    int img_run, img_off, right_pad;

	    if (left_pad > x1 - x0) left_pad = x1 - x0;
	    if (left_pad > 0) {
		memset(dest_line, 255, 3 * left_pad);
	    } else left_pad = 0;
	    img_off = src_x0;
	    if (img_off < 0) img_off = 0;
	    img_run = x1 - x0 - left_pad;
	    if (img_run > im->width - img_off) img_run = im->width - img_off;
	    if (img_run > 0) {
		memcpy(dest_line + 3 * left_pad, img_line + 3 * img_off, 3 * img_run);
	    } else img_run = 0;
	    right_pad = x1 - x0 - left_pad - img_run;
	    if (right_pad > 0) {
		memset(dest_line + 3 * (left_pad + img_run), 255, 3 * right_pad);
	    }
	} else {
	    memset(dest_line, 255, rowstride);
	}
	dest_line += rowstride;
    }
}
