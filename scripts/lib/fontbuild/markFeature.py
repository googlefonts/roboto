# Copyright 2015 Google Inc. All Rights Reserved.
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


from ufo2ft.kernFeatureWriter import KernFeatureWriter
from ufo2ft.makeotfParts import FeatureOTFCompiler


class RobotoFeatureCompiler(FeatureOTFCompiler):
    def precompile(self):
        self.overwriteFeatures = True

    def setupAnchorPairs(self):
        self.anchorPairs = [
            ["top", "_marktop", True, True],
            ["bottom", "_markbottom", True, True],
            ["top_dd", "_marktop_dd", True, False],
            ["bottom_dd", "_markbottom_dd", True, False],
            ["rhotichook", "_markrhotichook", False, False],
            ["top0315", "_marktop0315", False, False],
            ["parent_top", "_markparent_top", False, False],
            ["parenthesses.w1", "_markparenthesses.w1", False, False],
            ["parenthesses.w2", "_markparenthesses.w2", False, False],
            ["parenthesses.w3", "_markparenthesses.w3", False, False]]

        self.mkmkAnchorPairs = [
            ["mkmktop", "_marktop"],
            ["mkmkbottom_acc", "_markbottom"]]

    def setupAliases(self):
        self.aliases = [
            ["a", "uni0430"], ["e", "uni0435"], ["p", "uni0440"],
            ["c", "uni0441"], ["x", "uni0445"], ["s", "uni0455"],
            ["i", "uni0456"], ["psi", "uni0471"]]


class RobotoKernWriter(KernFeatureWriter):
    leftFeaClassRe = r"@_(.+)_L$"
    rightFeaClassRe = r"@_(.+)_R$"
