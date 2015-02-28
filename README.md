# Setup

### OTF Generation
OTF generation depends on:
- ufo2fdk (https://github.com/typesupply/ufo2fdk)
- Open-source portions of the AFDKO (https://github.com/adobe-type-tools/afdko/releases)
The AFDKO from GitHub can be time consuming to setup. It is easier to just use the variety which includes closed-source tools (http://www.adobe.com/devnet/opentype/afdko.html), though these closed-source portions are not used to build Roboto.

### TTF Generation and Overlap Removal
TTF generation and overlap removal depend on:
- FontForge (https://github.com/fontforge/fontforge)
Whose Python interface should be availabe on Ubuntu by default via `apt-get install fontforge` and `apt-get install python-fontforge`.
