typedef struct _image image;

image *
load_image_file(const char *fn, char **reason);

void
free_image(image *im);

void
render_image(image *im, const double affine[6],
	     unsigned char *buf, int rowstride, int x0, int y0, int x1, int y1);
