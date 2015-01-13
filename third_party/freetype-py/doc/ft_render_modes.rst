FT_RENDER_MODES
===============

An enumeration type that lists the render modes supported by FreeType 2. Each
mode corresponds to a specific type of scanline conversion performed on the
outline.

For bitmap fonts and embedded bitmaps the 'bitmap->pixel_mode' field in the
.. data:: FT_GlyphSlotRec structure gives the format of the returned bitmap.

All modes except FT_RENDER_MODE_MONO use 256 levels of opacity.


.. data:: FT_RENDER_MODE_NORMAL	

  This is the default render mode; it corresponds to 8-bit anti-aliased
  bitmaps.


.. data:: FT_RENDER_MODE_LIGHT	

  This is equivalent to FT_RENDER_MODE_NORMAL. It is only defined as a separate
  value because render modes are also used indirectly to define hinting
  algorithm selectors. See FT_LOAD_TARGET_XXX for details.


.. data:: FT_RENDER_MODE_MONO	

  This mode corresponds to 1-bit bitmaps (with 2 levels of opacity).


.. data:: FT_RENDER_MODE_LCD	

  This mode corresponds to horizontal RGB and BGR sub-pixel displays like LCD
  screens. It produces 8-bit bitmaps that are 3 times the width of the original
  glyph outline in pixels, and which use the FT_PIXEL_MODE_LCD mode.


.. data:: FT_RENDER_MODE_LCD_V	

  This mode corresponds to vertical RGB and BGR sub-pixel displays (like PDA
  screens, rotated LCD displays, etc.). It produces 8-bit bitmaps that are 3
  times the height of the original glyph outline in pixels and use the
  FT_PIXEL_MODE_LCD_V mode.

