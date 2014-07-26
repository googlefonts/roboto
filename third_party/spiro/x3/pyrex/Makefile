TARGET = gtk

ifeq ($(TARGET),gtk)
  X3_PLAT = X3_GTK
  X3_INCL = `pkg-config --cflags gtk+-2.0`
  X3_LIBS = `pkg-config --libs gtk+-2.0`
  SHARED_FLAG = -shared
endif

ifeq ($(TARGET),carbon)
  X3_PLAT = X3_CARBON
  X3_LIBS = -framework Carbon
  SHARED_FLAG = -dynamiclib -flat_namespace -undefined suppress
endif

ifeq ($(TARGET),win32)
  X3_PLAT = X3_WIN32
  X3_LIBS = -lgdi32
endif

PY_INCL := -I$(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_inc()")

CFLAGS = -g -Wall -fPIC -I.. $(PY_INCL) -D$(X3_PLAT) $(X3_INCL)
LDFLAGS = -g
LDLIBS = $(X3_LIBS)

x3.so:	x3.o x3$(TARGET).o x3common.o
	gcc $(SHARED_FLAG) $^ $(X3_LIBS) -o $@

x3.c:	x3.pyx
	python2.4-pyrexc $<

x3$(TARGET).o:	../x3$(TARGET).c
	$(CC) -c $(CFLAGS) -o $@ $<

x3common.o:	../x3common.c
	$(CC) -c $(CFLAGS) -o $@ $<


