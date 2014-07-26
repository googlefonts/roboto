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
#include <Carbon/Carbon.h>

#include "bezctx.h"
#include "bezctx_quartz.h"
#include "plate.h"
#include "pe_view.h"

#define kCommandToggleCorner 'togC'

typedef struct {
    WindowRef window_ref;
    plate *p;

    HIViewRef view;
} plate_edit;

int n_iter = 10;

pascal OSStatus my_handler(EventHandlerCallRef nextHandler, EventRef theEvent, void *data)
{
    plate_edit *pe = (plate_edit *)data;
    WindowRef window = pe->window_ref;
    UInt32 klass = GetEventClass(theEvent);
    UInt32 kind = GetEventKind(theEvent);
    OSStatus result = eventNotHandledErr;
    OSStatus err;
    Point where;
    Rect bounds;

    switch (klass) {
    case kEventClassMouse:
	switch (kind) {
	case kEventMouseDown:
	    err = GetEventParameter(theEvent, kEventParamMouseLocation,
				       typeQDPoint, NULL, sizeof(where), NULL, &where);
	    printf("mouse down %d %d\n", where.h, where.v);
	    break;
	}
	break;
    case kEventClassWindow:
	switch (kind) {
	case kEventWindowDrawContent:
	    printf("draw content\n");
	    result = noErr;
	    break;
	case kEventWindowClickContentRgn:
	    printf("click_content region\n");
	    break;
	case kEventWindowHandleContentClick:
	    err = GetEventParameter(theEvent, kEventParamMouseLocation,
				    typeQDPoint, NULL, sizeof(where), NULL, &where);
	    GetWindowBounds(window, kWindowContentRgn, &bounds);
	    printf("content click %d, %d; %d, %d\n", where.h, where.v,
		   where.h - bounds.left, where.v - bounds.top);
	    break;
	}
    }
    return result;
}

pascal OSStatus app_handler(EventHandlerCallRef nextHandler, EventRef theEvent, void *data)
{
    plate_edit *pe = (plate_edit *)data;
    HICommand hiCommand;
    OSStatus result = eventNotHandledErr;
    GetEventParameter(theEvent, kEventParamDirectObject, typeHICommand,NULL,
                          sizeof(HICommand),NULL,&hiCommand);
    unsigned int c = hiCommand.commandID;
    MenuRef menu;
    MenuItemIndex ix;

    printf("app_handler %c%c%c%c\n",
	   (c >> 24) & 255, (c >> 16) & 255, (c >> 8) & 255, c & 255);
    switch (c) {
    case kHICommandUndo:
	GetIndMenuItemWithCommandID(NULL, kHICommandUndo, 1, &menu, &ix);
	SetMenuItemTextWithCFString(menu, ix, CFSTR("Undo disabled"));
	DisableMenuItem(menu, ix);
	break;
    case kCommandToggleCorner:
	pe_view_toggle_corner(pe->view);
	break;
    }
    return result;
}

void
add_pe_view(WindowRef window, plate_edit *pe, plate *p)
{
    HIRect rect = {{0, 0}, {32767, 32767}};
    HIViewRef view;

    pe_view_create(window, &rect, &view);
    pe_view_set_plate(view, p);
    HIViewSetVisible(view, true);
    pe->view = view;
}

void
init_window(WindowRef window, plate_edit *pe)
{
    EventTypeSpec app_event_types[] = {
	{ kEventClassCommand, kEventProcessCommand }
    };
    EventTypeSpec event_types[] = {
	{ kEventClassWindow, kEventWindowDrawContent },
	{ kEventClassWindow, kEventWindowHandleContentClick },
	{ kEventClassMouse, kEventMouseDown }
    };

    InstallApplicationEventHandler(NewEventHandlerUPP(app_handler),
				   GetEventTypeCount(app_event_types),
				   app_event_types, (void *)pe, NULL);
    InstallWindowEventHandler(window, NewEventHandlerUPP(my_handler),
			      GetEventTypeCount(event_types),
			      event_types, (void *)pe, NULL);

    add_pe_view(window, pe, pe->p);
}

int main(int argc, char* argv[])
{
    IBNibRef 		nibRef;
    WindowRef 		window;
    plate_edit pe;
    
    OSStatus		err;

    // Create a Nib reference passing the name of the nib file (without the .nib extension)
    // CreateNibReference only searches into the application bundle.
    err = CreateNibReference(CFSTR("main"), &nibRef);
    require_noerr( err, CantGetNibRef );
    
    // Once the nib reference is created, set the menu bar. "MainMenu" is the name of the menu bar
    // object. This name is set in InterfaceBuilder when the nib is created.
    err = SetMenuBarFromNib(nibRef, CFSTR("MenuBar"));
    require_noerr( err, CantSetMenuBar );
    
    // Then create a window. "MainWindow" is the name of the window object. This name is set in 
    // InterfaceBuilder when the nib is created.
    err = CreateWindowFromNib(nibRef, CFSTR("MainWindow"), &window);
    require_noerr( err, CantCreateWindow );

    // We don't need the nib reference anymore.
    DisposeNibReference(nibRef);

    pe.window_ref = window;
    pe.p = file_read_plate("/Users/raph/golf/ppedit/g.plate");
    if (pe.p == NULL)
	pe.p = new_plate();
    init_window(window, &pe);
    // The window was created hidden so show it.
    ShowWindow( window );
    
    // Call the event loop
    RunApplicationEventLoop();

CantCreateWindow:
CantSetMenuBar:
CantGetNibRef:
	return err;
}
