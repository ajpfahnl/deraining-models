# Deraining SOTAs

This repo is intended to allow images to be run on various SOTAs quickly and easily on a local development environment. This is a crude DIY implementation and has only been tested on MacOS. Each deraining model has its own conda environment, and the specifics of each can be found in [conda-envs](conda-envs). 

You can run all models in Google Colab with the [RunModels.ipynb](./RunModels.ipynb) notebook. Make sure to change the working directory to wherever you've decided to place this repo in your Google Drive.

__Exception__: SPANet is set up so that the model runs only on Google Colab.

## Requirements
This assumes 
 * A miniconda installation (try testing to see if `~/miniconda3/etc/profile.d/conda.sh` exists).

## Setting up
Here's a sample workflow using the `run.sh` script:
 1. `./run.sh` to see the options.
 2. `./run.sh setup models`: modify SOTAs for testing locally. Make sure to download and add the pretrained models afterwards (check the messages after running this command).
 3. `./run.sh setup conda`: set up conda environments. `./run.sh setup condarm` to remove the environments created.
 4. `./run.sh setup images`: Set up the testing image directories.
 5. Add rainy images to `images/rainy-orig` and, optionally, clean images to `images/clean-orig`. You can try testing with `1.jpg` in [sample_images](sample_images).
 6. `./preprocess.py` to convert images to widths and heights of multiples of 4.
 7. `./run.sh [MPRNet | MSPFN | RCDNet | SPANet | ED]`: Run the SOTAs.
 8. View the derained images in the `images/output/[model]`.

To compare images with SSIM and PSNR, use the [compare_images.py](compare_images.py) program.
```
usage: compare_images.py [-h] [--single] [--display] [--save] [-p PARTICULAR] model

Compare with PSNR and SSIM. Example command:./compare_images.py ED-v3 --single --save -p Cordele_0-0,Base_Cam_0-0,Hualien_0-0,Hualien_0-2,Hualien_0-3,Marunuma_Alt_0-0,Marunuma_Alt_0-1,Geiranger_0-0,Geiranger_0-1,Miami_County_0-0,Fort_Lauderdale_1-0,Fort_Lauderdale_1-1

positional arguments:
  model                 Model whose outputs to test. Choose from MPRNet, MSPFN, RCDNet-spa, RCDNet-rain100h, SPANet, ED-v4, ED-v3

optional arguments:
  -h, --help            show this help message and exit
  --single              Only process one image from each scene
  --display             Display first and last image groupings for each scene
  --save                Save metrics to csv files in ./images/metrics/ (create this directory first)
  -p PARTICULAR, --particular PARTICULAR
                        Particular scenes to parse separated by commas
```