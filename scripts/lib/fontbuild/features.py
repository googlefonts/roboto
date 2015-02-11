"""Functions for parsing and validating RoboFab RFont feature files."""


import re


# feature file syntax rules from:
# http://www.adobe.com/devnet/opentype/afdko/topic_feature_file_syntax.html
_glyphNameChars = r"[A-Za-z_][\w.]"
_glyphName = r"%s{,30}" % _glyphNameChars
_className = re.compile(r"@%s{,29}" % _glyphNameChars)
_classValToken = (
    r"(?:%s|%s(?:\s*-\s*%s)?)" % (_className.pattern, _glyphName, _glyphName))
_classVal = re.compile(
    r"\[(\s*%s(?:\s+%s)*)\s*\]" % (_classValToken, _classValToken))
_classDef = re.compile(
    r"(%s)\s*=\s*%s;" % (_className.pattern, _classVal.pattern))
_featureDef = re.compile(
    r"(feature\s+(?P<tag>[A-Za-z]{4})\s+\{.*?\}\s+(?P=tag)\s*;\s*?\n)",
    re.DOTALL)
_systemDef = re.compile(r"languagesystem\s+([A-Za-z]+)\s+([A-Za-z]+)\s*;")
_comment = re.compile(r"\s*#.*")


def readFeatureFile(font, text):
    """Incorporate valid definitions from feature text into font."""

    readGlyphClasses(font, text)
    lines = [l for l in re.split(r"[\r\n]+", text) if not _comment.match(l)]
    text = "\n".join(lines)

    errorMsg = "feature definition %s (definition removed)"
    if not hasattr(font.features, "tags"):
        font.features.tags = []
        font.features.values = {}
    for value, tag in _featureDef.findall(text):
        valid = True
        for reference in _className.findall(value):
            valid = valid and _isValidReference(errorMsg % tag, reference, font)
        for referenceList in _classVal.findall(value):
            for ref in referenceList.split():
                valid = valid and _isValidReference(errorMsg % tag, ref, font)
        if valid:
            font.features.tags.append(tag)
            font.features.values[tag] = value


def readGlyphClasses(font, text, update=True):
    """Incorporate valid glyph classes from feature text into font."""

    lines = [l for l in re.split(r"[\r\n]+", text) if not _comment.match(l)]
    text = "\n".join(lines)

    errorMsg = "glyph class definition %s (reference removed)"
    if not hasattr(font, "classNames"):
        font.classNames = []
        font.classVals = {}
    for name, value in _classDef.findall(text):
        if name in font.classNames:
            if not update:
                continue
            font.classNames.remove(name)
        validRefs = []
        for reference in value.split():
            if _isValidReference(errorMsg % name, reference, font):
                validRefs.append(reference)
        value = " ".join(validRefs)
        font.classNames.append(name)
        font.classVals[name] = value

    if not hasattr(font, "languageSystems"):
        font.languageSystems = []
    for system in _systemDef.findall(text):
        if system not in font.languageSystems:
            font.languageSystems.append(system)


def _isValidReference(referencer, ref, font):
    """Check if a reference is valid for a font."""

    if ref.startswith("@"):
        if not font.classVals.has_key(ref):
            print "Undefined class %s referenced in %s." % (ref, referencer)
            return False
    else:
        for r in ref.split("-"):
            if r and not font.has_key(r):
                print "Undefined glyph %s referenced in %s." %  (r, referencer)
                return False
    return True


def generateFeatureFile(font):
    """Populate a font's feature file text from its classes and features."""

    classes = "\n".join(
        ["%s = [%s];" % (n, font.classVals[n]) for n in font.classNames])
    systems = "\n".join(
        ["languagesystem %s %s;" % (s[0], s[1]) for s in font.languageSystems])
    features = "\n".join([font.features.values[t] for t in font.features.tags])
    font.features.text = "\n\n".join([classes, systems, features])


def writeFeatureFile(font, path):
    """Write the font's features to an external file."""

    generateFeatureFile(font)
    fout = open(path, "w")
    fout.write(font.features.text)
    fout.close()
