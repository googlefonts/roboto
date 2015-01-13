FT_LCD_FILTERS
==============

A list of values to identify various types of LCD filters.


.. data:: FT_LCD_FILTER_NONE	

  Do not perform filtering. When used with subpixel rendering, this results in
  sometimes severe color fringes.


.. data:: FT_LCD_FILTER_DEFAULT	

  The default filter reduces color fringes considerably, at the cost of a
  slight blurriness in the output.


.. data:: FT_LCD_FILTER_LIGHT	

  The light filter is a variant that produces less blurriness at the cost of
  slightly more color fringes than the default one. It might be better,
  depending on taste, your monitor, or your personal vision.


.. data:: FT_LCD_FILTER_LEGACY	

  This filter corresponds to the original libXft color filter. It provides high
  contrast output but can exhibit really bad color fringes if glyphs are not
  extremely well hinted to the pixel grid. In other words, it only works well
  if the TrueType bytecode interpreter is enabled and high-quality hinted fonts
  are used.

  This filter is only provided for comparison purposes, and might be disabled
  or stay unsupported in the future.

