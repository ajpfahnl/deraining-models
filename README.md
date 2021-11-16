# Deraining SOTAs

This repo is intended to allow images to be run on various SOTAs quickly and easily. This is a crude DIY implementation and has only been tested on MacOS and Google Colab. Each deraining model has its own conda environment, all of which can be created as described in the setup steps below.

The following deraining models are included:
 * [MPRNet](https://github.com/swz30/MPRNet)
 * [MSPFN](https://github.com/kuijiang0802/MSPFN)
 * [RCDNet](https://github.com/hongwang01/RCDNet)
 * [SPANet](https://github.com/stevewongv/SPANet)
 * [EfficientDeRain](https://github.com/tsingqguo/efficientderain)
 * [HeavyRainRemoval](https://github.com/liruoteng/HeavyRainRemoval)
 * [DGNL-Net](https://github.com/xw-hu/DGNL-Net)

## Requirements
This assumes 
 * A miniconda installation (try testing to see if `~/miniconda3/etc/profile.d/conda.sh` exists).

## Setting up
Here's a sample workflow using the `run.sh` script:
 1. `./run.sh` to see the options.
 2. `./run.sh setup models`: modify SOTAs for testing locally. Make sure to download and add the pretrained models afterwards (check the messages after running this command).
 3. OPTIONAL if only running with Google Colab: `./run.sh setup conda`: set up conda environments. `./run.sh setup condarm` to remove the environments created.
 4. `./run.sh setup images`: Set up the testing image directories.
 5. `./run.sh setup images-files`: Set up files used to run models, analyze derained outputs, and more in the `images` directory. Includes
    * [RunModels.ipynb](./sample_RunModels.ipynb) which allows for all models to be run in a Jupyter notebook (tested on Google Colab).
    * [Metrics.ipynb](./sample_Metrics.ipynb) which calculates PSNR and SSIM of outputs relative to GTs (if they exist).
    * [copy.sh](./sample_copy.sh) which provides a sample method for copying images into the `image` directory.
 5. Add rainy images to `images/rainy-orig` and, optionally, clean images to `images/clean-orig`. You can try testing with `1.jpg` in [sample_images](sample_images).
 6. `./preprocess.py` to convert images to widths and heights of multiples of 4.
 7. `./run.sh [MPRNet | MSPFN | RCDNet | SPANet | ED | HRR | DGNL]`: Run the SOTAs.
 8. View the derained images in the `images/output/[model]`.

To compare images with SSIM and PSNR, use the [compare_images.py](compare_images.py) program.
```
usage: compare_images.py [-h] [--single] [--display] [--save] [-p PARTICULAR] [-c CLEAN_FORMAT] model

Compare with PSNR and SSIM. Example command:./compare_images.py ED-v3 --single --save -p Cordele_0-0,Base_Cam_0-0,Hualien_0-0

positional arguments:
  model                 Model whose outputs to test. Choose from MPRNet, MSPFN, RCDNet-spa, RCDNet-rain100h, SPANet, ED-v4, ED-v3, HRR, DGNL, ED-v3rain100h, ED-v4rain100h, ED-v3rain1400, ED-v4rain1400

optional arguments:
  -h, --help            show this help message and exit
  --single              Only process one image from each scene
  --display             Display first and last image groupings for each scene
  --save                Save metrics to csv files in ./images/metrics/
  -p PARTICULAR, --particular PARTICULAR
                        Particular scenes to parse
  -c CLEAN_FORMAT, --clean_format CLEAN_FORMAT
                        Clean/GT (ground truth) input format. Choose from one, one2one
```