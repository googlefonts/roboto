FT_LOAD_TARGETS
===============

A list of values that are used to select a specific hinting algorithm to use
by the hinter. You should OR one of these values to your 'load_flags' when
calling FT_Load_Glyph.

Note that font's native hinters may ignore the hinting algorithm you have
specified (e.g., the TrueType bytecode interpreter). You can set
.. data:: FT_LOAD_FORCE_AUTOHINT to ensure that the auto-hinter is used.

Also note that FT_LOAD_TARGET_LIGHT is an exception, in that it always
implies FT_LOAD_FORCE_AUTOHINT.


.. data:: FT_LOAD_TARGET_NORMAL	

  This corresponds to the default hinting algorithm, optimized for standard
  gray-level rendering. For monochrome output, use FT_LOAD_TARGET_MONO instead.


.. data:: FT_LOAD_TARGET_LIGHT	

  A lighter hinting algorithm for non-monochrome modes. Many generated glyphs
  are more fuzzy but better resemble its original shape. A bit like rendering
  on Mac OS X.

  As a special exception, this target implies FT_LOAD_FORCE_AUTOHINT.


.. data:: FT_LOAD_TARGET_MONO	

  Strong hinting algorithm that should only be used for monochrome output. The
  result is probably unpleasant if the glyph is rendered in non-monochrome
  modes.


.. data:: FT_LOAD_TARGET_LCD	

  A variant of FT_LOAD_TARGET_NORMAL optimized for horizontally decimated LCD
  displays.


.. data:: FT_LOAD_TARGET_LCD_V	

  A variant of FT_LOAD_TARGET_NORMAL optimized for vertically decimated LCD
  displays.

