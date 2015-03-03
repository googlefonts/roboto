def saveOTF(font, destFile, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    from ufo2fdk import OTFCompiler

    # glyphs with multiple unicode values must be split up, due to FontTool's
    # use of a name -> UV dictionary during cmap compilation
    for glyph in font:
        if len(glyph.unicodes) > 1:
            newUV = glyph.unicodes.pop()
            newGlyph = font.newGlyph("uni%04X" % newUV)
            newGlyph.appendComponent(glyph.name)
            newGlyph.unicode = newUV
            newGlyph.width = glyph.width

    compiler = OTFCompiler()
    reports = compiler.compile(font, destFile, autohint=autohint)
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]
