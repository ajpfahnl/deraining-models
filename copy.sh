#!/bin/bash
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
python3 imgto4.py

( cd images; rmdir clean; ln -s rainy clean )
