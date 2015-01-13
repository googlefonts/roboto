FT_STROKER_BORDERS
==================

These values are used to select a given stroke border in
.. data:: FT_Stroker_GetBorderCounts and FT_Stroker_ExportBorder.


.. data:: FT_STROKER_BORDER_LEFT	

  Select the left border, relative to the drawing direction.


.. data:: FT_STROKER_BORDER_RIGHT

  Select the right border, relative to the drawing direction.


Note

  Applications are generally interested in the 'inside' and 'outside'
  borders. However, there is no direct mapping between these and the 'left' and
  'right' ones, since this really depends on the glyph's drawing orientation,
  which varies between font formats.

  You can however use FT_Outline_GetInsideBorder and
  FT_Outline_GetOutsideBorder to get these.

