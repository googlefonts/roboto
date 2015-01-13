TT_PLATFORMS
============

A list of valid values for the 'platform_id' identifier code in FT_CharMapRec
and FT_SfntName structures.


.. data:: TT_PLATFORM_APPLE_UNICODE

  Used by Apple to indicate a Unicode character map and/or name entry. See
  TT_APPLE_ID_XXX for corresponding 'encoding_id' values. Note that name
  entries in this format are coded as big-endian UCS-2 character codes only.


.. data:: TT_PLATFORM_MACINTOSH	

  Used by Apple to indicate a MacOS-specific charmap and/or name entry. See
  TT_MAC_ID_XXX for corresponding 'encoding_id' values. Note that most TrueType
  fonts contain an Apple roman charmap to be usable on MacOS systems (even if
  they contain a Microsoft charmap as well).


.. data:: TT_PLATFORM_ISO	

  This value was used to specify ISO/IEC 10646 charmaps. It is however now
  deprecated. See TT_ISO_ID_XXX for a list of corresponding 'encoding_id'
  values.


.. data:: TT_PLATFORM_MICROSOFT	

  Used by Microsoft to indicate Windows-specific charmaps. See TT_MS_ID_XXX for
  a list of corresponding 'encoding_id' values. Note that most fonts contain a
  Unicode charmap using (TT_PLATFORM_MICROSOFT, TT_MS_ID_UNICODE_CS).


.. data:: TT_PLATFORM_CUSTOM	

  Used to indicate application-specific charmaps.


.. data:: TT_PLATFORM_ADOBE	

  This value isn't part of any font format specification, but is used by
  FreeType to report Adobe-specific charmaps in an FT_CharMapRec structure. See
  TT_ADOBE_ID_XXX.

