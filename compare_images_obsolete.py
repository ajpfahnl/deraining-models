import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import numpy as np
import argparse
import sys

class ImgCompare():

    def load_image(self, path):
        img = cv2.imread(path)
        if not isinstance(img, np.ndarray):
            print(f"Couldn't read image from {path}", file=sys.stderr)
        return img

    def __init__(self, name, self_compare = False):
        self.img_orig_rainy = cv2.imread(f"images/rainy/{name}.jpg")
        if self_compare:
            clean_dir = "rainy"
        else:
            clean_dir = "clean"
        self.img_orig_clean = self.load_image(f"images/{clean_dir}/{name}.jpg")
        self.img_MPRNet = self.load_image(f"images/output/MPRNet/{name}.png")
        self.img_MSPFN = self.load_image(f"images/output/MSPFN/{name}.jpg")
        self.img_RCDNet = self.load_image(f"images/output/RCDNet/{name}_x2_SR.png")

    def find_metrics(self):
        psnr_gt = cv2.PSNR(self.img_orig_clean, self.img_orig_clean)
        psnr_base = cv2.PSNR(self.img_orig_clean, self.img_orig_rainy)
        psnr_MPRNet = cv2.PSNR(self.img_orig_clean, self.img_MPRNet)
        psnr_MSPFN = cv2.PSNR(self.img_orig_clean[:self.img_MSPFN.shape[0], :self.img_MSPFN.shape[1], :], self.img_MSPFN)
        psnr_RCDNet = cv2.PSNR(self.img_orig_clean, self.img_RCDNet)

        ssim_gt = ssim(self.img_orig_clean, self.img_orig_clean, multichannel=True)
        ssim_base = ssim(self.img_orig_clean, self.img_orig_rainy, multichannel=True)
        ssim_MPRNet = ssim(self.img_orig_clean, self.img_MPRNet, multichannel=True)
        ssim_MSPFN = ssim(self.img_orig_clean[:self.img_MSPFN.shape[0], :self.img_MSPFN.shape[1], :], self.img_MSPFN, multichannel=True)
        ssim_RCDNet = ssim(self.img_orig_clean, self.img_RCDNet, multichannel=True)

        print(f"              PSNR / SSIM")
        print(f"GT - GT:     {psnr_gt:.2f} / {ssim_gt:.2f}")
        print(f"GT - rainy:  {psnr_base:.2f} / {ssim_base:.2f}")
        print(f"GT - MPRNet: {psnr_MPRNet:.2f} / {ssim_MPRNet:.2f}")
        print(f"GT - MSPFN : {psnr_MSPFN:.2f} / {ssim_MSPFN:.2f}")
        print(f"GT - RCDNet: {psnr_RCDNet:.2f} / {ssim_RCDNet:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare with PSNR and SSIM')
    parser.add_argument('imgbase', type=str, help="Basename of image path in images/output/[model]/[imgbase].png suffix.")
    parser.add_argument('--self', action='store_true', help="Compare to input.")
    args = parser.parse_args()

    ic = ImgCompare(args.imgbase, args.self)
    ic.find_metrics()

