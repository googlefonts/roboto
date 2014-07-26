OSStatus pe_view_create(
	WindowRef			inWindow,
	const HIRect*		inBounds,
	HIViewRef*			outView);

void
pe_view_set_plate(HIViewRef view, plate *p);

void
pe_view_toggle_corner(HIViewRef view);

