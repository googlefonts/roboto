#!/usr/bin/python
"""Post-build changes for Roboto for Android."""

import os
from os import path
import sys

from fontTools import ttLib
from nototools import font_data


def output_protruding_glyphs(font, ymin, ymax, file_name):
   protruding_glyphs = []
   glyph_dict = font['glyf'].glyphs
   for glyph_name, glyph in glyph_dict.items():
       if glyph.numberOfContours == 0:
           continue
       if glyph.yMin < ymin or glyph.yMax > ymax:
           protruding_glyphs.append(glyph_name)
   if protruding_glyphs:
       print "Protruding glyphs in %s:" % file_name,
       print ', '.join(sorted(protruding_glyphs))


def drop_lookup(table, lookup_number):
    """Drop a lookup from an OpenType table by number.
    
    Actually remove pointers from features to the lookup, which should be less
    intrusive.
    """
    for feature in table.table.FeatureList.FeatureRecord:
        if lookup_number in feature.Feature.LookupListIndex:
            feature.Feature.LookupListIndex.remove(lookup_number)
            feature.Feature.LookupCount -= 1


def apply_temporary_fixes(font):
    """Apply some temporary fixes needed for Android."""

    # Remove tab, combining keycap, and the arrows from the cmap table
    font_data.delete_from_cmap(font, [0x0009, 0x20E3, 0x2191, 0x2193])
    
    # Drop the lookup forming the ff ligature
    drop_lookup(font['GSUB'], 5)
    
    # Drop tables not useful on Android
    for table in ['LTSH', 'hdmx', 'VDMX', 'gasp']:
        if table in font:
            del font[table]

    # Fix version number from buildnumber.txt
    from datetime import date

    build_number_txt = path.join(
        path.dirname(__file__), os.pardir, 'res', 'buildnumber.txt')
    build_number = open(build_number_txt).read().strip()
    version_record = 'Version 2.0%s; %d' % (build_number, date.today().year)
    for record in font['name'].names:
        if record.nameID == 5:
            if record.platformID == 1 and record.platEncID == 0:  # MacRoman
                record.string = version_record
            elif record.platformID == 3 and record.platEncID == 1:
                # Windows UCS-2
                record.string = version_record.encode('UTF-16BE')
            else:
                assert False


def correct_font(source_font_name, target_font_name):
    """Corrects metrics and other meta information."""
    font = ttLib.TTFont(source_font_name)

    YMAX = 2163
    YMIN = -555
    
    head = font['head']
    head.yMax = YMAX
    head.yMin = YMIN
    output_protruding_glyphs(font, YMIN, YMAX, source_font_name)
    
    hhea = font['hhea']
    hhea.ascent = 1900
    hhea.descent = -500
    hhea.lineGap = 0
    
    basename = path.basename(source_font_name)
    bold = ('Bold' in basename) or ('Black' in basename)
    italic = 'Italic' in basename
    head.macStyle = (italic << 1) | bold
    
    os2 = font['OS/2']
    os2.fsType = 0
    os2.achVendID = 'GOOG'
    
    apply_temporary_fixes(font)
    
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
