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

project = roboto_font_project.RobotoFontProject(BASEDIR)
srcdir = os.path.join(BASEDIR, 'src', 'v2')

class_values = (
    ('Roboto', 'Thin', 250),
    ('Roboto', 'Light', 300),
    ('Roboto', 'Regular', 400),
    ('Roboto', 'Medium', 500),
    ('Roboto', 'Bold', 700),
    ('Roboto', 'Black', 900),
    ('RobotoCondensed', 'Light', 300),
    ('RobotoCondensed', 'Regular', 400),
    ('RobotoCondensed', 'Bold', 700),
)
instance_data = {'Roboto': [], 'RobotoCondensed': []}
for family, style, weight_class in class_values:
    instance_data[family].append((
        os.path.join('instance_ufo', '%s-%s.ufo' % (family, style)),
        {'customParameters': [{'name': 'weightClass', 'value': weight_class}]}))

for family in ('Roboto', 'RobotoCondensed'):
    designspace_path = os.path.join(srcdir, '%s.designspace' % family)
    project.run_from_designspace(
        designspace_path, output=('ufo', 'otf', 'ttf'), interpolate=True,
        instance_data=instance_data[family], conversion_error=0.002,
        use_production_names=False,
        fea_compiler=roboto_font_project.RobotoFeatureCompiler,
        kernWriter=roboto_font_project.RobotoKernWriter)
