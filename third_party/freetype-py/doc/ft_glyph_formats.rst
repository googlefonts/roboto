FT_GLYPH_FORMATS
================

An enumeration type used to describe the format of a given glyph image. Note
that this version of FreeType only supports two image formats, even though
future font drivers will be able to register their own format.

.. data:: FT_GLYPH_FORMAT_NONE	

  The value 0 is reserved.

.. data:: FT_GLYPH_FORMAT_COMPOSITE

  The glyph image is a composite of several other images. This format is only
  used with FT_LOAD_NO_RECURSE, and is used to report compound glyphs (like
  accented characters).

.. data:: FT_GLYPH_FORMAT_BITMAP	

  The glyph image is a bitmap, and can be described as an FT_Bitmap. You
  generally need to access the 'bitmap' field of the FT_GlyphSlotRec structure
  to read it.

.. data:: FT_GLYPH_FORMAT_OUTLINE

  The glyph image is a vectorial outline made of line segments and Bezier arcs;
  it can be described as an FT_Outline; you generally want to access the
  'outline' field of the FT_GlyphSlotRec structure to read it.

.. data:: FT_GLYPH_FORMAT_PLOTTER

  The glyph image is a vectorial path with no inside and outside contours. Some
  Type 1 fonts, like those in the Hershey family, contain glyphs in this
  format. These are described as FT_Outline, but FreeType isn't currently
  capable of rendering them correctly.

