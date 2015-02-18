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
    r"\[\s*(%s(?:\s+%s)*)\s*\]" % (_classValToken, _classValToken))
_classDef = re.compile(
    r"(%s)\s*=\s*%s\s*;" % (_className.pattern, _classVal.pattern))
_featureDef = re.compile(
    r"(feature\s+(?P<tag>[A-Za-z]{4})\s+\{.*?\}\s+(?P=tag)\s*;)",
    re.DOTALL)
_subRuleToken = r"(?:%s|%s)'?" % (_glyphName, _className.pattern)
_subRuleTokenList =  (
    r"\[?\s*(%s(?:\s+%s)*)\s*\]?" % (_subRuleToken, _subRuleToken))
_subRule = re.compile(
    r"(\s*)sub(?:stitute)?\s+%s\s+by\s+%s\s*;" %
    (_subRuleTokenList, _subRuleTokenList))
_systemDef = re.compile(r"languagesystem\s+([A-Za-z]+)\s+([A-Za-z]+)\s*;")
_comment = re.compile(r"\s*#.*")


def readFeatureFile(font, text):
    """Incorporate valid definitions from feature text into font."""

    readGlyphClasses(font, text)
    text = "\n".join([l for l in text.splitlines() if not _comment.match(l)])

    # filter out substitution rules with invalid references
    errorMsg = "feature definition %s (substitution rule removed)"
    if not hasattr(font.features, "tags"):
        font.features.tags = []
        font.features.values = {}
    for value, tag in _featureDef.findall(text):
        lines = value.splitlines()
        for i in range(len(lines)):
            if _subRule.match(lines[i]):
                indentation, subbed, sub = _subRule.match(lines[i]).groups()
                refs = subbed.split() + sub.split()
                invalid = None
                for ref in refs:
                    if ref[-1] == "'":
                        ref = ref[:-1]
                    if not invalid and not _isValidRef(errorMsg % tag, ref, font):
                        invalid = ref
                if invalid:
                    lines[i] = ("%s; # substitution rule removed for invalid "
                                "reference %s" % (indentation, invalid))
        font.features.tags.append(tag)
        font.features.values[tag] = "\n".join(lines)


def readGlyphClasses(font, text, update=True):
    """Incorporate valid glyph classes from feature text into font."""

    text = "\n".join([l for l in text.splitlines() if not _comment.match(l)])

    # filter out invalid references from glyph class definitions
    errorMsg = "glyph class definition %s (reference removed)"
    if not hasattr(font, "classNames"):
        font.classNames = []
        font.classVals = {}
    for name, value in _classDef.findall(text):
        if name in font.classNames:
            if not update:
                continue
            font.classNames.remove(name)
        refs = value.split()
        refs = [r for r in refs if _isValidRef(errorMsg % name, r, font)]
        font.classNames.append(name)
        font.classVals[name] = " ".join(refs)

    if not hasattr(font, "languageSystems"):
        font.languageSystems = []
    for system in _systemDef.findall(text):
        if system not in font.languageSystems:
            font.languageSystems.append(system)


def _isValidRef(referencer, ref, font):
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


def replaceFeatureFileReferences(font, replace):
    """Replace references according to a given mapping of old names to new."""

    lines = font.features.text.splitlines()
    for i, line in enumerate(lines):

        # check for reference in class definitions
        if _classDef.match(line):
            name, value = _classDef.match(line).groups()
            value = " ".join([replace.get(n, n) for n in value.split()])
            lines[i]= "%s = [%s];" % (name, value)

        # check in substitution rules
        elif _subRule.match(line):
            indentation, subbed, sub = _subRule.match(line).groups()
            subbed = " ".join([replace.get(n, n) for n in subbed.split()])
            sub = " ".join([replace.get(n, n) for n in sub.split()])

            # put brackets around tokens if they were there before
            if re.match(r"\s*sub(stitute)?\s+\[.+\]\s+by", line):
                subbed = "[%s]" % subbed
            if re.match(r"\s*sub(stitute)?.+by\s+\[.+\]\s*;", line):
                sub = "[%s]" % sub
            lines[i] = "%ssub %s by %s;" % (indentation, subbed, sub)

    font.features.text = "\n".join(lines)


def generateFeatureFile(font):
    """Populate a font's feature file text from its classes and features."""

    classes = "\n".join(
        ["%s = [%s];" % (n, font.classVals[n]) for n in font.classNames])
    systems = "\n".join(
        ["languagesystem %s %s;" % (s[0], s[1]) for s in font.languageSystems])
    fea = "\n\n".join([font.features.values[t] for t in font.features.tags])
    font.features.text = "\n\n".join([classes, systems, fea])


def writeFeatureFile(font, path):
    """Write the font's features to an external file."""

    generateFeatureFile(font)
    fout = open(path, "w")
    fout.write(font.features.text)
    fout.close()
