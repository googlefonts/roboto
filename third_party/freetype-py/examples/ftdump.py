#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
# -----------------------------------------------------------------------------
from __future__ import print_function
from __future__ import division
import sys
from freetype import *

verbose     = 0
debug       = 0
name_tables = 0

def usage( execname ):
    print( )
    print( "ftdump: simple font dumper -- part of the FreeType project" )
    print( "----------------------------------------------------------" )
    print( "Usage: %s [options] fontname", execname )
    print( )
    print( "  -n        print SFNT name tables" )
    print( "  -v        be verbose" )
    print( )
    sys.exit()


def Print_Name( face ):
    print( "font name entries" );
    print( "   family:     %s" % face.family_name )
    print( "   style:      %s" % face.style_name )
    ps_name = face.postscript_name or "UNAVAILABLE"
    print( "   postscript: %s" % ps_name )


def Print_Type( face ):

    print( "font type entries" )

    #   module = &face->driver->root;
    #   printf( "   FreeType driver: %s\n", module->clazz->module_name );

    #  Is it better to dump all sfnt tag names?
    print( "   sfnt wrapped:    ",end="")
    if face.is_sfnt: print( "yes")
    else:            print( "no")

    # is scalable ?
    print( "   type:            ", end="")
    if face.is_scalable:
        print( "scalable, ", end="")
        if face.has_multiple_masters:
            print( "multiple_masters, ", end="")
    if face.has_fixed_sizes:
        print( "fixed size",end="")
    print()

    #  Direction
    print( "   direction:       ", end="" )
    if face.has_horizontal:
        print( "horizontal, ", end="")
    if face.has_vertical:
        print( "vertical", end="")
    print( )

    # Fixed width
    print( "   fixed width:     ", end="")
    if face.is_fixed_width: print( "yes")
    else:                   print( "no")

    # Glyph names
    print( "   glyph names:     ", end="")
    if face.has_glyph_names: print( "yes")
    else:                   print( "no")

    if face.is_scalable:
        print( "   EM size:         %d" % face.units_per_EM )
        print( "   global BBox:     (%ld,%ld):(%ld,%ld)" %
               (face.bbox.xMin, face.bbox.yMin,
                face.bbox.xMax, face.bbox.yMax ))
        print( "   ascent:          %d" % face.ascender )
        print( "   descent:         %d" % face.descender )
        print( "   text height:     %d" % face.height )


def get_platform_id( platform_id ):
    if platform_id == TT_PLATFORM_APPLE_UNICODE:
        return "Apple (Unicode)"
    elif platform_id == TT_PLATFORM_MACINTOSH:
        return "Macintosh"
    elif platform_id == TT_PLATFORM_ISO:
        return "ISO (deprecated)"
    elif platform_id == TT_PLATFORM_MICROSOFT:
        return "Microsoft"
    elif platform_id == TT_PLATFORM_CUSTOM:
        return "custom"
    elif platform_id == TT_PLATFORM_ADOBE:
        return "Adobe"
    else:
      return "UNKNOWN"

def get_name_id( name_id ):
    if name_id == TT_NAME_ID_COPYRIGHT:
        return "copyright"
    elif name_id == TT_NAME_ID_FONT_FAMILY:
        return "font family"
    elif name_id == TT_NAME_ID_FONT_SUBFAMILY:
        return "font subfamily"
    elif name_id == TT_NAME_ID_UNIQUE_ID:
        return "unique ID"
    elif name_id == TT_NAME_ID_FULL_NAME:
        return "full name"
    elif name_id == TT_NAME_ID_VERSION_STRING:
        return "version string"
    elif name_id == TT_NAME_ID_PS_NAME:
        return "PostScript name"
    elif name_id == TT_NAME_ID_TRADEMARK:
        return "trademark"

    # the following values are from the OpenType spec 
    elif name_id == TT_NAME_ID_MANUFACTURER:
        return "manufacturer"
    elif name_id == TT_NAME_ID_DESIGNER:
        return "designer"
    elif name_id == TT_NAME_ID_DESCRIPTION:
        return "description"
    elif name_id == TT_NAME_ID_VENDOR_URL:
        return "vendor URL"
    elif name_id == TT_NAME_ID_DESIGNER_URL:
        return "designer URL"
    elif name_id == TT_NAME_ID_LICENSE:
        return "license"
    elif name_id == TT_NAME_ID_LICENSE_URL:
        return "license URL"
    # number 15 is reserved
    elif name_id == TT_NAME_ID_PREFERRED_FAMILY:
        return "preferred family"
    elif name_id == TT_NAME_ID_PREFERRED_SUBFAMILY:
        return "preferred subfamily"
    elif name_id == TT_NAME_ID_MAC_FULL_NAME:
        return "Mac full name"

    # The following code is new as of 2000-01-21
    elif name_id == TT_NAME_ID_SAMPLE_TEXT:
      return "sample text"

    # This is new in OpenType 1.3
    elif name_id == TT_NAME_ID_CID_FINDFONT_NAME:
        return "CID 'findfont' name"
    else:
        return "UNKNOWN";


def Print_Sfnt_Names( face ):
    print( "font string entries" );

    for i in range(face.sfnt_name_count):

        name = face.get_sfnt_name(i)
        print( "   %-15s [%s]" % ( get_name_id( name.name_id ),
                                   get_platform_id( name.platform_id )),end="")

        if name.platform_id == TT_PLATFORM_APPLE_UNICODE:
            if name.encoding_id in [TT_APPLE_ID_DEFAULT,
                                    TT_APPLE_ID_UNICODE_1_1,
                                    TT_APPLE_ID_ISO_10646,
                                    TT_APPLE_ID_UNICODE_2_0]:
                print(name.string.decode('utf-16be', 'ignore'))
            else:
                print( "{unsupported encoding %d}" % name.encoding_id )

        elif name.platform_id == TT_PLATFORM_MACINTOSH:
            if name.language_id != TT_MAC_LANGID_ENGLISH:
                print( " (language=%d)" % name.language_id )
            print ( " : " )
            if name.encoding_id == TT_MAC_ID_ROMAN:
                # FIXME: convert from MacRoman to ASCII/ISO8895-1/whatever
                # (MacRoman is mostly like ISO8895-1 but there are differences)
                print(name.string)
            else:
                print( "{unsupported encoding %d}" % name.encoding_id )

        elif name.platform_id == TT_PLATFORM_ISO:
            if name.encoding_id in [ TT_ISO_ID_7BIT_ASCII,
                                     TT_ISO_ID_8859_1]:
                print(name.string)
            print ( " : " )
            if name.encoding_id == TT_ISO_ID_10646:
                print(name.string.decode('utf-16be', 'ignore'))
            else:
                print( "{unsupported encoding %d}" % name.encoding_id )

        elif name.platform_id == TT_PLATFORM_MICROSOFT:
            if name.language_id != TT_MS_LANGID_ENGLISH_UNITED_STATES:
                print( " (language=0x%04x)" % name.language_id );
            print( " : " )
            if name.encoding_id in [TT_MS_ID_SYMBOL_CS,
                                    TT_MS_ID_UNICODE_CS]:
                print(name.string.decode('utf-16be', 'ignore'))
            else:
                print( "{unsupported encoding %d}" % name.encoding_id )
        else:
           print( "{unsupported platform}" )

        print( )


def Print_Fixed( face ):

    # num_fixed_size
    print( "fixed size\n" )

    # available size
    for i,bsize in enumerate(face.available_sizes):
        print( "   %3d: height %d, width %d\n",
               i, bsize.height, bsize.width )
        print( "        size %.3f, x_ppem %.3f, y_ppem %.3f\n",
               bsize.size / 64.0,
               bsize.x_ppem / 64.0, bsize.y_ppem / 64.0 )


def Print_Charmaps( face ):
    global verbose
    active = -1
    if face.charmap:
        active = face.charmap.index

    # CharMaps
    print( "charmaps" )
    for i,charmap in enumerate(face.charmaps):
        print( "   %d: platform %d, encoding %d, language %d" %
               (i, charmap.platform_id, charmap.encoding_id,
               int(charmap.cmap_language_id)), end="" )
        if i == active:
            print( " (active)", end="" )
        print ( )
        if verbose:
            face.set_charmap( charmap )
            charcode, gindex = face.get_first_char()
            while ( gindex ):
                print( "      0x%04lx => %d" % (charcode, gindex) )
                charcode, gindex = face.get_next_char( charcode, gindex )



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import getopt
    execname = sys.argv[0]

    if len(sys.argv) < 2:
        usage( execname )
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], ':nv')
    except getopt.GetoptError, err:
        usage( execname )

    verbose = False
    name_tables = False

    for o, a in opts:
        if o == "-v":   verbose = True
        elif o == "-n": name_tables = True
        else:           usage( execname )


    face = Face(args[0])
    num_faces = face.num_faces

    if num_faces > 1:
        print( "There are %d faces in this file." % num_faces)
    else:
        print( "There is 1 face in this file.")

    for i in range(num_faces):
        face = Face(args[0], i)

        print( "\n----- Face number: %d -----\n" % i )
        Print_Name( face )
        print( "" )
        Print_Type( face )
        print( "   glyph count:     %d" % face.num_glyphs )

        if name_tables and face.is_sfnt:
            print( )
            Print_Sfnt_Names( face )
            
        if face.num_fixed_sizes:
            print(  )
            Print_Fixed( face )

        if face.num_charmaps:
            print(  )
            Print_Charmaps( face )
