FT_PIXEL_MODES
==============

An enumeration type that lists the render modes supported by FreeType 2. Each
mode corresponds to a specific type of scanline conversion performed on the
outline.


.. data:: FT_PIXEL_MODE_NONE

  Value 0 is reserved.


.. data:: FT_PIXEL_MODE_MONO

  A monochrome bitmap, using 1 bit per pixel. Note that pixels are stored in
  most-significant order (MSB), which means that the left-most pixel in a byte
  has value 128.


.. data:: FT_PIXEL_MODE_GRAY	

  An 8-bit bitmap, generally used to represent anti-aliased glyph images. Each
  pixel is stored in one byte. Note that the number of 'gray' levels is stored
  in the 'num_grays' field of the FT_Bitmap structure (it generally is 256).


.. data:: FT_PIXEL_MODE_GRAY2   

  A 2-bit per pixel bitmap, used to represent embedded anti-aliased bitmaps in
  font files according to the OpenType specification. We haven't found a single
  font using this format, however.


.. data:: FT_PIXEL_MODE_GRAY4   

  A 4-bit per pixel bitmap, representing embedded anti-aliased bitmaps in font
  files according to the OpenType specification. We haven't found a single font
  using this format, however.


.. data:: FT_PIXEL_MODE_LCD     

  An 8-bit bitmap, representing RGB or BGR decimated glyph images used for
  display on LCD displays; the bitmap is three times wider than the original
  glyph image. See also FT_RENDER_MODE_LCD.


.. data:: FT_PIXEL_MODE_LCD_V   

  An 8-bit bitmap, representing RGB or BGR decimated glyph images used for
  display on rotated LCD displays; the bitmap is three times taller than the
  original glyph image. See also FT_RENDER_MODE_LCD_V.


