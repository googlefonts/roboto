import re
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12
from ufo2fdk import OTFCompiler
from ufo2fdk.makeotfParts import MakeOTFPartsCompiler
from ufo2fdk.outlineOTF import OutlineOTFCompiler


def saveOTF(font, destFile, checkOutlines=False, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    # according to the AGL spec, names of glyphs outside the BMP must have
    # prefix "u" and not "uni": http://sourceforge.net/adobe/aglfn/aglspec
    for glyph in font:
        glyph.name = re.sub(r"uni([\dA-F]{5,})", r"u\1", glyph.name)

    compiler = OTFCompiler(partsCompilerClass=_PartsCompilerBlankGlyphOrder,
                           outlineCompilerClass=_OutlineCompilerFormat12)
    reports = compiler.compile(font, destFile, checkOutlines=checkOutlines,
                               autohint=autohint)
    if checkOutlines:
        print reports["checkOutlines"]
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]


class _PartsCompilerBlankGlyphOrder(MakeOTFPartsCompiler):
    """Child class of parts compiler which produces a blank glyph order file.

    This seems necessary for now because AFDKO's makeotf function produces
    Roboto OTFs without ASCII mappings when called with ufo2fdk's default glyph
    order file.
    """

    def setupFile_glyphOrder(self, path):
        f = open(path, "w")
        f.close()


class _OutlineCompilerFormat12(OutlineOTFCompiler):
    """Child class of outline compiler to work with format 12 cmaps."""

    def setupTable_cmap(self):
        """Set up cmap exactly like ufo2fdk, switching format 4 for 12."""

        # set up a mac-compatible table
        cmap12_0_3 = cmap_format_12(12)
        cmap12_0_3.platformID = 0
        cmap12_0_3.platEncID = 3
        cmap12_0_3.language = 0
        cmap12_0_3.cmap = dict(self.unicodeToGlyphNameMapping)
        # set up a windows-compatible table
        cmap12_3_1 = cmap_format_12(12)
        cmap12_3_1.platformID = 3
        cmap12_3_1.platEncID = 1
        cmap12_3_1.language = 0
        cmap12_3_1.cmap = dict(self.unicodeToGlyphNameMapping)
        # store the tables in the cmap
        self.otf["cmap"] = cmap = newTable("cmap")
        cmap.tableVersion = 0
        cmap.tables = [cmap12_0_3, cmap12_3_1]
