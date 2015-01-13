FT_ENCODINGS
============

An enumeration used to specify character sets supported by charmaps. Used in
the FT_Select_Charmap API function.

.. data:: FT_ENCODING_NONE	

  The encoding value 0 is reserved.

.. data:: FT_ENCODING_UNICODE	

  Corresponds to the Unicode character set. This value covers all versions of
  the Unicode repertoire, including ASCII and Latin-1. Most fonts include a
  Unicode charmap, but not all of them.

  For example, if you want to access Unicode value U+1F028 (and the font
  contains it), use value 0x1F028 as the input value for FT_Get_Char_Index.

.. data:: FT_ENCODING_MS_SYMBOL	

  Corresponds to the Microsoft Symbol encoding, used to encode mathematical
  symbols in the 32..255 character code range. For more information, see
  'http://www.ceviz.net/symbol.htm'.

.. data:: FT_ENCODING_SJIS	

  Corresponds to Japanese SJIS encoding. More info at at
  'http://langsupport.japanreference.com/encoding.shtml'. See note on
  multi-byte encodings below.

.. data:: FT_ENCODING_GB2312	

  Corresponds to an encoding system for Simplified Chinese as used used in
  mainland China.

.. data:: FT_ENCODING_BIG5	

  Corresponds to an encoding system for Traditional Chinese as used in Taiwan
  and Hong Kong.

.. data:: FT_ENCODING_WANSUNG	

  Corresponds to the Korean encoding system known as Wansung. For more
  information see 'http://www.microsoft.com/typography/unicode/949.txt'.

.. data:: FT_ENCODING_JOHAB	

  The Korean standard character set (KS C 5601-1992), which corresponds to MS
  Windows code page 1361. This character set includes all possible Hangeul
  character combinations.

.. data:: FT_ENCODING_ADOBE_LATIN_1

  Corresponds to a Latin-1 encoding as defined in a Type 1 PostScript font. It
  is limited to 256 character codes.

.. data:: FT_ENCODING_ADOBE_STANDARD

  Corresponds to the Adobe Standard encoding, as found in Type 1, CFF, and
  OpenType/CFF fonts. It is limited to 256 character codes.

.. data:: FT_ENCODING_ADOBE_EXPERT

  Corresponds to the Adobe Expert encoding, as found in Type 1, CFF, and
  OpenType/CFF fonts. It is limited to 256 character codes.

.. data:: FT_ENCODING_ADOBE_CUSTOM

  Corresponds to a custom encoding, as found in Type 1, CFF, and OpenType/CFF
  fonts. It is limited to 256 character codes.

.. data:: FT_ENCODING_APPLE_ROMAN

  Corresponds to the 8-bit Apple roman encoding. Many TrueType and OpenType
  fonts contain a charmap for this encoding, since older versions of Mac OS are
  able to use it.

.. data:: FT_ENCODING_OLD_LATIN_2

  This value is deprecated and was never used nor reported by FreeType. Don't
  use or test for it.

