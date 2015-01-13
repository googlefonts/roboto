=============
Release notes
=============

0.4.1
=====
* Fixed a bug in Face.load_char
* Added get_format and get_fstype in Face (titusz.pan)

0.3.3
=====
* Fixed a bug in get_kerning
* Added test against freetype version for FT_ReferenceFace and FT_Get_FSType_Flags

0.3.2
=====
* Added wordle.py example
* Added get_bbox for Outline class
* Added get_cbox for Outline and Glyph classes
* Added __del__ method to Face class
* Set encoding (utf-8) to all source files and examples.
* Added test against freetype version for FT_Library_SetLcdFilterWeights.

0.3.1
=====
* Added FT_Stroker bindings (enums, structs and methods)
* Added ft-outline and ft-color examples
* Fixed first/next char in Face
* Pythonic interface has been documented

0.3.0
=====
* Added ftdump.py demo and necessary functions

0.2.0
=====
* Added sfnt functions
* Added TT_XXX flags in ft_enums
* New examples

0.1.1
=====
* Initial release
* Working examples
