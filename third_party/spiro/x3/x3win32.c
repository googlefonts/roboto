#include "x3.h"
#include "x3common.h"
#include <stdio.h> /* for printf only, probably remove in production */

HINSTANCE theInstance = NULL;

void x3init_win32(HINSTANCE hInstance)
{
    theInstance = hInstance;
}

void x3widget_init(x3widget *w, const x3type *type)
{
    w->type = type;
    w->name = NULL;
    w->parent = NULL;
    w->var = x3winnone;
    w->u.hwnd = NULL;
    w->n_children = 0;
    w->children = NULL;
}

LRESULT CALLBACK x3WndProc(HWND hwnd, UINT iMsg, WPARAM wParam, LPARAM lParam)
{
    switch (iMsg) {
    case WM_DESTROY:
	if (--x3n_winopen <= 0) {
	    PostQuitMessage(0);
	    return 0;
	}
	break;
    }
    return DefWindowProc(hwnd, iMsg, wParam, lParam);
}

void x3window_sizereq(x3widget *w)
{
}

void x3window_sizealloc(x3widget *w, x3rect *r)
{
    int i;
    RECT rect;
    x3rect child_r;

    GetClientRect(w->u.hwnd, &rect);
    child_r.x0 = 0;
    child_r.x1 = rect.right - rect.left;
    child_r.y0 = 0;
    child_r.y1 = rect.bottom - rect.top;
    printf("x3window_sizealloc (%ld, %ld) - (%ld, %ld)\n",
	   rect.left, rect.top, rect.right, rect.bottom);
    for (i = 0; i < w->n_children; i++) {
	x3widget *child = w->children[i];
	if (child->type->sizealloc)
	    child->type->sizealloc(child, &child_r);
	child->flags &= ~x3flag_needsizealloc;
    }
}

x3type x3windowtype = { x3window_sizereq,
			x3window_sizealloc,
			x3add_default };

x3widget *x3window(x3windowflags flags, char *label,
		   x3window_callback callback, void *data)
{
    HWND hwnd;
    DWORD style = WS_OVERLAPPEDWINDOW;
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));
    WNDCLASSEX wndclass;

    wndclass.cbSize = sizeof(wndclass);
    wndclass.style = CS_HREDRAW | CS_VREDRAW;
    wndclass.lpfnWndProc = x3WndProc;
    wndclass.cbClsExtra = 0;
    wndclass.cbWndExtra = 0;
    wndclass.hInstance = theInstance;
    wndclass.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wndclass.hCursor = LoadCursor(NULL, IDC_ARROW);
    wndclass.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);
    wndclass.lpszMenuName = NULL;
    wndclass.lpszClassName = "x3win";
    wndclass.hIconSm = LoadIcon(NULL, IDI_APPLICATION);

    RegisterClassEx(&wndclass);

    hwnd = CreateWindowEx(0, "x3win", "My window",
			  style, 100, 100, 300, 300,
			  NULL, NULL,
			  theInstance, NULL);
    x3widget_init(result, &x3windowtype);
    result->var = x3winhwnd;
    result->u.hwnd = hwnd;
    x3_nwinopen++;
    //ShowWindow(hwnd, SW_SHOWNORMAL);
    return result;
			 
}

void x3_window_show(x3widget *w)
{
    ShowWindow(w->u.hwnd, SW_SHOW);
}

static HWND x3hwnd_of(x3widget *w)
{
    while (w->parent) w = w->parent;
    return w->var == x3winhwnd ? w->u.hwnd : NULL;
}

static x3widget *x3widget_new_hwnd(x3widget *parent, char *name,
				   const x3type *type,
				   HWND hwnd)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));
    x3widget_init(result, type);
    result->name = name ? strdup(name) : NULL;
    result->var = x3winhwnd;
    result->u.hwnd = hwnd;
    x3add(parent, result);
    x3qsizereq(result);
    return result;
}

void x3button_sizereq(x3widget *w)
{
    w->sizerequest.x0 = 0;
    w->sizerequest.y0 = 0;
    w->sizerequest.x1 = 100;
    w->sizerequest.y1 = 20;
#ifdef VERBOSE
    printf("button sizereq = (%d, %d) - (%d, %d)\n",
	   w->sizerequest.x0, w->sizerequest.y0,
	   w->sizerequest.x1, w->sizerequest.y1);
#endif
}

void x3button_sizealloc(x3widget *w, x3rect *r)
{
    printf("button sizealloc = (%g, %g) - (%g, %g)\n",
	   r->x0, r->y0, r->x1, r->y1);
    if (w->var == x3winhwnd) {
	SetWindowPos(w->u.hwnd, HWND_TOP,
		     r->x0, r->y0, r->x1 - r->x0, r->y1 - r->y0,
		     SWP_NOZORDER);
    }
}

x3type x3buttontype = { x3button_sizereq,
			x3button_sizealloc,
			x3add_default };

x3widget *x3button(x3widget *parent, char *cmd, char *label)
{
    HWND hwnd;

    hwnd = CreateWindow("button", label,
			WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
			10, 10, 100, 20, x3hwnd_of(parent), NULL,
			theInstance, NULL);
    return x3widget_new_hwnd(parent, cmd, &x3buttontype, hwnd);
}

void x3main(void)
{
    MSG msg;

    x3sync();
    while (GetMessage(&msg, NULL, 0, 0)) {
	TranslateMessage(&msg);
	DispatchMessage(&msg);
    }
}
