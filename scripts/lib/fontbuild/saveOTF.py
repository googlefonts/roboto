from ufo2fdk import OTFCompiler
from ufo2fdk.makeotfParts import MakeOTFPartsCompiler


def saveOTF(font, destFile, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    compiler = OTFCompiler(partsCompilerClass=_PartsCompilerCustomGlyphOrder)
    reports = compiler.compile(font, destFile, autohint=autohint)
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]


class _PartsCompilerCustomGlyphOrder(MakeOTFPartsCompiler):
    """OTF parts compiler that produces a custom glyph order file."""

    def setupFile_glyphOrder(self, path):
        # fixes: https://github.com/typesupply/ufo2fdk/pull/3
        lines = []
        for name in self.glyphOrder:
            if name in self.font and self.font[name].unicode is not None:
                code = "%04X" % self.font[name].unicode
                if len(code) <= 4:
                    code = "uni%s" % code
                else:
                    code = "u%s" % code
                line = "%s %s %s" % (name, name, code)
            else:
                line = "%s %s" % (name, name)
            lines.append(line)
        ofile = open(path, "wb")
        ofile.write("\n".join(lines) + "\n")
        ofile.close()
