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


from FL import *

import json
import os


def main():
    """Extract anchors which will be dropped during conversion via vfb2ufo.

    Specifically, these are the anchors belonging to glyphs containing
    components but no contours. This script exports them to json files.
    """

    path = ""  # CHANGE THIS TO LOCAL ROBOTO PATH
    if not path:
        print "Please change the 'path' variable to your local roboto location"
        return

    # list of input fonts (master VFBs) with their respective weights
    fonts = (
        (os.path.join(path, "src", "v2", "Roboto_Thin.vfb"), "thin"),
        (os.path.join(path, "src", "v2", "Roboto_Regular.vfb"), "regular"),
        (os.path.join(path, "src", "v2", "Roboto_Bold.vfb"), "bold"))

    # extract the anchors which will be dropped
    for fontpath, weight in fonts:
        fontData = {}
        font = Font(fontpath)
        for i in range(len(font)):
            glyph = font[i]
            if glyph.anchors and glyph.components and not glyph.nodes:
                glyphData = {}
                for anchor in glyph.anchors:
                    glyphData[anchor.name] = [anchor.x, anchor.y]
                fontData[glyph.name] = glyphData

        # write the data as json
        outpath = os.path.join(path, "res", "anchors_%s.json" % weight)
        with open(outpath, "w") as outfile:
            json.dump(fontData, outfile, sort_keys=True, indent=2,
                      separators=(',', ': '))
            print "Wrote " + outpath
    print "Done"


main()
