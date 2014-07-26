#include "x3.h"
#include "x3common.h"

/* Globals for managing sync */

#define VERBOSE

#define kX3ViewClassID CFSTR("com.levien.x3.X3View")
#define kX3ViewPrivate 'X3_v'

/* Some utility-type functions. */

UInt32 x3mkmultichar(const char *s)
{
    int len = strlen(s);
    int i;
    UInt32 result = 0;

    for (i = 0; i < (len > 4 ? 4 : len); i++)
	result = (result << 8) + (unsigned char)s[i];
    for (; i < 4; i++)
	result = (result << 8) + ' ';
    return result;
}

char *x3multicharstr(UInt32 mc, char buf[5])
{
    int i, len;

    for (i = 0; i < 4; i++)
	if (((mc >> (8 * i)) & 0xff) != ' ') break;
    len = 4 - i;
    for (i = 0; i < len; i++)
	buf[i] = (mc >> (24 - 8 * i)) & 0xff;
    buf[len] = 0;
    return buf;
}

void x3widget_init(x3widget *w, const x3type *type)
{
    w->type = type;
    w->name = NULL;
    w->parent = NULL;
    w->var = x3carbonnone;
    w->u.window = NULL;
    w->n_children = 0;
    w->children = NULL;
}

static x3widget *x3widget_new_container(x3widget *parent, char *name,
					const x3type *type)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));
    x3widget_init(result, type);
    result->name = name ? strdup(name) : NULL;
    x3add(parent, result);
    x3qsizereq(result);
    return result;
}

static x3widget *x3widget_new_hiview(x3widget *parent, char *name,
				     const x3type *type,
				     HIViewRef hiview)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));
    x3widget_init(result, type);
    result->name = name ? strdup(name) : NULL;
    result->var = x3carbonhiview;
    result->u.hiview = hiview;
    x3add(parent, result);
    x3qsizereq(result);
    return result;
}

static x3widget *x3widget_new_menu(x3widget *parent,
				     const x3type *type,
				     MenuRef menu)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));
    x3widget_init(result, type);
    result->var = x3carbonmenu;
    result->u.menu = menu;
    x3add(parent, result);
    return result;
}

static x3widget *x3widget_new_menuitem(x3widget *parent,
					const x3type *type, int index)
{
    x3widget *result = (x3widget *)malloc(sizeof(x3widget));
    x3widget_init(result, type);
    x3add(parent, result);
    result->var = x3carbonmenuitem;
    result->u.menuitem = index;
    return result;
}

void x3init(int *pargc, char ***pargv)
{
    ProcessSerialNumber psn;

    /* Most apps get this done from loading the menu bar from the NIB.
       Prior to 10.3, there was an undocumented call. This one is official
       for 10.3 and later. */
    GetCurrentProcess(&psn);
    TransformProcessType(&psn, kProcessTransformToForegroundApplication);
    SetFrontProcess(&psn);

    x3initqs();
}

void x3main(void)
{
    x3sync();
    RunApplicationEventLoop();
}

void x3_window_show(x3widget *mainwin)
{
    ControlRef root;
#if 0
    TransitionWindow(mainwin->u.window, kWindowZoomTransitionEffect,
		     kWindowShowTransitionAction, NULL);
#endif

#if 0
    CreateRootControl(mainwin->u.window, &root);
#endif
    //RepositionWindow(mainwin->u.window, NULL, kWindowCascadeOnMainScreen);
    ShowWindow(mainwin->u.window);
    SelectWindow(mainwin->u.window);
}

static WindowRef x3window_of(x3widget *w)
{
    while (w->parent) w = w->parent;
    return w->var == x3carbonwindow ? w->u.window : NULL;
}

typedef struct {
    x3widget base;
    x3window_callback callback;
    void *callback_data;
} x3widget_window;

pascal OSStatus x3carbonWindowEventHandler(EventHandlerCallRef cr,
					   EventRef inEvent, void *data)
{
    x3widget_window *z = (x3widget_window *)data;
    OSStatus result = noErr;
    UInt32 eclass = GetEventClass(inEvent);
    UInt32 ekind = GetEventKind(inEvent);
    char multicharbuf[5];

    if (eclass == kEventClassCommand && ekind == kEventCommandProcess) {
	HICommand command;
	int status;

	GetEventParameter(inEvent, kEventParamDirectObject, typeHICommand,
			  NULL, sizeof(HICommand), NULL, &command);
	status = z->callback(&z->base, z->callback_data,
			     x3multicharstr(command.commandID, multicharbuf),
			     "command", NULL, NULL);
	if (status == 1)
	    result = eventNotHandledErr;
    } else if (eclass = kEventClassWindow && ekind == kEventWindowBoundsChanged) {
	/* todo: only queue size request when size changes, not just pos */
	x3qsizereq(&z->base);
	x3sync();
    } else {
	printf("My handler is getting called %s %d!\n",
	       x3multicharstr(eclass, multicharbuf),
	       GetEventKind(inEvent));
    }
    result = eventNotHandledErr;
    return result;
}

void x3window_sizereq(x3widget *w)
{
}

void x3window_sizealloc(x3widget *w, x3rect *r)
{
    int i;
    Rect bounds;
    x3rect child_r;

    GetWindowBounds(w->u.window, kWindowContentRgn, &bounds);
    child_r.x0 = 0;
    child_r.x1 = bounds.right - bounds.left;
    child_r.y0 = 0;
    child_r.y1 = bounds.bottom - bounds.top;
    printf("x3window_sizealloc (%d, %d) - (%d, %d)\n",
	   bounds.left, bounds.top, bounds.right, bounds.bottom);
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
    WindowRef window;
    Rect bounds = { 100, 100, 400, 600 };
    EventHandlerRef handlerRef;
    WindowAttributes attrs =
	kWindowCompositingAttribute |
	kWindowLiveResizeAttribute |
	kWindowInWindowMenuAttribute |
	kWindowFrameworkScaledAttribute |
	kWindowStandardHandlerAttribute;
    EventTypeSpec windowEvents[] = {
		{ kEventClassCommand,	kEventCommandProcess }, 
		//{ kEventClassCommand,	kEventCommandUpdateStatus }, 

		//{ kEventClassMouse,	kEventMouseDown },

		//{ kEventClassWindow,	kEventWindowClose }, 
		//{ kEventClassWindow,	kEventWindowGetIdealSize },
		{ kEventClassWindow,	kEventWindowBoundsChanged }, 
		//{ kEventClassWindow,	kEventWindowGetClickActivation }, 
		//{ kEventClassWindow,	kEventWindowContextualMenuSelect } 
	};
    CFStringRef cflabel = CFStringCreateWithCString(NULL, label,
						    kCFStringEncodingUTF8);
    x3widget *result = (x3widget *)malloc(sizeof(x3widget_window));

    if (flags & x3window_main)
	attrs |= kWindowStandardDocumentAttributes;

    OSStatus err = CreateNewWindow(kDocumentWindowClass, attrs,
				   &bounds, &window);

    SetWindowTitleWithCFString(window, cflabel);
    CFRelease(cflabel);
    x3widget_init(result, &x3windowtype);
    result->var = x3carbonwindow;
    result->u.window = window;
    ((x3widget_window *)result)->callback = callback;
    ((x3widget_window *)result)->callback_data = data;

    InstallWindowEventHandler(window, NewEventHandlerUPP(x3carbonWindowEventHandler),
			      sizeof(windowEvents)/sizeof(EventTypeSpec),
			      windowEvents, result, &handlerRef);

    x3qshow(result);
    return result;
}

x3type x3menutype = { NULL, NULL, x3add_default };

x3widget *x3menu(x3widget *parent, char *name)
{
    static int id = 1; /* Note: menu id should probably be kept per-window */
    MenuRef menu;
    CFStringRef cflabel = CFStringCreateWithCString(NULL, name,
						    kCFStringEncodingUTF8);

    CreateNewMenu(id++, 0, &menu);
    SetMenuTitleWithCFString(menu, cflabel);
    CFRelease(cflabel);
    InsertMenu(menu, 0);
    return x3widget_new_menu(parent, &x3menutype, menu);
}

int x3parseshortcut(const char *shortcut, UInt16 *pkey, UInt8 *pmods)
{
    UInt16 key;
    UInt8 mods = kMenuNoCommandModifier;
    int i = 0;

    while (shortcut[i] == '<') {
	if (!strncmp(shortcut + i, "<cmd>", 5)) {
	    mods &= ~kMenuNoCommandModifier;
	    i += 5;
	} else if (!strncmp(shortcut + i, "<shift>", 7)) {
	    mods |= kMenuShiftModifier;
	    i += 7;
	} else if (!strncmp(shortcut + i, "<option>", 8)) {
	    mods |= kMenuOptionModifier;
	    i += 8;
	} else if (!strncmp(shortcut + i, "<ctrl>", 6)) {
	    mods |= kMenuControlModifier;
	    i += 6;
	} else
	    return false;
    }
    if (shortcut[i] && shortcut[i + 1] == 0) {
	key = shortcut[i];
	if (key >= 'a' && key <= 'z') key -= 'a' - 'A';
	else if (key >= 'A' && key <= 'Z') mods |= kMenuShiftModifier;
    } else
	return false;

    *pkey = key;
    *pmods = mods;
    return true;
}

x3type x3menuitemtype = { NULL, NULL, x3add_default };

x3widget *x3menuitem(x3widget *parent, char *name, char *cmd, char *shortcut)
{
    CFStringRef cflabel = CFStringCreateWithCString(NULL, name,
						    kCFStringEncodingUTF8);
    MenuItemIndex index;

    AppendMenuItemTextWithCFString(parent->u.menu, cflabel,
				   0,
				   x3mkmultichar(cmd), &index);
    if (shortcut) {
	UInt16 key;
	UInt8 mods;

	if (x3parseshortcut(shortcut, &key, &mods)) {
	    SetMenuItemCommandKey(parent->u.menu, index, false, key);
	    SetMenuItemModifiers(parent->u.menu, index, mods);
	}
    }
    CFRelease(cflabel);
    return x3widget_new_menuitem(parent, &x3menuitemtype, index);
}

x3widget *x3menusep(x3widget *parent)
{
    Str255 str = {1, '-'};

    AppendMenu(parent->u.menu, str);
    return x3widget_new_menuitem(parent, &x3menuitemtype, -1);
}

void x3button_sizereq(x3widget *w)
{
    SInt16 offset;
    Rect r = { 0, 0, 0, 0 };

    GetBestControlRect(w->u.hiview, &r, &offset);
    w->sizerequest.x0 = r.left;
    w->sizerequest.y0 = r.top;
    w->sizerequest.x1 = r.right;
    w->sizerequest.y1 = r.bottom;
#ifdef VERBOSE
    printf("button sizereq = (%g, %g) - (%g, %g)\n",
	   w->sizerequest.x0, w->sizerequest.y0,
	   w->sizerequest.x1, w->sizerequest.y1);
#endif
}

void x3button_sizealloc(x3widget *w, x3rect *r)
{
    Rect bounds;

    bounds.left = r->x0;
    bounds.top = r->y0;
    bounds.right = r->x1;
    bounds.bottom = r->y1;
    /* TODO probably want to use HIViewSetFrame instead */
    printf("button sizealloc = (%g, %g) - (%g, %g)\n",
	   r->x0, r->y0, r->x1, r->y1);
    SetControlBounds(w->u.hiview, &bounds);
}

x3type x3buttontype = { x3button_sizereq,
			x3button_sizealloc,
			x3add_default };

x3widget *x3button(x3widget *parent, char *cmd, char *label)
{
    WindowRef window = x3window_of(parent);
    Rect r = {10, 10, 30, 100};
    ControlRef control;
    OSStatus err;
    CFStringRef cflabel = CFStringCreateWithCString(NULL, label,
						    kCFStringEncodingUTF8);

    err = CreatePushButtonControl(window, &r, cflabel, &control);
    CFRelease(cflabel);
    SetControlCommandID(control, x3mkmultichar(cmd));
    //SetWindowDefaultButton(window, control);
    return x3widget_new_hiview(parent, cmd, &x3buttontype, control);
}

x3widget *x3label(x3widget *parent, char *text)
{
    WindowRef window = x3window_of(parent);
    Rect r = {10, 10, 30, 100};
    ControlRef control;
    OSStatus err;
    Boolean singleline = true;
    CFStringRef cftext = CFStringCreateWithCString(NULL, text,
						    kCFStringEncodingUTF8);

    err = CreateStaticTextControl(window, &r, cftext,
				  NULL, &control);
    CFRelease(cftext);
#if 0
    SetControlData(control, kControlEntireControl,
		   kControlEditTextSingleLineTag, sizeof(Boolean),
		   &singleline);
#endif
    return x3widget_new_hiview(parent, NULL, &x3buttontype, control);
}

x3widget *x3edittext(x3widget *parent, char *cmd)
{
    WindowRef window = x3window_of(parent);
    Rect r = {10, 10, 30, 100};
    ControlRef control;
    OSStatus err;
    Boolean singleline = true;

    err = CreateEditUnicodeTextControl(window, &r, CFSTR(""),
				  false, NULL, &control);
    SetControlCommandID(control, x3mkmultichar(cmd));
#if 0
    SetControlData(control, kControlEntireControl,
		   kControlEditTextSingleLineTag, sizeof(Boolean),
		   &singleline);
#endif
    return x3widget_new_hiview(parent, cmd, &x3buttontype, control);
}

x3widget *x3hpane(x3widget *parent)
{
    return NULL;
}

x3widget *x3vpane(x3widget *parent)
{
    return NULL;
}

typedef struct
{
    HIViewRef view;
    x3viewflags flags;
    x3viewclient *vc;
} x3view_data;

static OSStatus
x3view_construct(EventRef inEvent)
{
    OSStatus err;
    x3view_data *data;

    data = (x3view_data *)malloc(sizeof(x3view_data));
    require_action(data != NULL, CantMalloc, err = memFullErr);
    err = GetEventParameter(inEvent, kEventParamHIObjectInstance,
			    typeHIObjectRef, NULL, sizeof(HIObjectRef), NULL,
			    (HIObjectRef *)&data->view);
    require_noerr(err, ParameterMissing);
    err = SetEventParameter(inEvent, kEventParamHIObjectInstance,
			    typeVoidPtr, sizeof(x3view_data *), &data);

    data->vc = NULL;

 ParameterMissing:
    if (err != noErr)
	free(data);

 CantMalloc:
    return err;
}

static OSStatus
x3view_destruct(EventRef inEvent, x3view_data *inData)
{
    free(inData);
    return noErr;
}

static OSStatus
x3view_initialize(EventHandlerCallRef inCallRef, EventRef inEvent,
		  x3view_data *inData)
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

static OSStatus
x3view_draw(EventRef inEvent, x3view_data *inData)
{
    OSStatus err;
    CGContextRef ctx;

    err = GetEventParameter(inEvent, kEventParamCGContextRef, typeCGContextRef,
			    NULL, sizeof(CGContextRef), NULL, &ctx);
    require_noerr(err, ParameterMissing);

#ifdef VERBOSE
    printf("x3view_draw!\n");
#endif

    if (inData->vc && inData->vc->draw) {
	x3dc dc;

	/* set up bounds */
	if (inData->flags & x3view_2d) {
	    dc.ctx = ctx;
	    dc.path = NULL;
	    dc.buf = NULL;

	    inData->vc->draw(inData->vc, &dc);
	    if (dc.path) {
		CGPathRelease(dc.path);
	    }
	} else if (inData->flags & x3view_rgb) {
	    /* todo */
	}
    }

 ParameterMissing:
    return err;
}

static OSStatus
x3view_get_data(EventRef inEvent, x3view_data *inData)
{
    OSStatus err;
    OSType tag;
    Ptr ptr;
    Size outSize;

    /* Probably could use a bit more error checking here, for type
       and size match. Also, just returning an x3view_data seems a
       little hacky. */
    err = GetEventParameter(inEvent, kEventParamControlDataTag, typeEnumeration,
			    NULL, sizeof(OSType), NULL, &tag);
    require_noerr(err, ParameterMissing);

    err = GetEventParameter(inEvent, kEventParamControlDataBuffer, typePtr,
			    NULL, sizeof(Ptr), NULL, &ptr);

    if (tag == kX3ViewPrivate) {
	*((x3view_data **)ptr) = inData;
	outSize = sizeof(x3view_data *);
    } else
	err = errDataNotSupported;

    if (err == noErr)
	err = SetEventParameter(inEvent, kEventParamControlDataBufferSize, typeLongInteger,
				sizeof(Size), &outSize);

 ParameterMissing:
    return err;
}

static OSStatus
x3view_set_data(EventRef inEvent, x3view_data *inData)
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

    if (tag == 'X3vc') {
	inData->vc = *(x3viewclient **)ptr;
    } else if (tag == 'X3vf') {
	inData->flags = *(x3viewflags *)ptr;
    } else
	err = errDataNotSupported;

 ParameterMissing:
    return err;
}

static OSStatus
x3view_hittest(EventRef inEvent, x3view_data *inData)
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

/*
  If we need more sophisticated tracking (like mixing key events), there's
  a good discussion here:
  http://lists.apple.com/archives/Carbon-development/2001/Apr/msg01688.html
*/
static OSStatus
x3view_track(EventRef inEvent, x3view_data *inData)
{
    OSStatus err;
    HIPoint where;
    MouseTrackingResult mouseStatus;
    HIRect bounds;
    Rect windBounds;
    Point theQDPoint;
    UInt32 mods;

    err = GetEventParameter(inEvent, kEventParamMouseLocation, typeHIPoint,
			    NULL, sizeof(HIPoint), NULL, &where);
    require_noerr(err, ParameterMissing);

    err = GetEventParameter(inEvent, kEventParamKeyModifiers, typeUInt32,
			    NULL, sizeof(UInt32), NULL, &mods);
    require_noerr(err, ParameterMissing);

    err = HIViewGetBounds(inData->view, &bounds);
    require_noerr(err, ParameterMissing);

    GetWindowBounds(GetControlOwner(inData->view), kWindowStructureRgn, &windBounds);

    if (inData->vc && inData->vc->mouse)
	inData->vc->mouse(inData->vc, 1, mods, where.x, where.y);

#ifdef VERBOSE
    printf("press: %g, %g!\n", where.x, where.y);
#endif
    //pe_view_button_press(inData, where.x, where.y, 0);

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
	    if (inData->vc && inData->vc->mouse)
		inData->vc->mouse(inData->vc, -1, mods, where.x, where.y);
	} else if (mouseStatus == kMouseTrackingKeyModifiersChanged) {
	    mods = GetCurrentEventKeyModifiers();
	    if (inData->vc && inData->vc->mouse)
		inData->vc->mouse(inData->vc, 0, mods, where.x, where.y);
	} else {
	    if (inData->vc && inData->vc->mouse)
		inData->vc->mouse(inData->vc, 0, mods, where.x, where.y);
	}
    }

 ParameterMissing:
    return err;
}

pascal OSStatus
x3view_handler(EventHandlerCallRef inCallRef,
		EventRef inEvent,
		void* inUserData )
{
    OSStatus err = eventNotHandledErr;
    UInt32 eventClass = GetEventClass(inEvent);
    UInt32 eventKind = GetEventKind(inEvent);
    x3view_data *data = (x3view_data *)inUserData;

    printf("view handler %c%c%c%c %d\n",
	   (eventClass >> 24) & 0xff, 
	   (eventClass >> 16) & 0xff, 
	   (eventClass >> 8) & 0xff, 
	   (eventClass >> 0) & 0xff, 
	   eventKind);
    switch (eventClass) {
    case kEventClassHIObject:
	switch (eventKind) {
	case kEventHIObjectConstruct:
	    err = x3view_construct(inEvent);
	    break;
	case kEventHIObjectInitialize:
	    err = x3view_initialize(inCallRef, inEvent, data);
	    break;
	case kEventHIObjectDestruct:
	    err = x3view_destruct(inEvent, data);
	    break;
	}
	break;
    case kEventClassControl:
	switch (eventKind) {
	case kEventControlInitialize:
	    err = noErr;
	    break;
	case kEventControlDraw:
	    err = x3view_draw(inEvent, data);
	    break;
	case kEventControlGetData:
	    err = x3view_get_data(inEvent, data);
	    break;
	case kEventControlSetData:
	    err = x3view_set_data(inEvent, data);
	    break;
	case kEventControlTrack:
	    err = x3view_track(inEvent, data);
	    break;
	case kEventControlHitTest:
	    err = x3view_hittest(inEvent, data);
	    break;
	case kEventControlClick:
	    printf("click event\n");
	    break;
	    /*...*/
	}
	break;
    }
    return err;
}

static OSStatus
x3view_register(void)
{
    OSStatus err = noErr;
    static HIObjectClassRef x3view_ClassRef = NULL;

    if (x3view_ClassRef == NULL) {
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
	    { kEventClassControl, kEventControlTrack },
	    { kEventClassControl, kEventControlClick }
	};
	err = HIObjectRegisterSubclass(kX3ViewClassID,
				       kHIViewClassID,
				       0,
				       x3view_handler,
				       GetEventTypeCount(eventList),
				       eventList,
				       NULL,
				       &x3view_ClassRef);
    }
    return err;
}

OSStatus x3view_create(
	WindowRef		inWindow,
	const HIRect*		inBounds,
	HIViewRef*		outView)
{
    OSStatus err;
    EventRef event;

    err = x3view_register();
    require_noerr(err, CantRegister);

    err = CreateEvent(NULL, kEventClassHIObject, kEventHIObjectInitialize,
		      GetCurrentEventTime(), 0, &event);
    require_noerr(err, CantCreateEvent);

    if (inBounds != NULL) {
	err = SetEventParameter(event, 'Boun', typeHIRect, sizeof(HIRect),
				inBounds);
	require_noerr(err, CantSetParameter);
    }

    err = HIObjectCreate(kX3ViewClassID, event, (HIObjectRef*)outView);
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

x3widget *x3view(x3widget *parent, x3viewflags flags, x3viewclient *vc)
{
    WindowRef window = x3window_of(parent);
    HIRect r = { {10, 10}, {30, 100} };
    OSStatus err;
    HIViewRef view;

    err = x3view_create(window, &r, &view);
    err = SetControlData(view, 1, 'X3vc', sizeof(x3view_data *), &vc);
    err = SetControlData(view, 1, 'X3vf', sizeof(x3viewflags), &flags);
    HIViewSetVisible(view, true);
    return x3widget_new_hiview(parent, NULL, &x3buttontype, view);
}

void
x3view_dirty(x3widget *w)
{
    if (w->var == x3carbonhiview)
	HIViewSetNeedsDisplay(w->u.hiview, true);
}

void x3view_scrollto(x3widget *w, int x, int y, int width, int height)
{
    /* todo */
}

void x3viewclient_init(x3viewclient *vc)
{
    vc->destroy = NULL;
    vc->mouse = NULL;
    vc->key = NULL;
    vc->draw = NULL;
}

/* Functions for manipulating widget state - some fairly polymorphic. */

void x3setactive(x3widget *w, int active)
{
    if (w->var == x3carbonmenuitem) {
	MenuRef menu = w->parent->u.menu;
	if (active)
	    EnableMenuItem(menu, w->u.menuitem);
	else
	    DisableMenuItem(menu, w->u.menuitem);
	/* According to Carbon docs, we need to redraw menu. */
    } else if (w->var == x3carbonhiview) {
	if (active)
	    ActivateControl(w->u.hiview);
	else
	    DeactivateControl(w->u.hiview);
    }
}

int x3hasfocus(x3widget *w)
{
    if (w->var == x3carbonhiview) {
	return HIViewSubtreeContainsFocus(w->u.hiview);
    } else
	return 0;
}

/* 2d drawing functions, implemented using Quartz */

void
x3moveto(x3dc *dc, double x, double y)
{
    if (dc->path == NULL) {
	dc->path = CGPathCreateMutable();
    }
    CGPathMoveToPoint(dc->path, NULL, x, y);
}

void 
x3lineto(x3dc *dc, double x, double y)
{
    CGPathAddLineToPoint(dc->path, NULL, x, y);
}

void 
x3curveto(x3dc *dc,
	  double x1, double y1,
	  double x2, double y2,
	  double x3, double y3)
{
    CGPathAddCurveToPoint(dc->path, NULL, x1, y1, x2, y2, x3, y3);
}

void 
x3closepath(x3dc *dc)
{
    CGPathCloseSubpath(dc->path);
}

void 
x3rectangle(x3dc *dc, double x, double y, double width, double height)
{
    CGRect rect;

    if (dc->path == NULL) {
	dc->path = CGPathCreateMutable();
    }
    rect.origin.x = x;
    rect.origin.y = y;
    rect.size.width = width;
    rect.size.height = height;
    CGPathAddRect(dc->path, NULL, rect);
}

void
x3getcurrentpoint(x3dc *dc, double *px, double *py)
{
    CGPoint point = CGPathGetCurrentPoint(dc->path);

    *px = point.x;
    *py = point.y;
}

void
x3setrgba(x3dc *dc, unsigned int rgba)
{
    CGContextSetRGBFillColor(dc->ctx,
			     ((rgba >> 24) & 0xff) * (1.0/255),
			     ((rgba >> 16) & 0xff) * (1.0/255),
			     ((rgba >> 8) & 0xff) * (1.0/255),
			     (rgba & 0xff) * (1.0/255));
    CGContextSetRGBStrokeColor(dc->ctx,
			       ((rgba >> 24) & 0xff) * (1.0/255),
			       ((rgba >> 16) & 0xff) * (1.0/255),
			       ((rgba >> 8) & 0xff) * (1.0/255),
			       (rgba & 0xff) * (1.0/255));
}

void
x3setlinewidth(x3dc *dc, double w)
{
    CGContextSetLineWidth(dc->ctx, w);
}

void
x3fill(x3dc *dc)
{
    CGContextAddPath(dc->ctx, dc->path);
    CGPathRelease(dc->path);
    dc->path = NULL;
    CGContextFillPath(dc->ctx);
}

void
x3stroke(x3dc *dc)
{
    CGContextAddPath(dc->ctx, dc->path);
    CGPathRelease(dc->path);
    dc->path = NULL;
    CGContextStrokePath(dc->ctx);
}

void
x3selectfont(x3dc *dc, char *fontname, int slant, int weight)
{
    CGContextSelectFont(dc->ctx, fontname, 8.0, kCGEncodingMacRoman);
}

void
x3setfontsize(x3dc *dc, double size)
{
    CGContextSetFontSize(dc->ctx, size);
}

void
x3showtext(x3dc *dc, char *text)
{
    CGPoint point = CGPathGetCurrentPoint(dc->path);
    CGAffineTransform textmat;

    textmat = CGAffineTransformMakeScale(1, -1);
    CGContextSetTextMatrix(dc->ctx, textmat);
    CGContextShowTextAtPoint(dc->ctx, point.x, point.y, text, strlen(text));
}

void x3textextents(x3dc *dc, char *text, x3extents *extents)
{
    /* todo */
}
