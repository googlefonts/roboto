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
/* This module implements a Carbon HIView object for a pattern plate
   editor. */

#include <Carbon/Carbon.h>

#include "bezctx.h"
#include "bezctx_quartz.h"
#include "plate.h"
#include "pe_view.h"

#define kPEViewClassID CFSTR("com.levien.ppedit.PEView")
#define kPEViewPrivate 'PE_v'

typedef struct
{
    HIViewRef view;
    int show_knots;
    plate *p;
} pe_view_data;

static OSStatus
pe_view_construct(EventRef inEvent)
{
    OSStatus err;
    pe_view_data *data;

    data = (pe_view_data *)malloc(sizeof(pe_view_data));
    require_action(data != NULL, CantMalloc, err = memFullErr);
    err = GetEventParameter(inEvent, kEventParamHIObjectInstance,
			    typeHIObjectRef, NULL, sizeof(HIObjectRef), NULL,
			    (HIObjectRef *)&data->view);
    require_noerr(err, ParameterMissing);
    err = SetEventParameter(inEvent, kEventParamHIObjectInstance,
			    typeVoidPtr, sizeof(pe_view_data *), &data);

    data->p = NULL;
    data->show_knots = 1;

 ParameterMissing:
    if (err != noErr)
	free(data);

 CantMalloc:
    return err;
}

static OSStatus
pe_view_destruct(EventRef inEvent, pe_view_data *inData)
{
    free(inData);
    return noErr;
}

static OSStatus
pe_view_initialize(EventHandlerCallRef inCallRef, EventRef inEvent,
		   pe_view_data *inData)
{
    OSStatus err;
    HIRect bounds;

    err = CallNextEventHandler(inCallRef, inEvent);
    require_noerr(err, TroubleInSuperClass);

    err = GetEventParameter(inEvent, 'Boun', typeHIRect,
			    NULL, sizeof(HIRect), NULL, &bounds);
    require_noerr(err, ParameterMissing);

    HIViewSetFrame(inData->view, &bounds);

 ParameterMissing:
 TroubleInSuperClass:
    return err;
}

#ifndef M_PI
#define M_PI            3.14159265358979323846  /* pi */
#endif

static void
cgcontext_set_rgba(CGContextRef ctx, unsigned int rgba)
{
    const double norm = 1.0 / 255;
    CGContextSetRGBFillColor(ctx,
			     ((rgba >> 24) & 0xff) * norm,
			     ((rgba >> 16) & 0xff) * norm,
			     ((rgba >> 8) & 0xff) * norm,
			     (rgba & 0xff) * norm);
}

static void
draw_dot(CGContextRef ctx, double x, double y, double r,
	 unsigned int rgba)
{
    cgcontext_set_rgba(ctx, rgba);
    CGMutablePathRef path = CGPathCreateMutable();
    CGPathAddArc(path, NULL, x, y, r, 0, 2 * M_PI, false);
    CGContextAddPath(ctx, path);
    CGPathRelease(path);
    CGContextFillPath(ctx);
}

static void
draw_raw_rect(CGContextRef ctx, double x0, double y0, double x1, double y1,
	      unsigned int rgba)
{
    HIRect rect;

    cgcontext_set_rgba(ctx, rgba);
    rect.origin.x = x0;
    rect.origin.y = y0;
    rect.size.width = x1 - x0;
    rect.size.height = y1 - y0;
    CGContextFillRect(ctx, rect);
}

static void
draw_rect(CGContextRef ctx, double x, double y, double r,
	 unsigned int rgba)
{
    draw_raw_rect(ctx, x - r, y - r, x + r, y + r, rgba);
}

static void
draw_plate(CGContextRef ctx, pe_view_data *pe)
{
    plate *p = pe->p;
    int i, j;
    bezctx *bc;
    subpath *sp;
    spiro_seg **ss = znew(spiro_seg *, p->n_sp);

    for (i = 0; i < p->n_sp; i++) {
	bc = new_bezctx_quartz();
	ss[i] = draw_subpath(&p->sp[i], bc);
	CGMutablePathRef path = bezctx_to_quartz(bc);
	CGContextAddPath(ctx, path);
	CGPathRelease(path);
	CGContextStrokePath(ctx);
    }

    for (i = 0; i < p->n_sp; i++) {
	if (pe->show_knots) {
	    sp = &p->sp[i];
	    for (j = 0; j < sp->n_kt; j++) {
		knot *kt = &sp->kt[j];
		kt_flags kf = kt->flags;
		if ((kf & KT_SELECTED) && (kf & KT_OPEN)) {
		    draw_dot(ctx, kt->x, kt->y,
			     3, 0x000000ff);
		    draw_dot(ctx, kt->x, kt->y,
			     1.5, 0xffffffff);
		} else if ((kf & KT_SELECTED) && (kf & KT_CORNER)) {
		    draw_rect(ctx, kt->x, kt->y,
			      3, 0x000000ff);
		    draw_rect(ctx, kt->x, kt->y,
			      1.5, 0xffffffff);
		} else if (!(kf & KT_SELECTED) && (kf & KT_CORNER)) {
		    draw_rect(ctx, kt->x, kt->y,
			      2.5, 0x000080ff);
		} else {
		    draw_dot(ctx, kt->x, kt->y,
			     2, 0x000080ff);
		}
	    }
	}
	spiro_free(ss[i]);
    }
    zfree(ss);
}

static void
draw_selection(CGContextRef ctx, pe_view_data *pe)
{
    plate *p = pe->p;

    if (p->motmode == MOTION_MODE_SELECT) {
	double rx0 = p->sel_x0;
	double ry0 = p->sel_y0;
	double rx1 = p->x0;
	double ry1 = p->y0;
	if (rx0 > rx1) {
	    double tmp = rx1;
	    rx1 = rx0;
	    rx0 = tmp;
	}
	if (ry0 > ry1) {
	    double tmp = ry1;
	    ry1 = ry0;
	    ry0 = tmp;
	}
	if (rx1 > rx0 && ry1 > ry0)
	    draw_raw_rect(ctx, rx0, ry0, rx1, ry1, 0x0000ff20);
    }
}

static OSStatus
pe_view_draw(EventRef inEvent, pe_view_data *inData)
{
    OSStatus err;
    CGContextRef ctx;

    err = GetEventParameter(inEvent, kEventParamCGContextRef, typeCGContextRef,
			    NULL, sizeof(CGContextRef), NULL, &ctx);
    require_noerr(err, ParameterMissing);

    if (inData->p) {
	draw_plate(ctx, inData);
	draw_selection(ctx, inData);
    }

 ParameterMissing:
    return err;
}

static OSStatus
pe_view_get_data(EventRef inEvent, pe_view_data *inData)
{
    OSStatus err;
    OSType tag;
    Ptr ptr;
    Size outSize;

    /* Probably could use a bit more error checking here, for type
       and size match. Also, just returning a pe_view_data seems a
       little hacky. */
    err = GetEventParameter(inEvent, kEventParamControlDataTag, typeEnumeration,
			    NULL, sizeof(OSType), NULL, &tag);
    require_noerr(err, ParameterMissing);

    err = GetEventParameter(inEvent, kEventParamControlDataBuffer, typePtr,
			    NULL, sizeof(Ptr), NULL, &ptr);

    if (tag == kPEViewPrivate) {
	*((pe_view_data **)ptr) = inData;
	outSize = sizeof(pe_view_data *);
    } else
	err = errDataNotSupported;

    if (err == noErr)
	err = SetEventParameter(inEvent, kEventParamControlDataBufferSize, typeLongInteger,
				sizeof(Size), &outSize);

 ParameterMissing:
    return err;
}

static OSStatus
pe_view_set_data(EventRef inEvent, pe_view_data *inData)
{
    OSStatus err;
    Ptr ptr;
    OSType tag;

    err = GetEventParameter(inEvent, kEventParamControlDataTag, typeEnumeration,
			    NULL, sizeof(OSType), NULL, &tag);
    require_noerr(err, ParameterMissing);

    err = GetEventParameter(inEvent, kEventParamControlDataBuffer, typePtr,
			    NULL, sizeof(Ptr), NULL, &ptr);
    require_noerr(err, ParameterMissing);

    if (tag == 'Plat') {
	inData->p = *(plate **)ptr;
    } else
	err = errDataNotSupported;

 ParameterMissing:
    return err;
}

static OSStatus
pe_view_hittest(EventRef inEvent, pe_view_data *inData)
{
    OSStatus err;
    HIPoint where;
    HIRect bounds;
    ControlPartCode part;

    err = GetEventParameter(inEvent, kEventParamMouseLocation, typeHIPoint,
			    NULL, sizeof(HIPoint), NULL, &where);
    require_noerr(err, ParameterMissing);

    err = HIViewGetBounds(inData->view, &bounds);
    require_noerr(err, ParameterMissing);

    if (CGRectContainsPoint(bounds, where))
	part = 1;
    else
	part = kControlNoPart;
    err = SetEventParameter(inEvent, kEventParamControlPart,
			    typeControlPartCode, sizeof(ControlPartCode),
			    &part);
    printf("hittest %g, %g!\n", where.x, where.y);

 ParameterMissing:
    return err;
}

static void
pe_view_queue_draw(pe_view_data *pe)
{
    HIViewSetNeedsDisplay(pe->view, true);
}

static int
pe_view_button_press(pe_view_data *pe, double x, double y, press_mod mods)
{
    pe->p->description = NULL;
    plate_press(pe->p, x, y, mods);
    pe_view_queue_draw(pe);
    return 1;
}

static int
pe_view_motion(pe_view_data *pe, double x, double y)
{
    if (pe->p->motmode == MOTION_MODE_MOVE)
	plate_motion_move(pe->p, x, y);
    else if (pe->p->motmode == MOTION_MODE_SELECT)
	plate_motion_select(pe->p, x, y);
    pe_view_queue_draw(pe);
    return 1;
}

static int
pe_view_button_release(pe_view_data *pe)
{
    int need_redraw;
    
    need_redraw = (pe->p->motmode == MOTION_MODE_SELECT);

    plate_unpress(pe->p);

    if (need_redraw)
	pe_view_queue_draw(pe);
    return 1;
}

static OSStatus
pe_view_track(EventRef inEvent, pe_view_data *inData)
{
    OSStatus err;
    HIPoint where;
    MouseTrackingResult mouseStatus;
    HIRect bounds;
    Rect windBounds;
    Point theQDPoint;

    err = GetEventParameter(inEvent, kEventParamMouseLocation, typeHIPoint,
			    NULL, sizeof(HIPoint), NULL, &where);
    require_noerr(err, ParameterMissing);

    err = HIViewGetBounds(inData->view, &bounds);
    require_noerr(err, ParameterMissing);

    GetWindowBounds(GetControlOwner(inData->view), kWindowStructureRgn, &windBounds);

#ifdef VERBOSE
    printf("press: %g, %g!\n", where.x, where.y);
#endif
    pe_view_button_press(inData, where.x, where.y, 0);

    mouseStatus = kMouseTrackingMouseDown;
    while (mouseStatus != kMouseTrackingMouseUp) {
	TrackMouseLocation(NULL, &theQDPoint, &mouseStatus);
	where.x = theQDPoint.h - windBounds.left;
	where.y = theQDPoint.v - windBounds.top;
	HIViewConvertPoint(&where, NULL, inData->view);
#ifdef VERBOSE
	printf("track %d: %g, %g!\n", mouseStatus, where.x, where.y);
#endif
	if (mouseStatus == kMouseTrackingMouseUp) {
	    pe_view_button_release(inData);
	} else {
	    pe_view_motion(inData, where.x, where.y);
	}
    }

 ParameterMissing:
    return err;
}

pascal OSStatus
pe_view_handler(EventHandlerCallRef inCallRef,
		EventRef inEvent,
		void* inUserData )
{
    OSStatus err = eventNotHandledErr;
    UInt32 eventClass = GetEventClass(inEvent);
    UInt32 eventKind = GetEventKind(inEvent);
    pe_view_data *data = (pe_view_data *)inUserData;

    switch (eventClass) {
    case kEventClassHIObject:
	switch (eventKind) {
	case kEventHIObjectConstruct:
	    err = pe_view_construct(inEvent);
	    break;
	case kEventHIObjectInitialize:
	    err = pe_view_initialize(inCallRef, inEvent, data);
	    break;
	case kEventHIObjectDestruct:
	    err = pe_view_destruct(inEvent, data);
	    break;
	}
	break;
    case kEventClassControl:
	switch (eventKind) {
	case kEventControlInitialize:
	    err = noErr;
	    break;
	case kEventControlDraw:
	    err = pe_view_draw(inEvent, data);
	    break;
	case kEventControlGetData:
	    err = pe_view_get_data(inEvent, data);
	    break;
	case kEventControlSetData:
	    err = pe_view_set_data(inEvent, data);
	    break;
	case kEventControlTrack:
	    err = pe_view_track(inEvent, data);
	    break;
	case kEventControlHitTest:
	    err = pe_view_hittest(inEvent, data);
	    break;
	    /*...*/
	}
	break;
    }
    return err;
}

static OSStatus
pe_view_register(void)
{
    OSStatus err = noErr;
    static HIObjectClassRef pe_view_ClassRef = NULL;

    if (pe_view_ClassRef == NULL) {
	EventTypeSpec eventList[] = {
	    { kEventClassHIObject, kEventHIObjectConstruct },
	    { kEventClassHIObject, kEventHIObjectInitialize },
	    { kEventClassHIObject, kEventHIObjectDestruct },

	    { kEventClassControl, kEventControlActivate },
	    { kEventClassControl, kEventControlDeactivate },
	    { kEventClassControl, kEventControlDraw },
	    { kEventClassControl, kEventControlHiliteChanged },
	    { kEventClassControl, kEventControlHitTest },
	    { kEventClassControl, kEventControlInitialize },
	    { kEventClassControl, kEventControlGetData },
	    { kEventClassControl, kEventControlSetData },
	    { kEventClassControl, kEventControlTrack }
	};
	err = HIObjectRegisterSubclass(kPEViewClassID,
				       kHIViewClassID,
				       NULL,
				       pe_view_handler,
				       GetEventTypeCount(eventList),
				       eventList,
				       NULL,
				       &pe_view_ClassRef);
    }
    return err;
}

OSStatus pe_view_create(
	WindowRef			inWindow,
	const HIRect*		inBounds,
	HIViewRef*			outView)
{
    OSStatus err;
    EventRef event;

    err = pe_view_register();
    require_noerr(err, CantRegister);

    err = CreateEvent(NULL, kEventClassHIObject, kEventHIObjectInitialize,
		      GetCurrentEventTime(), 0, &event);
    require_noerr(err, CantCreateEvent);

    if (inBounds != NULL) {
	err = SetEventParameter(event, 'Boun', typeHIRect, sizeof(HIRect),
				inBounds);
	require_noerr(err, CantSetParameter);
    }

    err = HIObjectCreate(kPEViewClassID, event, (HIObjectRef*)outView);
    require_noerr(err, CantCreate);

    if (inWindow != NULL) {
	HIViewRef root;
	err = GetRootControl(inWindow, &root);
	require_noerr(err, CantGetRootView);
	err = HIViewAddSubview(root, *outView);
    }
 CantCreate:
 CantGetRootView:
 CantSetParameter:
 CantCreateEvent:
    ReleaseEvent(event);
 CantRegister:
    return err;
}

void
pe_view_set_plate(HIViewRef view, plate *p)
{
    OSStatus err;

    err = SetControlData(view, 1, 'Plat', 4, &p);
}

void
pe_view_toggle_corner(HIViewRef view)
{
    OSStatus err;
    pe_view_data *pe;

    err = GetControlData(view, 1, kPEViewPrivate, 4, &pe, NULL);
    require_noerr(err, CantGetPrivate);

    plate_toggle_corner(pe->p);
    pe_view_queue_draw(pe);

 CantGetPrivate:
}
