FT_OUTLINE_FLAGS
================

A list of bit-field constants use for the flags in an outline's 'flags'
field.


.. data:: FT_OUTLINE_NONE	

  Value 0 is reserved.


.. data:: FT_OUTLINE_OWNER	

  If set, this flag indicates that the outline's field arrays (i.e., 'points',
  'flags', and 'contours') are 'owned' by the outline object, and should thus
  be freed when it is destroyed.


.. data:: FT_OUTLINE_EVEN_ODD_FILL

  By default, outlines are filled using the non-zero winding rule. If set to 1,
  the outline will be filled using the even-odd fill rule (only works with the
  smooth rasterizer).


.. data:: FT_OUTLINE_REVERSE_FILL

  By default, outside contours of an outline are oriented in clock-wise
  direction, as defined in the TrueType specification. This flag is set if the
  outline uses the opposite direction (typically for Type 1 fonts). This flag
  is ignored by the scan converter.


.. data:: FT_OUTLINE_IGNORE_DROPOUTS

  By default, the scan converter will try to detect drop-outs in an outline and
  correct the glyph bitmap to ensure consistent shape continuity. If set, this
  flag hints the scan-line converter to ignore such cases. See below for more
  information.


.. data:: FT_OUTLINE_SMART_DROPOUTS

  Select smart dropout control. If unset, use simple dropout control. Ignored
  if FT_OUTLINE_IGNORE_DROPOUTS is set. See below for more information.


.. data:: FT_OUTLINE_INCLUDE_STUBS

  If set, turn pixels on for 'stubs', otherwise exclude them. Ignored if
  FT_OUTLINE_IGNORE_DROPOUTS is set. See below for more information.


.. data:: FT_OUTLINE_HIGH_PRECISION
 
  This flag indicates that the scan-line converter should try to convert this
  outline to bitmaps with the highest possible quality. It is typically set for
  small character sizes. Note that this is only a hint that might be completely
  ignored by a given scan-converter.


.. data:: FT_OUTLINE_SINGLE_PASS	

  This flag is set to force a given scan-converter to only use a single pass
  over the outline to render a bitmap glyph image. Normally, it is set for very
  large character sizes. It is only a hint that might be completely ignored by
  a given scan-converter.

