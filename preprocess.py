#!/usr/bin/env python3

import cv2
import argparse
from pathlib import Path
import numpy as np

def main():
    # parser = argparse.ArgumentParser("convert images to widths and heights of multiples of 4")
    # parser.add_argument('--rainy-only', action='store_true', help='convert only rainy images')
    
    img_orig_dirs = ['./images/clean-orig', './images/rainy-orig']
    img_orig_dirs = [Path(d) for d in img_orig_dirs]

    img_out_dirs = ['./images/clean', './images/rainy']
    img_out_dirs = [Path(d) for d in img_out_dirs]

    for img_orig_dir, img_out_dir in zip(img_orig_dirs, img_out_dirs):
        p = img_orig_dir.glob('*')
        for img_path in p:
            print(img_path)
            img = cv2.imread(str(img_path), 1)
            if not isinstance(img, np.ndarray):
                continue
            cols, rows, _ = img.shape
            img = img[:cols-cols%4, :rows-rows%4, :]
            print(f'\tRemoving {cols%4} cols and {rows%4} rows')
            cv2.imwrite(str(img_out_dir / (img_path.stem+".png")), img)

if __name__ == "__main__":
    main()