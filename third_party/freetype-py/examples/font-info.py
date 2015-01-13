# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
from freetype import *

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: %s font_filename" % sys.argv[0])
        sys.exit()

    face = Face(sys.argv[1])

    print 'Family name:        ', face.family_name
    print 'Style name:         ', face.style_name
    print 'Charmaps:           ', [charmap.encoding_name for charmap in face.charmaps]
    print
    print 'Face number:        ', face.num_faces
    print 'Glyph number:       ', face.num_glyphs
    print 'Available sizes:    ', face.available_sizes
    print
    print 'units per em:       ', face.units_per_EM
    print 'ascender:           ', face.ascender
    print 'descender:          ', face.descender
    print 'height:             ', face.height
    print
    print 'max_advance_width:  ', face.max_advance_width
    print 'max_advance_height: ', face.max_advance_height
    print
    print 'underline_position: ', face.underline_position
    print 'underline_thickness:', face.underline_thickness
    print
    print 'Has horizontal:     ', face.has_horizontal
    print 'Has vertical:       ', face.has_vertical
    print 'Has kerning:        ', face.has_kerning
    print 'Is fixed width:     ', face.is_fixed_width
    print 'Is scalable:        ', face.is_scalable
    print
