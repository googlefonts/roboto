/* Functions common to more than one platform. */

#include <stdlib.h>

#include "x3.h"
#include "x3common.h"

int n_x3needshow = 0;
int n_x3needshow_max = 0;
x3widget **x3needshow = NULL;

#if defined(X3_GTK) || defined(X3_WIN32)
int x3n_winopen = 0;
#endif

#if defined(X3_CARBON) || defined(X3_WIN32)

int n_x3needsizereqs = 0;
int n_x3needsizereqs_max = 0;
x3widget **x3needsizereqs = NULL;

int n_x3needsizeallocs = 0;
int n_x3needsizeallocs_max = 0;
x3widget **x3needsizeallocs = NULL;

void x3qsizereq(x3widget *w)
{
    if (w && !(w->flags & x3flag_needsizereq)) {
	x3qsizereq(w->parent);
	if (n_x3needsizereqs == n_x3needsizereqs_max)
	    x3needsizereqs = (x3widget **)realloc(x3needsizereqs,
						  sizeof(x3widget *) *
						  (n_x3needsizereqs_max <<= 1));
	x3needsizereqs[n_x3needsizereqs++] = w;
	w->flags |= x3flag_needsizereq;
    }
}

void x3add_default(x3widget *parent, x3widget *child)
{
    const int n_children_init = 4;

    child->parent = parent;
    if (parent->n_children == 0)
	parent->children = (x3widget **)malloc(sizeof(x3widget *) *
					       n_children_init);
    else if (parent->n_children >= n_children_init &&
	     !(parent->n_children & (parent->n_children - 1)))
	parent->children = (x3widget **)realloc(parent->children,
						sizeof(x3widget *) *
						(parent->n_children << 1));
    parent->children[parent->n_children++] = child;
}

void x3add(x3widget *parent, x3widget *child)
{
    parent->type->add(parent, child);
}

/* Widgets common to carbon and win32 platforms */

typedef struct {
    x3widget base;
    int homogeneous;
    int spacing;
    int cur_child_prop;
    int *child_props; /* bit 0=expand, bit 1=fill, bits 2:31=padding */
} x3widget_box;

void x3vbox_sizereq(x3widget *w)
{
    x3widget_box *wb = (x3widget_box *)w;
    int i;
    int spacing = wb->spacing;

    w->sizerequest.x0 = 0;
    w->sizerequest.y0 = 0;
    w->sizerequest.x1 = 0;
    w->sizerequest.y1 = 0;
    for (i = 0; i < w->n_children; i++) {
	x3widget *child = w->children[i];
	int childw = child->sizerequest.x1 - child->sizerequest.x0;
	int childh = child->sizerequest.y1 - child->sizerequest.y0;
	int padding = wb->child_props[i] >> 2;

	if (i < w->n_children - 1)
	    childh += spacing;
	w->sizerequest.y1 += childh + 2 * padding;
	if (childw > w->sizerequest.x1)
	    w->sizerequest.x1 = childw;
    }
}

void x3vbox_sizealloc(x3widget *w, x3rect *r)
{
    x3widget_box *wb = (x3widget_box *)w;
    int i;
    x3rect child_r = *r;
    int spacing = wb->spacing;
    int n_extend = 0;
    int n_stretch, i_stretch = 0;
    int extra;

    /* todo: impl padding & homog, factor hbox/vbox common */
    printf("vbox sizealloc = (%g, %g) - (%g, %g), req was %g x %g\n",
	   r->x0, r->y0, r->x1, r->y1,
	   w->sizerequest.x1, w->sizerequest.y1);
    extra = r->y1 - r->y0 - w->sizerequest.y1;
    for (i = 0; i < w->n_children; i++)
	if (wb->child_props[i] & 1)
	    n_extend++;
    n_stretch = n_extend ? n_extend : w->n_children;
    printf("extra = %d, n_stretch = %d\n", extra, n_stretch);
    for (i = 0; i < w->n_children; i++) {
	x3widget *child = w->children[i];
	int childh = child->sizerequest.y1 - child->sizerequest.y0;
	int my_extra;
	int next_top;

	if (n_extend == 0 || (wb->child_props[i] & 1)) {
	    my_extra = (extra * (i_stretch + 1)) / n_stretch -
		(extra * i_stretch) / n_stretch;
	    i_stretch++;
	} else
	    my_extra = 0;
	next_top = child_r.y0 + childh + spacing + my_extra;

	if (wb->child_props[i] & 2) {
	    childh += my_extra;
	} else {
	    child_r.y0 += my_extra >> 1;
	}
	child_r.y1 = child_r.y0 + childh;

	child->type->sizealloc(child, &child_r);
	child->flags &= ~x3flag_needsizealloc;

	child_r.y0 = next_top;
    }
}

void x3vbox_add(x3widget *w, x3widget *child)
{
    x3widget_box *wb = (x3widget_box *)w;
    const int n_children_init = 4;

    if (w->n_children == 0)
	wb->child_props = (int *)malloc(sizeof(int) * n_children_init);
    else if (w->n_children >= n_children_init &&
	     !(w->n_children & (w->n_children - 1)))
	wb->child_props = (int *)realloc(wb->child_props,
					 sizeof(int) * (w->n_children << 1));
    wb->child_props[w->n_children] = wb->cur_child_prop;
    x3add_default(w, child);
}

x3type x3vboxtype = { x3vbox_sizereq,
		      x3vbox_sizealloc,
		      x3vbox_add };

x3widget *x3vbox(x3widget *parent, int homogeneous, int spacing)
{
    x3widget_box *result = (x3widget_box *)malloc(sizeof(x3widget_box));
    x3widget_init(&result->base, &x3vboxtype);
    x3add(parent, &result->base);
    result->homogeneous = homogeneous;
    result->spacing = spacing;
    result->cur_child_prop = 3;
    x3qsizereq(&result->base);
    return &result->base;
}

void x3setpacking(x3widget *w, int fill, int expand, int padding)
{
    if (w->type == &x3vboxtype) {
	x3widget_box *wb = (x3widget_box *)w;
	int child_props = padding << 2;

	if (fill) child_props |= 1;
	if (expand) child_props |= 2;
	wb->cur_child_prop = child_props;
    }
}

typedef struct {
    x3widget base;
    x3alignment alignment;
} x3widget_align;

void x3align_sizereq(x3widget *w)
{
    w->sizerequest.x0 = 0;
    w->sizerequest.y0 = 0;
    w->sizerequest.x1 = 0;
    w->sizerequest.y1 = 0;
    if (w->n_children) {
	x3widget *child = w->children[0];
	int childw = child->sizerequest.x1 - child->sizerequest.x0;
	int childh = child->sizerequest.y1 - child->sizerequest.y0;
	w->sizerequest.x1 = childw;
	w->sizerequest.y1 = childh;
    }
}

void x3align_sizealloc(x3widget *w, x3rect *r)
{
    x3widget_align *z = (x3widget_align *)w;
    x3alignment a = z->alignment;
    int xa = a & 3;
    int ya = (a >> 2) & 3;
    x3rect child_r = *r;

    printf("align sizealloc = (%g, %g) - (%g, %g)\n",
	   r->x0, r->y0, r->x1, r->y1);
    if (w->n_children) {
	x3widget *child = w->children[0];
	if (xa < 3) {
	    int childw = child->sizerequest.x1 - child->sizerequest.x0;
	    int pad = r->x1 - r->x0 - childw;
	    child_r.x0 += (pad * (1 + (xa >> 1) - (xa & 1)) + 1) >> 1;
	    child_r.x1 = child_r.x0 + childw;
	}
	if (ya < 3) {
	    int childh = child->sizerequest.y1 - child->sizerequest.y0;
	    int pad = r->y1 - r->y0 - childh;
	    child_r.y0 += (pad * (1 + (ya >> 1) - (ya & 1)) + 1) >> 1;
	    child_r.y1 = child_r.y0 + childh;
	}

	child->type->sizealloc(child, &child_r);
	child->flags &= ~x3flag_needsizealloc;
    }
}

x3type x3aligntype = { x3align_sizereq,
		       x3align_sizealloc,
		       x3add_default };

x3widget *x3align(x3widget *parent, x3alignment alignment)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget_align));
    x3widget_init(result, &x3aligntype);
    x3add(parent, result);
    x3qsizereq(result);
    ((x3widget_align *)result)->alignment = alignment;
    return result;
}

typedef struct {
    x3widget base;
    int t, b, l, r;
} x3widget_pad;

void x3pad_sizereq(x3widget *w)
{
    x3widget_pad *z = (x3widget_pad *)w;
    w->sizerequest.x0 = 0;
    w->sizerequest.y0 = 0;
    w->sizerequest.x1 = 0;
    w->sizerequest.y1 = 0;
    if (w->n_children) {
	x3widget *child = w->children[0];
	int childw = child->sizerequest.x1 - child->sizerequest.x0;
	int childh = child->sizerequest.y1 - child->sizerequest.y0;
	w->sizerequest.x1 = childw + z->l + z->r;
	w->sizerequest.y1 = childh + z->t + z->b;
    }
}

void x3pad_sizealloc(x3widget *w, x3rect *r)
{
    x3widget_pad *z = (x3widget_pad *)w;
    x3rect child_r = *r;

    printf("pad sizealloc = (%g, %g) - (%g, %g)\n",
	   r->x0, r->y0, r->x1, r->y1);
    if (w->n_children) {
	x3widget *child = w->children[0];
	child_r.x0 += z->l;
	child_r.x1 -= z->r;
	child_r.y0 += z->t;
	child_r.y1 -= z->b;

	child->type->sizealloc(child, &child_r);
	child->flags &= ~x3flag_needsizealloc;
    }
}

x3type x3padtype = { x3pad_sizereq,
		     x3pad_sizealloc,
		     x3add_default };

x3widget *x3pad(x3widget *parent, int t, int b, int l, int r)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget_pad));
    x3widget_init(result, &x3padtype);
    x3add(parent, result);
    x3qsizereq(result);
    ((x3widget_pad *)result)->t = t;
    ((x3widget_pad *)result)->b = b;
    ((x3widget_pad *)result)->l = l;
    ((x3widget_pad *)result)->r = r;
    return result;
}

#endif

void x3initqs(void)
{
    n_x3needshow = 0;
    x3needshow = (x3widget **)malloc(sizeof(x3widget *) *
				     (n_x3needshow_max = 16));

#if defined(X3_CARBON) || defined(X3_WIN32)
    n_x3needsizereqs = 0;
    x3needsizereqs = (x3widget **)malloc(sizeof(x3widget *) *
					 (n_x3needsizereqs_max = 16));

    n_x3needsizeallocs = 0;
    x3needsizeallocs = (x3widget **)malloc(sizeof(x3widget *) *
					   (n_x3needsizeallocs_max = 16));
#endif
}

void x3qshow(x3widget *w)
{
    if (n_x3needshow == n_x3needshow_max)
	x3needshow = (x3widget **)realloc(x3needshow,
					  sizeof(x3widget *) *
					  (n_x3needshow_max <<= 1));
    x3needshow[n_x3needshow++] = w;
}

void x3sync(void)
{
    int i;

#if defined(X3_CARBON) || defined(X3_WIN32)

    for (i = n_x3needsizereqs - 1; i >= 0; i--) {
	x3widget *w = x3needsizereqs[i];
	w->type->sizereq(w);
	w->flags &= ~x3flag_needsizereq;
	w->flags |= x3flag_needsizealloc;
    }
    for (i = 0; i < n_x3needsizereqs; i++) {
	x3widget *w = x3needsizereqs[i];
	if (w->flags & x3flag_needsizealloc) {
	    w->type->sizealloc(w, NULL);
	    w->flags &= ~x3flag_needsizealloc;
	}
    }
    n_x3needsizereqs = 0;
#endif

    for (i = 0; i < n_x3needshow; i++)
	x3_window_show(x3needshow[i]);
    n_x3needshow = 0;
}
