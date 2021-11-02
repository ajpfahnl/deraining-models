#!/usr/bin/env python3
import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import numpy as np
import argparse
import sys
from pathlib import Path
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

class ImgCompare():
    models = ["MPRNet", "MSPFN", "RCDNet-spa", "RCDNet-rain100h", "SPANet", "ED-v4", "ED-v3"]
    def load_image(self, path):
        img = cv2.imread(path)
        if not isinstance(img, np.ndarray):
            print(f"Couldn't read image from {path}", file=sys.stderr)
        return img
    
    def path_from_stem(self, folder: Path, stem: str):
        return list(folder.glob(f'{stem}*'))[0]

    def __init__(self, model: str, single: bool=False, progress_func=tqdm):
        if model not in self.models:
            models_str = ", ".join(self.models)
            print(f"Invalid model: {model}. Please choose from {models_str}")
            exit(1)
        self.model = model
        self.single = single
        self.progress_func = progress_func

        C_stems = {} # key: name, value: list of stems
        R_stems = {} # key: name, value: stem
        P_stems = {} # key: name, value: stem

        for impath in Path(f'./images/output/{self.model}/').glob('*.png'):
            scene_name, view, _, flag, _= str(impath.name).split('-')
            img_stem = str(impath.stem) # e.g. Taitung_0-0-Webcam-R-264.png
            img_name = "-".join([scene_name, view])

            if flag == 'R':
                if img_name in R_stems:
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

    def print_metrics(self, metrics):
        avg_psnr_rainy_gt, avg_psnr_derained_gt, avg_ssim_rainy_gt, avg_ssim_derained_gt = metrics
        print(f"                 PSNR    SSIM")
        print(f"Rainy vs. GT:    {avg_psnr_rainy_gt:.2f}    {avg_ssim_rainy_gt:.2f}")
        print(f"Derained vs. GT: {avg_psnr_derained_gt:.2f}    {avg_ssim_derained_gt:.2f}")


    def find_metrics(self, display_groups=False):
        print("Will display first and last image groupings for each scene")

        # intialize average metrics for all scenes
        metrics = np.zeros(4)
        count = 0

        for name in sorted(self.R_stems):

            # initialize metrics for one scene
            metrics_scene = np.zeros(4)
            count_scene = 0

            print(f'Processing {name}')
            clean_path = self.path_from_stem(Path('./images/rainy/'), self.C_stems[name])

            for stem in self.progress_func(self.R_stems[name]):
                count += 1
                count_scene += 1

                rainy_path = self.path_from_stem(Path('./images/rainy/'), stem)
                derained_path = self.path_from_stem(Path(f'./images/output/{self.model}/'), stem)

                clean_img = self.load_image(str(clean_path))
                rainy_img = self.load_image(str(rainy_path))
                derained_img = self.load_image(str(derained_path))

                metrics_scene[0] += cv2.PSNR(clean_img, rainy_img)
                metrics_scene[1] += cv2.PSNR(clean_img, derained_img)
                metrics_scene[2] += ssim(clean_img, rainy_img, multichannel=True)
                metrics_scene[3] += ssim(clean_img, derained_img, multichannel=True)

                if display_groups and count_scene in [1, len(self.R_stems[name])]:
                    plt.imshow(np.hstack((clean_img, rainy_img, derained_img)))
                    plt.show()
                if self.single:
                    break
            metrics_scene /= count_scene
            print(f'Metrics for scene {name}')
            self.print_metrics(metrics_scene)

            # update overall metrics
            metrics += metrics_scene
        
        metrics /= count
        print('####################')
        print('OVERALL')
        self.print_metrics(metrics)
        print('####################')

if __name__ == "__main__":
    models_str = ", ".join(ImgCompare.models)
    parser = argparse.ArgumentParser(description='Compare with PSNR and SSIM')
    parser.add_argument('model', type=str, help=f'Model whose outputs to test. Choose from {models_str}')
    parser.add_argument('--single', action='store_true', help=f'Only process one image from each scene')
    parser.add_argument('--display', action='store_true', help=f'Display first and last image groupings for each scene')
    args = parser.parse_args()

    ic = ImgCompare(args.model, args.single)
    ic.find_metrics(display_groups=args.display)
