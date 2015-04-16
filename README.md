# Setup
The Roboto build toolchain depends on:

- FontTools (https://github.com/behdad/fonttools)
- RoboFab (https://github.com/robofab-developers/robofab)
- An expanded version of Tal Leming's feaTools
  (https://github.com/jamesgk/feaTools/tree/expanded), for feature handling.
- BooleanOperations (https://github.com/typemytype/booleanOperations), for
  glyph overlap removal.

### OTF Generation
OTF generation depends on:

- ufo2fdk (https://github.com/typesupply/ufo2fdk)
- Open-source portions of the AFDKO
  (https://github.com/adobe-type-tools/afdko/releases)

The AFDKO from GitHub can be time consuming to setup. It is easier to just use
the variety which includes closed-source tools
(http://www.adobe.com/devnet/opentype/afdko.html), though these closed-source
portions are not used to build Roboto.

### TTF Generation
TTF generation depends on:

- FontForge (https://github.com/fontforge/fontforge)

Whose Python interface should be availabe on Ubuntu by default via `apt-get
install fontforge` and `apt-get install python-fontforge`.

# Testing
Test scripts (specifically, code in common-tests.py) depend on:

- https://github.com/rougier/freetype-py
