import re


className = re.compile(r"@[\w\.]+")
classVal = re.compile(r"\[(\s*(?:[\w\.-]+\s*)+)\]")
classDef = re.compile(
    r"(%s)\s*?=\s*?%s;" % (className.pattern, classVal.pattern))
featureDef = re.compile(
    r"(feature (?P<tag>[A-Za-z]{4}) \{.*?\} (?P=tag);\n)", re.DOTALL)
comment = re.compile(r"\s*#.*")


def validateFeatureFile(font):
    """Remove invalid features and glyph/class references from an RFont."""

    classes, text = validateGlyphClasses(font, font.features.text)
    for feature, name in featureDef.findall(text):
        remove = False
        for reference in className.findall(feature):
            if reference not in classes:
                print ("Undefined glyph class %s referenced in feature "
                       "definition %s (removed)." % (reference, name))
                remove = True
        for references in classVal.findall(feature):
            for reference in references.split():
                if "-" not in reference and not font.has_key(reference):
                    print ("Undefined glyph %s referenced in feature "
                           "definition %s (removed)." % (reference, name))
                    remove = True
        if remove:
            text = text.replace(feature, "")
    font.features.text = text


def validateGlyphClasses(font, text):
    """Parse glyph classes from feature text, removing invalid references."""

    classes = set()
    validLines = []
    for line in [l for l in re.split(r"[\r\n]+", text) if not comment.match(l)]:
        match = classDef.match(line)
        if match:
            name, references = match.groups()
            classes.add(name)

            validRefs = []
            for reference in references.split():
                if reference.startswith("@") and reference not in classes:
                    print ("Undefined glyph class %s referenced in glyph class "
                           "definition %s (removed)." % (reference, name))
                elif "-" not in reference and not font.has_key(reference):
                    print ("Undefined glyph %s referenced in glyph class "
                           "definition %s (removed)." % (reference, name))
                else:
                    validRefs.append(reference)

            line = "%s = [%s];" % (name, " ".join(validRefs))
        validLines.append(line)

    return classes, "\n".join(validLines)


def CreateFeaFile(font, path):
	fea_text = font.ot_classes
	for cls in font.classes:
		text = "@" + cls + "];\n"
		text = string.replace(text, ":", "= [")
		text = string.replace(text, "\'", "")
		fea_text += text	
	for fea in font.features:
		fea_text += fea.value
	fea_text = string.replace(fea_text, "\r\n", "\n")	
	fout = open(path, "w")
	fout.write(fea_text)
	fout.close()