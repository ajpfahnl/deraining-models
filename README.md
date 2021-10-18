# Deraining SOTAs

This repo is intended to allow images to be run on various SOTAs quickly and easily on a local development environment. This is a crude DIY implementation and has only been tested on MacOS. Each deraining model has its own conda environment, and the specifics of each can be found in [conda-envs](conda-envs). 

Note: These models were configured to run on CPU only.

## Requirements
This assumes 
 * A miniconda installation (try testing to see if `~/miniconda3/etc/profile.d/conda.sh` exists).
 * An ImageMagick installation which can be installed with `brew install imagemagick`. I'm using the `convert` utility to quickly convert .jpg images to .png for RCDNet.

## Setting up
Here's a sample workflow using the `run.sh` script:
 1. `./run.sh` to see the options.
 2. `./run.sh setup models`: modify SOTAs for testing locally. Make sure to download and add the pretrained models afterwards (check the messages after running this command).
 3. `./run.sh setup conda`: set up conda environments. `./run.sh setup condarm` to remove the environments created.
 4. `./run.sh setup images`: Set up the testing image directories.
 5. Add rainy images to `images/rainy-orig` and, optionally, clean images to `images/clean-orig`. You can try testing with `1.jpg` in [sample_images](sample_images).
 6. `./imgto4.py` to convert images to widths and heights of multiples of 4.
 7. `./run.sh [MPRNet | MSPFN | RCDNet]`: Run the SOTAs.
 8. View the derained images in the `images/output/[model]`.

 To compare images with SSIM and PSNR, use the [compare_images.py](compare_images.py) program.
 ```
 Compare with PSNR and SSIM

positional arguments:
  imgbase     Basename of image path in images/output/[model]/[imgbase].png suffix.

optional arguments:
  -h, --help  show this help message and exit
  --self      Compare to input.
 ```
For example, to measure compare the outputs of the models on `1.jpg` to the input itself, run `python3 compare_images.py --self 1`. If there was a clean image to compare to, we would omit the `--self` option.