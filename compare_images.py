#!/usr/bin/env python3
import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import numpy as np
import argparse
import sys
from pathlib import Path
from tqdm import tqdm

class ImgCompare():
    models = ["MPRNet", "MSPFN", "RCDNet-spa", "RCDNet-rain100h", "SPANet", "ED-v4", "ED-v3"]
    def load_image(self, path):
        img = cv2.imread(path)
        if not isinstance(img, np.ndarray):
            print(f"Couldn't read image from {path}", file=sys.stderr)
        return img
    
    def path_from_stem(self, folder: Path, stem: str):
        return list(folder.glob(f'{stem}.*'))[0]

    def __init__(self, model: str):
        if model not in self.models:
            models_str = ", ".join(self.models)
            print(f"Invalid model: {model}. Please choose from {models_str}")
            exit(1)
        self.model = model

        C_stems = {} # key: name, value: list of stems
        R_stems = {} # key: name, value: stem
        P_stems = {} # key: name, value: stem

        for impath in Path(f'./images/output/{self.model}/').glob('*.png'):
            scene_name, view, _, flag, _= str(impath.name).split('-')
            img_stem = str(impath.stem) # e.g. Taitung_0-0-Webcam-R-264.png
            img_name = "-".join([scene_name, view])

            if flag == 'R':
                if scene_name in R_stems:
                    R_stems[img_name].append(img_stem)
                else:
                    R_stems[img_name] = [img_stem]
            elif flag == 'C':
                C_stems[img_name] = img_stem
            elif flag == 'P':
                P_stems[img_name] = img_stem
            else:
                print(f"Encountered invalid flag for {impath}", file=sys.stderr)
        
        print(f'Will process {len(R_stems)} scenes')

        self.C_stems = C_stems
        self.R_stems = R_stems
        self.P_stems = P_stems

    def find_metrics(self):
        avg_psnr_rainy_gt = 0
        avg_psnr_derained_gt = 0
        avg_ssim_rainy_gt = 0
        avg_ssim_derained_gt = 0
        count = 0

        for name in self.R_stems:
            for stem in tqdm(self.R_stems[name]):
                rainy_path = self.path_from_stem(Path('./images/rainy/'), stem)
                derained_path = self.path_from_stem(Path(f'./images/output/{self.model}/'), stem)
                clean_path = self.path_from_stem(Path('./images/rainy/'), self.C_stems[name])

                clean_img = self.load_image(str(clean_path))
                rainy_img = self.load_image(str(rainy_path))
                derained_img = self.load_image(str(derained_path))

                avg_psnr_rainy_gt += cv2.PSNR(clean_img, rainy_img)
                avg_psnr_derained_gt += cv2.PSNR(clean_img, derained_img)
                avg_ssim_rainy_gt += ssim(clean_img, rainy_img, multichannel=True)
                avg_ssim_derained_gt += ssim(clean_img, derained_img, multichannel=True)
                count += 1
                break
        avg_psnr_rainy_gt /= count
        avg_psnr_derained_gt /= count
        avg_ssim_rainy_gt /= count
        avg_ssim_derained_gt /= count
        print(f"                 PSNR    SSIM")
        print(f"Rainy vs. GT:    {avg_psnr_rainy_gt:.2f}    {avg_ssim_rainy_gt:.2f}")
        print(f"Derained vs. GT: {avg_psnr_derained_gt:.2f}    {avg_ssim_derained_gt:.2f}")

if __name__ == "__main__":
    models_str = ", ".join(ImgCompare.models)
    parser = argparse.ArgumentParser(description='Compare with PSNR and SSIM')
    parser.add_argument('model', type=str, help=f'Model whose outputs to test. Choose from {models_str}')
    args = parser.parse_args()

    ic = ImgCompare(args.model)
    ic.find_metrics()

