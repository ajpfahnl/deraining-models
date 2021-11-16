#!/usr/bin/env python3
import cv2
import matplotlib.pyplot as plt
from numpy.lib.arraysetops import isin
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import numpy as np
import argparse
import sys
from pathlib import Path
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import re

class ImgCompare():
    models = ["MPRNet", "MSPFN", "RCDNet-spa", "RCDNet-rain100h", "SPANet", "ED-v4", "ED-v3", "HRR", "DGNL", "ED-v3rain100h", "ED-v4rain100h", "ED-v3rain1400", "ED-v4rain1400"]
    clean_opts = ["one", "one2one"]

    def load_image(self, path):
        img = cv2.imread(path)
        if not isinstance(img, np.ndarray):
            print(f"Couldn't read image from {path}", file=sys.stderr)
        return img
    
    def path_from_stem(self, folder: Path, stem: str):
        return list(folder.glob(f'{stem}*'))[0]

    def __init__(self, model: str, single: bool=False, progress_func=tqdm, particulars=None, clean="one"):
        '''
        clean option can be "one" or "one2one"
        '''
        if model not in self.models:
            models_str = ", ".join(self.models)
            print(f"Invalid model: {model}. Please choose from {models_str}")
            exit(1)
        if clean not in ["one", "one2one"]:
            clean_opts_str = ", ".join(self.clean_opts)
            print(f"Invalid clean option. Please choose from {clean_opts_str}")
        
        self.model = model
        self.clean = clean
        self.single = single
        self.progress_func = progress_func

        C_stems = {} # key: name, value: list of stems
        R_stems = {} # key: name, value: stem
        P_stems = {} # key: name, value: stem

        prog = re.compile(".*-[0-9]*-.*-[RCP]-[0-9]*")

        for impath in Path(f'./images/output/{self.model}/').glob('*.png'):
            scene_name, view, _, flag, _= str(impath.name).split('-')
            img_stem = str(impath.stem) # e.g. Taitung_0-0-Webcam-R-264_x2_SR.png
            img_stem = prog.match(img_stem).group(0) # e.g. Taitung_0-0-Webcam-R-264
            img_name = "-".join([scene_name, view]) # e.g. Taitung_0-0

            if (particulars is not None) and (img_name not in particulars):
                continue

            if flag == 'R':
                if img_name in R_stems:
                    R_stems[img_name].append(img_stem)
                else:
                    R_stems[img_name] = [img_stem]
            elif flag == 'C':
                pass
            elif flag == 'P':
                pass
            else:
                print(f"Encountered invalid flag for {impath}", file=sys.stderr)
        
        for impath in Path(f'./images/rainy/').glob('*.png'):
            scene_name, view, _, flag, _= str(impath.name).split('-')
            img_stem = str(impath.stem)
            img_stem = prog.match(img_stem).group(0)
            img_name = "-".join([scene_name, view])

            if (particulars is not None) and (img_name not in particulars):
                continue

            if flag == 'R':
                pass
            elif flag == 'C':
                if img_name in C_stems:
                    C_stems[img_name].append(img_stem)
                else:
                    C_stems[img_name] = [img_stem]
            elif flag == 'P':
                P_stems[img_name] = img_stem
            else:
                print(f"Encountered invalid flag for {impath}", file=sys.stderr)
        
        print(f'Will process {len(R_stems)} scenes')

        self.C_stems = C_stems
        self.R_stems = R_stems
        self.P_stems = P_stems

        print(f"{len(C_stems[img_name])} GTs and {len(R_stems[img_name])} derained images")

    def print_metrics(self, metrics):
        avg_psnr_rainy_gt, avg_psnr_derained_gt, avg_ssim_rainy_gt, avg_ssim_derained_gt = metrics
        print(f"                 PSNR    SSIM")
        print(f"Rainy vs. GT:    {avg_psnr_rainy_gt:.2f}    {avg_ssim_rainy_gt:.2f}")
        print(f"Derained vs. GT: {avg_psnr_derained_gt:.2f}    {avg_ssim_derained_gt:.2f}")

    def write_metrics(self, file, row_name: str, metrics: np.ndarray):
        file.write(f'{row_name},' + ','.join([f"{n}" for n in metrics]) + '\n')
        file.flush()


    def find_metrics(self, display_groups=False, save=False):
        print("Will display first and last image groupings for each scene")

        # intialize average metrics for all scenes
        metrics = np.zeros(4)
        count = 0

        # create metrics save file if specified
        if save:
            mfile = open(Path(f'./images/metrics/{self.model}.csv'), 'w')
            mfile.write("Scene_frame,PSNR_clean_v_rainy,PSNR_clean_v_derained,SSIM_clean_v_rainy,SSIM_clean_v_derained\n")

            oscenefile = open(Path(f'./images/metrics/{self.model}_by_scene.csv'), 'w')
            oscenefile.write("Scene,avg_PSNR_clean_v_rainy,avg_PSNR_clean_v_derained,avg_SSIM_clean_v_rainy,avg_SSIM_clean_v_derained\n")

            ofile_path = Path(f'./images/metrics/overall.csv')
            if not ofile_path.exists():
                ofile = open(ofile_path, 'a')
                ofile.write("Model,avg_PSNR_clean_v_rainy,avg_PSNR_clean_v_derained,avg_SSIM_clean_v_rainy,avg_SSIM_clean_v_derained\n")
            else:
                ofile = open(ofile_path, 'a') 

        for name in sorted(self.R_stems):

            # initialize metrics for one scene
            metrics_scene = np.zeros(4)
            count_scene = 0

            print(f'Processing {name}')

            if self.clean == "one":
                clean_path = self.path_from_stem(Path('./images/rainy/'), self.C_stems[name][0])

            for i, rstem in enumerate(self.progress_func(self.R_stems[name])):
                if self.clean == "one2one":
                   clean_path = self.path_from_stem(Path('./images/rainy/'), self.C_stems[name][i]) 
                metrics_frame = np.zeros(4)

                count += 1
                count_scene += 1

                rainy_path = self.path_from_stem(Path('./images/rainy/'), rstem)
                derained_path = self.path_from_stem(Path(f'./images/output/{self.model}/'), rstem)

                clean_img = self.load_image(str(clean_path)) / 255.0
                rainy_img = self.load_image(str(rainy_path)) / 255.0
                derained_img = self.load_image(str(derained_path)) / 255.0

                metrics_frame[0] += psnr(clean_img, rainy_img)
                metrics_frame[1] += psnr(clean_img, derained_img)
                metrics_frame[2] += ssim(clean_img, rainy_img, multichannel=True)
                metrics_frame[3] += ssim(clean_img, derained_img, multichannel=True)

                metrics_scene += metrics_frame

                if save:
                    self.write_metrics(mfile, rstem, metrics_frame)

                if display_groups and count_scene in [1, len(self.R_stems[name])]:
                    plt.imshow(np.hstack((clean_img, rainy_img, derained_img)))
                    plt.show()
                if self.single:
                    break
            # update overall metrics
            metrics += metrics_scene

            # generate scene metrics
            metrics_scene /= count_scene
            print(f'Metrics for scene {name}')
            self.print_metrics(metrics_scene)

            if save:
                self.write_metrics(oscenefile, name, metrics_scene)
        
        metrics /= count
        print('####################')
        print('OVERALL')
        self.print_metrics(metrics)
        print('####################')

        if save:
            self.write_metrics(ofile, self.model, metrics)

if __name__ == "__main__":
    models_str = ", ".join(ImgCompare.models)
    clean_opts_str = ", ".join(ImgCompare.clean_opts)
    parser = argparse.ArgumentParser(description="Compare with PSNR and SSIM. Example command:"
        "./compare_images.py ED-v3 --single --save -p Cordele_0-0,Base_Cam_0-0,Hualien_0-0"
    )
    parser.add_argument('model', type=str, help=f'Model whose outputs to test. Choose from {models_str}')
    parser.add_argument('--single', action='store_true', help=f'Only process one image from each scene')
    parser.add_argument('--display', action='store_true', help=f'Display first and last image groupings for each scene')
    parser.add_argument('--save', action='store_true', help=f'Save metrics to csv files in ./images/metrics/')
    parser.add_argument('-p', '--particular', type=str, help='Particular scenes to parse')
    parser.add_argument('-c', '--clean_format', type=str, default='one', help=f'Clean/GT (ground truth) input format. Choose from {clean_opts_str}')
    args = parser.parse_args()
    if isinstance(args.particular, str):
        particulars = args.particular.split(',')
    else:
        particulars = None

    ic = ImgCompare(args.model, args.single, particulars=particulars, clean=args.clean_format)
    ic.find_metrics(display_groups=args.display, save=args.save)
