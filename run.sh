#!/bin/bash

model=$1
models=("MPRNet" "MSPFN" "RCDNet" "SPANet" "ED")
models_versions=("MPRNet" "MSPFN" "RCDNet-spa" "RCDNet-rain100h" "SPANet" "ED-v4" "ED-v3")

source ~/miniconda3/etc/profile.d/conda.sh
conda deactivate

if [[ $1 == "" ]] ; then
    printf "usage:
    ./run.sh download
    ./run.sh setup [conda | condarm | models | images]
    ./run.sh [MPRNet [gpu] | MSPFN | RCDNet [gpu] [clean] | SPANet | ED [gpu] \n"
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
            conda env create -f conda-envs/conda-${m}.yml || echo "${m} conda environment file does not exist"
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
        cp model-modifications/ED/*.py ED/
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
        mkdir -p ${models_versions[@]}
    fi
)
fi

################################################################################
# MPRNet
################################################################################
if [[ $model == "MPRNet" ]]; then
(
    printf "Running MPRNet\n"
    conda activate MPRNet
    cd MPRNet
    if [[ $2 == "gpu" ]]; then
        python3 demo.py --task Deraining --input_dir ../images/rainy/ --result_dir ../images/output/MPRNet
    else
        python3 demo_cpu.py --task Deraining --input_dir ../images/rainy/ --result_dir ../images/output/MPRNet
    fi
)
fi

################################################################################
# MSPFN
################################################################################
if [[ $model == "MSPFN" ]]; then
(
    printf "Running MSPFN\n"
    conda activate MSPFN
    cd MSPFN/model/test/
    python3 test_MSPFN.py --input_dir ../../../images/rainy/ --result_dir ../../../images/output/MSPFN
)
fi

################################################################################
# RCDNet
################################################################################
if [[ $model == "RCDNet" ]] || [[ $model == "RCDNet-spa" ]] || [[ $model == "RCDNet-rain100h" ]]; then
(
    if [[ $2 == "clean" ]]; then
        rm -rf ./RCDNet/RCDNet_code/for_spa/experiment/RCDNet_test/
        rm -rf ./RCDNet/RCDNet_code/for_spa/data/test/
        exit 0
    fi

    # create directories
    mkdir -p RCDNet/RCDNet_code/for_spa/experiment/
    data_dir="RCDNet/RCDNet_code/for_spa/data/test/small"
    mkdir -p ${data_dir}/norain/ ${data_dir}/rain/

    # clean image directories
    rm ${data_dir}/norain/*
    rm ${data_dir}/rain/*

    # convert and move
    for img_path in ./images/rainy/*.*; do
        convert_path=${data_dir}/rain/$(basename ${img_path%.*}).png
        printf "\t$img_path --> $convert_path\n"
        python3 -c "import cv2; in_img = cv2.imread(\"${img_path}\"); cv2.imwrite(\"${convert_path}\", in_img)"
    done

    # copy image as dummy data to norain
    cp ${data_dir}/rain/* ${data_dir}/norain/

    rm -f ${data_dir}/rain/.DS_Store
)
fi

if [[ $model == "RCDNet" ]]; then
    ./run.sh RCDNet-rain100h $2
    ./run.sh RCDNet-spa $2
fi

if [[ $model == "RCDNet-rain100h" ]]; then
(
    cpu='--cpu'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    printf "Running RCDNet with rain100H weights\n"
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
    mv ../experiment/RCDNet_test/results/*_SR.png ../../../../images/output/RCDNet-rain100h/
    rm -f ../experiment/RCDNet_test/results/*
)
fi

if [[ $model == "RCDNet-spa" ]]; then
(
    cpu='--cpu'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    printf "Running RCDNet with SPA data weights\n"
    conda activate RCDNet
    cd RCDNet/RCDNet_code/for_spa/src/
    python3 main.py --data_test RainHeavyTest  \
                    --ext img \
                    --scale 2 \
                    --pre_train ../../../Pretrained\ Model/SPA-Data/model_best.pt \
                    --model RCDNet \
                    --test_only \
                    --save_results \
                    --save RCDNet_test \
                    $cpu
    
    mv ../experiment/RCDNet_test/results/*_SR.png ../../../../images/output/RCDNet-spa/
    rm -f ../experiment/RCDNet_test/results/*
)
fi

################################################################################
# SPANet
################################################################################
if [[ $model == "SPANet" ]]; then
    printf "Run \`SPANet.ipynb\` in Google Colab. 
    Ensure that this repository is in your Google Drive, and 
    change the working directory to this folder's directory.
"
fi

################################################################################
# ED
################################################################################
if [[ $model == "ED" ]]; then
    ./run.sh ED-v3 $2
    ./run.sh ED-v4 $2
fi

if [[ $model == "ED-v3" ]]; then
(
    cpu='--no_gpu True'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    conda activate ED
    cd ED

    printf "Running EfficientDerain v3_SPA\n"
    python ./validation.py \
        --load_name "./models/v3_SPA/v3_SPA.pth" \
        --save_name "../images/output/ED-v3" \
        --baseroot "../images" \
        $cpu


)
fi

if [[ $model == "ED-v4" ]]; then
(
    cpu='--no_gpu True'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    conda activate ED
    cd ED

    printf "Running EfficientDerain v4_SPA\n"
    python ./validation.py \
        --load_name "./models/v4_SPA/v4_SPA.pth" \
        --save_name "../images/output/ED-v4" \
        --baseroot "../images" \
        $cpu


)
fi