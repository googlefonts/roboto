from ufo2fdk import OTFCompiler


def saveOTF(font, destFile, autohint=False):
    """Save a RoboFab font as an OTF binary using ufo2fdk."""

    compiler = OTFCompiler()
    reports = compiler.compile(font, destFile, autohint=autohint)
    if autohint:
        print reports["autohint"]
    print reports["makeotf"]
