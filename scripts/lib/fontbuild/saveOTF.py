import re
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12
from ufo2fdk import OTFCompiler
from ufo2fdk.makeotfParts import MakeOTFPartsCompiler
from ufo2fdk.outlineOTF import OutlineOTFCompiler


def saveOTF(font, destFile, checkOutlines=False, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    compiler = OTFCompiler(partsCompilerClass=_PartsCompilerCustomGlyphOrder,
                           outlineCompilerClass=_OutlineCompilerFormat12)
    reports = compiler.compile(font, destFile, checkOutlines=checkOutlines,
                               autohint=autohint)
    if checkOutlines:
        print reports["checkOutlines"]
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]


def conformToAGL(font, glyphList):
    """Ensure a font's glyph names conform to the AGL specification.

    The spec is described at http://sourceforge.net/adobe/aglfn/aglspec.
    This function only checks for some Roboto-specific problems.
    """

    ligaNameChanges = {}
    for glyph in font:
        if glyph.name in glyphList:
            continue

        # if a ligature name (without underscores) is in the AGL, remove the
        # underscores so AFDKO will keep the glyph in the font during conversion
        #TODO(jamesgk) figure out why AFDKO throws out names with underscores
        if re.match("([a-z]_)+[a-z]", glyph.name):
            ligaName = glyph.name.replace("_", "")
            if ligaName in glyphList:
                ligaNameChanges[glyph.name] = ligaName
                glyph.name = ligaName
                continue

        # names of glyphs outside the BMP must have prefix "u" and not "uni"
        glyph.name = re.sub(r"^uni([\dA-F]{5,})$", r"u\1", glyph.name)

    # references to altered ligature names must be updated in the font features
    #TODO(jamesgk) use a more robust system for parsing through RFont features
    for oldName, newName in ligaNameChanges.iteritems():
        font.features.text = font.features.text.replace(oldName, newName)


class _PartsCompilerCustomGlyphOrder(MakeOTFPartsCompiler):
    """OTF parts compiler that produces a custom glyph order file."""

    def setupFile_glyphOrder(self, path):
        # just create a blank file -- this seems necessary for now because
        # AFDKO's makeotf function produces Roboto OTFs without ASCII mappings
        # when called with ufo2fdk's default glyph order file
        #TODO(jamesgk) figure out why this is necessary
        f = open(path, "w")
        f.close()


class _OutlineCompilerFormat12(OutlineOTFCompiler):
    """OTF outline compiler to work with format 12 cmaps."""

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
