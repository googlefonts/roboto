# Roboto V2 Sources
This directory contains the current masters used to generate the Roboto Sans and
Roboto Condensed families.

### Updating Sources
When replacing the source VFBs, the source UFOs should be synced using FontLab's
vfb2ufo converter: http://blog.fontlab.com/font-utility/vfb2ufo/

Windows and Mac OS downloads are provided. The Windows download runs on Linux
via wine:

```
wine [path-to-vfb2ufo]/exe/vfb2ufo.exe [roboto]/src/v2/Roboto_Thin.vfb
wine [path-to-vfb2ufo]/exe/vfb2ufo.exe [roboto]/src/v2/Roboto_Regular.vfb
wine [path-to-vfb2ufo]/exe/vfb2ufo.exe [roboto]/src/v2/Roboto_Bold.vfb
```

The converter should work both ways, so it is possible to convert altered UFOs
back into VFBs which can be opened in FontLab.

### Notes
There is currently an issue when converting via vfb2ufo, in which
some anchors are dropped from glyphs. For now it is also necessary to run the
script `get_dropped_anchors.py` through FontLab after updating the VFBs, in
order to extract these dropped anchors into an external resource which is then
re-incorporated into the masters during the build.

vfb2ufo may output UFOs with bogus timestamps. Verify the openTypeNameCreated
field in the output `fontinfo.plist` files.
