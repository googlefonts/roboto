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


import os
import roboto_font_project

# The root of the Roboto tree
BASEDIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))

project = roboto_font_project.RobotoFontProject()
srcdir = os.path.join(BASEDIR, 'src', 'v2')
for family in ('Roboto', 'RobotoCondensed'):
    designspace_path = os.path.join(srcdir, '%s.designspace' % family)
    project.run_from_designspace(
        designspace_path, output=('ufo', 'otf', 'ttf'), interpolate=True,
        conversion_error=0.002, use_production_names=False,
        fea_compiler=roboto_font_project.RobotoFeatureCompiler,
        kern_writer=roboto_font_project.RobotoKernWriter)
