# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from fontmake.font_project import FontProject
from mutatorMath.ufo.document import DesignSpaceDocumentReader
from robofab.world import OpenFont
from ufo2ft.kernFeatureWriter import KernFeatureWriter
from ufo2ft.makeotfParts import FeatureOTFCompiler


class RobotoFontProject(FontProject):

    # glyphs with inconsistent components between masters
    decompose_pre_interpolate = set(['pipedbl', 'pipedblbar', 'uni1AB5'])

    def __del__(self):
        # restore masters if some exception occurs
        self._restore_masters()

    def _pre_interpolate(self, designspace_path):
        # decompose glyphs with both contours and components
        reader = DesignSpaceDocumentReader(designspace_path, ufoVersion=3)
        ufos = [OpenFont(p) for p in reader.getSourcePaths()]

        # first copy original UFO sources to be restored later
        self.original_ufos = [ufo.copy() for ufo in ufos]
        for f in self.original_ufos:
            # make sure everything gets read, so it will all get restored
            for g in f: pass

        # do the decomposition
        def decompose_filter(glyph):
            return ((glyph and glyph.components) or
                    glyph.name in self.decompose_pre_interpolate)
        self.decompose_glyphs(ufos, decompose_filter)

        # write masters for interpolation
        for ufo in ufos:
            ufo.save()
        return designspace_path

    def _pre_compile(self, ufos):
        # undo pre-interpolation changes (decomposition) to UFO sources
        self._restore_masters()

        #TODO append italicized UFOs to list
        return ufos

    def _restore_masters(self):
        if hasattr(self, 'original_ufos'):
            for ufo in self.original_ufos:
                ufo.save()


class RobotoFeatureCompiler(FeatureOTFCompiler):
    def precompile(self):
        self.overwriteFeatures = True

    def setupAnchorPairs(self):
        self.anchorPairs = [
            ["top", "_marktop"],
            ["bottom", "_markbottom"],
            ["top_dd", "_marktop_dd"],
            ["bottom_dd", "_markbottom_dd"],
            ["rhotichook", "_markrhotichook"],
            ["top0315", "_marktop0315"],
            ["parent_top", "_markparent_top"],
            ["parenthesses.w1", "_markparenthesses.w1"],
            ["parenthesses.w2", "_markparenthesses.w2"],
            ["parenthesses.w3", "_markparenthesses.w3"]]

        self.mkmkAnchorPairs = [
            ["mkmktop", "_marktop"],
            ["mkmkbottom_acc", "_markbottom"],

            # By providing a pair with accent anchor _bottom and no base anchor,
            # we designate all glyphs with _bottom as accents (so that they will
            # be used as base glyphs for mkmk features) without generating any
            # positioning rules actually using this anchor (which were instead
            # used to generate composite glyphs). This is all for consistency
            # with older roboto versions.
            ["", "_bottom"],
        ]

        self.ligaAnchorPairs = []


class RobotoKernWriter(KernFeatureWriter):
    leftFeaClassRe = r"@_(.+)_L$"
    rightFeaClassRe = r"@_(.+)_R$"
