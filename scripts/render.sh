#!/bin/bash

HARFBUZZ=$HOME/harfbuzz

function render {
 echo weT͟Hər | $HARFBUZZ/util/hb-view --font-file=$1 --output-format=png --output-file=$2.png
}

render ../out/RobotoTTF/Roboto-Regular.ttf original
render Roboto-Regular.ttf modified

eog *.png

