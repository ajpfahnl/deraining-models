#!/bin/bash

# This file should be in the `images` directory and called from the root of the
# repo like so:
#   bash ./images/copy.sh

# This is just an example script for copying files from another dataset directory.
# It assumes the following directory structure:

# dir
#  |--scene_name
#  |   |--image1.png
#  |   |--image2.png
#  |
#  |--Taitung_0-0
#  |   |--Taitung_0-0-Webcam-R-264.png
#  |   |--Taitung_0-0-Webcam-C-000.png
#  |   |--Taitung_0-0-Webcam-P-000.png

# The script also assumes clean images will be concurrently derained, so all images
# are stored in rainy-orig. After removing pseudo-ground-truths (P), the script runs 
# preprocess.py to preprocess the images for the models. The outputs are stored in
# `images/rainy`, and then the `images/clean` directory is removed and recreated as a symlink
# to the `images/rainy` directory

# In essence all images are considered rainy and clean/GTs to themselves.

dir="../video-downloader/CurrentTestSet/"
for scene_dir in ${dir}*/; do
    for img_path in ${scene_dir}*.png; do
        let num=$(python3 -c "s = \"${img_path}\"; n = int(s.split('-')[-1].split('.')[0]); print(n)")
        if (( num < 10 )); then
            echo "copying ${img_path}"
            cp -n ${img_path} ./images/rainy-orig
        fi
    done
done

rm ./images/rainy-orig/*-P-*.png
python3 preprocess.py

( cd images; rm -rf clean; ln -s rainy clean )
