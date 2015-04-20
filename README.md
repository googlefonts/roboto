# Setup
The Roboto build toolchain depends on:

- FontTools (https://github.com/behdad/fonttools)
- RoboFab (https://github.com/robofab-developers/robofab)
- NumPy and SciPy (http://www.numpy.org/)
- An expanded version of Tal Leming's feaTools
  (https://github.com/jamesgk/feaTools/tree/expanded), for feature handling.
- BooleanOperations (https://github.com/typemytype/booleanOperations), for
  glyph overlap removal.
  - (requires Cython to install: http://cython.org/)

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
install fontforge python-fontforge`.

# Post-Production
Post-production scripts (most of the code outside of the `fontbuild` directory,
e.g. for testing output) depend on:

- The nototools module, installed as part of Noto
  (https://code.google.com/p/noto/)
  - (Noto subsequently depends on HarfBuzz: https://github.com/behdad/harfbuzz)
- freetype-py (https://github.com/rougier/freetype-py)
