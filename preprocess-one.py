#!/usr/bin/env python3

import cv2
import argparse
from pathlib import Path
import numpy as np

def main():
    parser = argparse.ArgumentParser("convert images to widths and heights of multiples of 4")
    parser.add_argument("in_path", type=str)
    parser.add_argument("out_path", type=str)
    args=parser.parse_args()

    ipath = str(args.in_path)
    opath = str(args.out_path)
    
    img = cv2.imread(ipath, 1)
    if not isinstance(img, np.ndarray):
        print("not an image")
        return
    cols, rows, _ = img.shape
    img = img[:cols-cols%4, :rows-rows%4, :]
    print(f'\tRemoving {cols%4} cols and {rows%4} rows')
    cv2.imwrite(opath, img)

if __name__ == "__main__":
    main()