FT_STROKER_LINEJOINS
====================

These values determine how two joining lines are rendered in a stroker.


.. data:: FT_STROKER_LINEJOIN_ROUND

  Used to render rounded line joins. Circular arcs are used to join two lines
  smoothly.


.. data:: FT_STROKER_LINEJOIN_BEVEL

  Used to render beveled line joins; i.e., the two joining lines are extended
  until they intersect.


.. data:: FT_STROKER_LINEJOIN_MITER

  Same as beveled rendering, except that an additional line break is added if
  the angle between the two joining lines is too closed (this is useful to
  avoid unpleasant spikes in beveled rendering).

