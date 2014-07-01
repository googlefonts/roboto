#!/usr/bin/python
"""Post-build touch ups for Roboto."""

from os import path
import sys

from fontTools import ttLib
from nototools import font_data


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

    # Fix version to 2.000981
    version_record = 'Version 2.000981; 2014'
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
    
    head = font['head']
    head.yMax = 2163
    head.yMin = -555
    
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
    """Correct all fonts specified in the command line."""
    for font_name in argv[1:]:
        correct_font(font_name, path.basename(font_name))


if __name__ == "__main__":
    main(sys.argv)
