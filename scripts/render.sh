#!/bin/bash
#
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

HARFBUZZ=$HOME/harfbuzz

input_file=$1

function render {
 cat $input_file | $HARFBUZZ/util/hb-view --font-file=$1 --output-format=png --output-file=$2.png
}

render ../hinted/Roboto-Thin.ttf 100
render ../hinted/Roboto-Light.ttf 300
render ../hinted/Roboto-Regular.ttf 400
render ../hinted/Roboto-Medium.ttf 500
render ../hinted/Roboto-Bold.ttf 700
render ../hinted/Roboto-Black.ttf 900

render ../hinted/Roboto-ThinItalic.ttf i100
render ../hinted/Roboto-LightItalic.ttf i300
render ../hinted/Roboto-Italic.ttf i400
render ../hinted/Roboto-MediumItalic.ttf i500
render ../hinted/Roboto-BoldItalic.ttf i700
render ../hinted/Roboto-BlackItalic.ttf i900

render ../hinted/RobotoCondensed-Light.ttf c300
render ../hinted/RobotoCondensed-Regular.ttf c400
render ../hinted/RobotoCondensed-Bold.ttf c700

render ../hinted/RobotoCondensed-LightItalic.ttf ci300
render ../hinted/RobotoCondensed-Italic.ttf ci400
render ../hinted/RobotoCondensed-BoldItalic.ttf ci700

eog *.png

