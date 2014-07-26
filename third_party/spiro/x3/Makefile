TARGET = gtk

ifeq ($(TARGET),gtk)
  X3_PLAT = X3_GTK
  X3_INCL = `pkg-config --cflags gtk+-2.0`
  X3_LIBS = `pkg-config --libs gtk+-2.0`
endif

ifeq ($(TARGET),carbon)
  X3_PLAT = X3_CARBON
  X3_LIBS = -framework Carbon
endif

ifeq ($(TARGET),win32)
  X3_PLAT = X3_WIN32
  X3_LIBS = -lgdi32
endif

CFLAGS = -g -Wall -D$(X3_PLAT) $(X3_INCL)
LDFLAGS = -g
LDLIBS = $(X3_LIBS)

test:	test.o x3$(TARGET).o x3common.o

x3lisp.o:	x3lisp.c
