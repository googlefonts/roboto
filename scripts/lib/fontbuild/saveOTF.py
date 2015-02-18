import re

from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12
from ufo2fdk import OTFCompiler
from ufo2fdk.makeotfParts import MakeOTFPartsCompiler
from ufo2fdk.outlineOTF import OutlineOTFCompiler

from fontbuild.features import replaceFeatureFileReferences


def saveOTF(font, destFile, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    compiler = OTFCompiler(partsCompilerClass=_PartsCompilerCustomGlyphOrder,
                           outlineCompilerClass=_OutlineCompilerFormat12)
    reports = compiler.compile(font, destFile, autohint=autohint)
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]


def conformToAGL(font, glyphList):
    """Ensure a font's glyph names conform to the AGL specification.

    The spec is described at http://sourceforge.net/adobe/aglfn/aglspec.
    This function only checks for some Roboto-specific problems.
    """

    nameChanges = {}
    for glyph in font:
        name_components = glyph.name.split(".")
        name = name_components.pop(0)
        ext = ("." + name_components[0]) if name_components else ""
        if name in glyphList:
            continue

        # if a ligature name (without underscores) is in the AGL, remove the
        # underscores so AFDKO will keep the glyph in the font during conversion
        #TODO(jamesgk) figure out why AFDKO throws out names with underscores
        if re.match("([a-z]_)+[a-z]", name):
            ligaName = name.replace("_", "") + ext
            if ligaName in glyphList:
                nameChanges[glyph.name] = ligaName
                continue

        # use the glyph's unicode value as its name, if possible
        if not re.match(r"u(ni)?[\dA-F]+", glyph.name) and glyph.unicode:
            uvName = ("uni%04X" % glyph.unicode) + ext
            nameChanges[glyph.name] = uvName

        # names of glyphs outside the BMP must have prefix "u" and not "uni"
        if re.match(r"uni[\dA-F]{5,}", glyph.name):
            nameChanges[glyph.name] = re.sub("^uni", "u", glyph.name)

    for oldName, newName in nameChanges.items():
        font[oldName].name = newName
    replaceFeatureFileReferences(font, nameChanges)


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
