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

FONTDIR=$(dirname $0)/../src/hinted

input_file=$1

function render {
 cat $input_file | $HARFBUZZ/util/hb-view --font-file=$1 --output-format=png --output-file=$2.png --font-size=200
}

render $FONTDIR/Roboto-Thin.ttf 100
render $FONTDIR/Roboto-Light.ttf 300
render $FONTDIR/Roboto-Regular.ttf 400
render $FONTDIR/Roboto-Medium.ttf 500
render $FONTDIR/Roboto-Bold.ttf 700
render $FONTDIR/Roboto-Black.ttf 900

render $FONTDIR/Roboto-ThinItalic.ttf i100
render $FONTDIR/Roboto-LightItalic.ttf i300
render $FONTDIR/Roboto-Italic.ttf i400
render $FONTDIR/Roboto-MediumItalic.ttf i500
render $FONTDIR/Roboto-BoldItalic.ttf i700
render $FONTDIR/Roboto-BlackItalic.ttf i900

render $FONTDIR/RobotoCondensed-Light.ttf c300
render $FONTDIR/RobotoCondensed-Regular.ttf c400
render $FONTDIR/RobotoCondensed-Bold.ttf c700

render $FONTDIR/RobotoCondensed-LightItalic.ttf ci300
render $FONTDIR/RobotoCondensed-Italic.ttf ci400
render $FONTDIR/RobotoCondensed-BoldItalic.ttf ci700

eog *.png

