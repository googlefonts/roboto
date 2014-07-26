#if defined(X3_CARBON) || defined(X3_WIN32)

void x3qsizereq(x3widget *w);

void x3add_default(x3widget *parent, x3widget *child);
void x3add(x3widget *parent, x3widget *child);

#endif

void x3initqs(void);
void x3qshow(x3widget *w);
void x3sync(void);


/* provided by impls to common routines */
void x3_window_show(x3widget *w);
