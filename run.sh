#!/bin/bash

model=$1
models=("MPRNet" "MSPFN" "RCDNet" "SPANet" "ED")

source ~/miniconda3/etc/profile.d/conda.sh
conda deactivate

if [[ $1 == "" ]] ; then
    printf "usage:
    ./run.sh download
    ./run.sh setup [conda | condarm | models | images]
    ./run.sh [MPRNet | MSPFN | RCDNet [gpu] [skipcopy]] [clean] | SPANet | ED\n"
fi

if [[ $1 == "download" ]]; then
    git clone https://github.com/swz30/MPRNet.git
    git clone https://github.com/hongwang01/RCDNet.git
    git clone https://github.com/kuijiang0802/MSPFN.git
    git clone https://github.com/stevewongv/SPANet.git
    git clone https://github.com/tsingqguo/efficientderain.git ED
fi

# call setup to create directories
if [[ $1 == "setup" ]]; then
(
    # conda envs
    if [[ $2 == "conda" ]]; then
        for m in ${models[@]}; do
            conda env create -f conda-envs/conda-${m}.yml
        done
    fi

    if [[ $2 == "condarm" ]]; then
        for m in ${models[@]}; do
            conda env remove -n ${m}
        done
    fi

    # copy model modifications
    if [[ $2 == "models" ]]; then
        # MPRNet
        cp model-modifications/MPRNet/demo_cpu.py MPRNet/
        printf "Download the pretrained MPRNet models from
        https://drive.google.com/file/d/1O3WEJbcat7eTY6doXWeorAbQ1l_WmMnM/view?usp=sharing
        and copy 'model_deraining.pth' into 'MPRNet/Deraining/pretrained_models/'.\n"

        # MSPFN
        cp model-modifications/MSPFN/TEST_MSPFN_M17N1.py MSPFN/model/
        cp model-modifications/MSPFN/test_MSPFN.py MSPFN/model/test/
        mkdir -p MSPFN/model/MSPFN_pretrained
        printf "Download the pretrained MSPFN models from
        https://drive.google.com/file/d/1nrjZtNs6AJYvfHi9TeCVTs50E57Fxgsc/view
        and move the 'epoch44\*' files into 'MSPFN/model/MSPFN_pretrained'.\n"

        # SPANet
        cp model-modifications/SPANet/*.py SPANet/

        # ED
        cp model-modifications/ED/*.py model-modifications/ED/test.sh ED/
        printf "Download the pretrained EfficientDerain (ED) models from
        https://drive.google.com/file/d/1OBAIG4su6vIPEimTX7PNuQTxZDjtCUD8/view?usp=sharing
        and move the entire 'models' folder into the 'ED' folder (remove the 'models'
        folder if it exists.\n"
    fi

    if [[ $2 == "images" ]]; then
        # setup image directory
        mkdir -p images
        cd images
        mkdir -p rainy clean output clean-orig rainy-orig
        cd output
        mkdir -p ${models[@]}
    fi
)
fi

# MPRNet
if [[ $model == "MPRNet" ]]; then
(
    conda activate MPRNet
    cd MPRNet
    python3 demo_cpu.py --task Deraining --input_dir ../images/rainy/ --result_dir ../images/output/MPRNet
)
fi

# MSPFN
if [[ $model == "MSPFN" ]]; then
(
    conda activate MSPFN
    cd MSPFN/model/test/
    python3 test_MSPFN.py --input_dir ../../../images/rainy/ --result_dir ../../../images/output/MSPFN
)
fi

# RCDNet
if [[ $model == "RCDNet" ]]; then
(
    cpu='--cpu'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi

    if [[ $2 == "clean" ]]; then
        rm -rf ./RCDNet/RCDNet_code/for_spa/experiment/RCDNet_test/
        rm -rf ./RCDNet/RCDNet_code/for_spa/data/test/
        exit 0
    fi

    if [[ $3 == "skipcopy" ]]; then
        printf ""
    else
        # create directories
        mkdir -p RCDNet/RCDNet_code/for_spa/experiment/
        data_dir="RCDNet/RCDNet_code/for_spa/data/test/small"
        mkdir -p ${data_dir}/norain/ ${data_dir}/rain/

        # clean image directories
        rm ${data_dir}/norain/*
        rm ${data_dir}/rain/*

        # convert and move
        for img_path in ./images/rainy/*; do
            convert_path=${data_dir}/rain/$(basename ${img_path%.*}).png
            printf "\t$img_path --> $convert_path\n"
            convert $img_path $convert_path
    done
    fi

    # copy image as dummy data to norain
    cp ${data_dir}/rain/* ${data_dir}/norain/

    rm -f ${data_dir}/rain/.DS_Store
    
    conda activate RCDNet
    cd RCDNet/RCDNet_code/for_spa/src/
    python3 main.py --data_test RainHeavyTest  \
                    --ext img \
                    --scale 2 \
                    --pre_train ../../../Pretrained\ Model/rain100H/model_best.pt \
                    --model RCDNet \
                    --test_only \
                    --save_results \
                    --save RCDNet_test \
                    $cpu
    
    mv ../experiment/RCDNet_test/results/* ../../../../images/output/RCDNet/
)
fi

# SPANet
if [[ $model == "SPANet" ]]; then
    printf "Run \`SPANet.ipynb\` in Google Colab. 
    Ensure that this repository is in your Google Drive, and 
    change the working directory to this folder's directory.
"
fi

# ED
if [[ $model == "ED" ]]; then
(
    conda activate ED
    cd ED
    sh test.sh
)
fi