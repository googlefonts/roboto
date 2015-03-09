import re

from feaTools import parser
from feaTools.writers.fdkSyntaxWriter import FDKSyntaxFeatureWriter


# fix some regular expressions used by feaTools
# we may want to push these fixes upstream
# allow dashes in glyph class content, for glyph ranges
parser.classDefinitionRE = re.compile(
        "([\s;\{\}]|^)"        # whitepace, ; {, } or start of line
        "@"                    # @
        "([\w\d_.]+)"          # name
        "\s*=\s*"              #  = 
        "\["                   # [
        "([\w\d\s\-_.@]+)"     # content
        "\]"                   # ]
        "\s*;"                 # ;
        , re.M
        )
parser.classContentRE = re.compile(
        "([\w\d\-_.@]+)"
        )

# allow apostrophes in feature/lookup content
parser.sequenceInlineClassRE = re.compile(
        "\["                   # [
        "([\w\d\s_.@']+)"      # content
        "\]"                   # ]
        )

# allow apostrophes in the target and replacement of a substitution
parser.subType1And4RE = re.compile(
        "([\s;\{\}]|^)"        # whitepace, ; {, } or start of line
        "substitute|sub\s+"    # sub
        "([\w\d\s_.@\[\]']+)"  # target
        "\s+by\s+"             #  by
        "([\w\d\s_.@\[\]']+)"  # replacement
        "\s*;"                 # ;
        )

# don't be greedy when matching feature/lookup content (may be duplicates)
parser.featureContentRE[3] = parser.featureContentRE[3].replace('*', '*?')
parser.lookupContentRE[3] = parser.lookupContentRE[3].replace('*', '*?')


class FilterFeatureWriter(FDKSyntaxFeatureWriter):
    """Feature writer to detect invalid references and duplicate definitions."""

    def __init__(self, refs=set(), name=None, isFeature=False):
        """Initializes the set of known references, empty by default."""
        self.refs = refs
        self.featureNames = set()
        self.lookupNames = set()
        self.languageSystems = set()
        super(FilterFeatureWriter, self).__init__(
            name=name, isFeature=isFeature)

        # error to print when undefined reference is found in glyph class
        self.classErr = ('Undefined reference "%s" removed from glyph class '
            'definition %s.')

        # error to print when undefined reference is found in sub or pos rule
        subErr = ['Substitution rule with undefined reference "%s" removed']
        if self._name:
            subErr.append(" from ")
            subErr.append("feature" if self._isFeature else "lookup")
            subErr.append(' "%s"' % self._name)
        subErr.append(".")
        self.subErr = "".join(subErr)
        self.posErr = self.subErr.replace("Substitution", "Positioning")

    def _subwriter(self, name, isFeature):
        """Use this class for nested expressions e.g. in feature definitions."""
        return FilterFeatureWriter(self.refs, name, isFeature)

    def _checkRefs(self, refs, errorMsg):
        """Check a list of references found in a sub or pos rule."""
        for ref in refs:
            # trailing apostrophes should be ignored
            if ref[-1] == "'":
                ref = ref[:-1]
            if ref not in self.refs:
                print errorMsg % ref
                # insert an empty instruction so that we can't end up with an
                # empty block, which is illegal syntax
                super(FilterFeatureWriter, self).rawText(";")
                return False
        return True

    def classDefinition(self, name, contents):
        """Check that contents are valid, then add name to known references."""
        if name in self.refs:
            return
        newContents = []
        for ref in contents:
            if ref not in self.refs and ref != "-":
                print self.classErr % (ref, name)
            else:
                newContents.append(ref)
        self.refs.add(name)
        super(FilterFeatureWriter, self).classDefinition(name, newContents)

    def gsubType1(self, target, replacement):
        """Check a sub rule with one-to-one replacement."""
        if type(target) == str:
            target, replacement = [target], [replacement]
        if self._checkRefs(target + replacement, self.subErr):
            super(FilterFeatureWriter, self).gsubType1(target, replacement)

    def gsubType4(self, target, replacement):
        """Check a sub rule with many-to-one replacement."""
        if self._checkRefs(target + [replacement], self.subErr):
            super(FilterFeatureWriter, self).gsubType4(target, replacement)

    def gposType1(self, target, value):
        """Check a positioning rule."""
        if self._checkRefs([target], self.posErr):
            super(FilterFeatureWriter, self).gposType1(target, value)

    # these rules may contain references, but they aren't present in Roboto
    def gsubType3(self, target, replacement):
        raise NotImplementedError
    def gsubType6(self, precedingContext, target, trailingContext, replacement):
        raise NotImplementedError
    def gposType2(self, target, value):
        raise NotImplementedError

    def feature(self, name):
        """Adds a feature definition only once."""
        if name not in self.featureNames:
            self.featureNames.add(name)
            return super(FilterFeatureWriter, self).feature(name)
        # we must return a new writer even if we don't add it to this one
        return FDKSyntaxFeatureWriter(name, True)

    def lookup(self, name):
        """Adds a lookup block only once."""
        if name not in self.lookupNames:
            self.lookupNames.add(name)
            return super(FilterFeatureWriter, self).lookup(name)
        # we must return a new writer even if we don't add it to this one
        return FDKSyntaxFeatureWriter(name, False)

    def languageSystem(self, langTag, scriptTag):
        """Adds a language system instruction only once."""
        system = (langTag, scriptTag)
        if system not in self.languageSystems:
            self.languageSystems.add(system)
            super(FilterFeatureWriter, self).languageSystem(langTag, scriptTag)


def compileFeatureRE(name):
    """Compiles a feature-matching regex."""

    # this is the pattern used internally by feaTools:
    # https://github.com/typesupply/feaTools/blob/master/Lib/feaTools/parser.py
    featureRE = list(parser.featureContentRE)
    featureRE.insert(2, name)
    featureRE.insert(6, name)
    return re.compile("".join(featureRE))


def updateFeature(font, name, value):
    """Add a feature definition, or replace existing one."""
    featureRE = compileFeatureRE(name)
    if featureRE.search(font.features.text):
        font.features.text = featureRE.sub(value, font.features.text)
    else:
        font.features.text += "\n" + value


def readFeatureFile(font, text):
    """Incorporate valid definitions from feature text into font."""
    writer = FilterFeatureWriter(set(font.keys()))
    parser.parseFeatures(writer, text + font.features.text)
    font.features.text = writer.write()


def writeFeatureFile(font, path):
    """Write the font's features to an external file."""
    fout = open(path, "w")
    fout.write(font.features.text)
    fout.close()
