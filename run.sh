#!/bin/bash

model=$1
models=("MPRNet" "MSPFN" "RCDNet" "SPANet" "ED" "HRR" "DGNL")
models_versions=("MPRNet" "MSPFN" "RCDNet-spa" "RCDNet-rain100h" "SPANet" "ED-v4" "ED-v3" "ED-v3rain100h" "ED-v4rain100h" "ED-v3rain1400" "ED-v4rain1400" "HRR" "DGNL")

source ~/miniconda3/etc/profile.d/conda.sh
conda deactivate

if [[ $1 == "" ]] ; then
    printf "usage:
    ./run.sh download
    ./run.sh setup [conda | condarm | models | images]
    ./run.sh [MPRNet [gpu] | MSPFN | RCDNet [gpu] [clean] | SPANet | ED [gpu] | HRR | DGNL \n"
fi

if [[ $1 == "download" ]]; then
    git clone https://github.com/swz30/MPRNet.git
    git clone https://github.com/hongwang01/RCDNet.git
    git clone https://github.com/kuijiang0802/MSPFN.git
    git clone https://github.com/stevewongv/SPANet.git
    git clone https://github.com/tsingqguo/efficientderain.git ED
    git clone https://github.com/liruoteng/HeavyRainRemoval.git HRR
    git clone https://github.com/xw-hu/DGNL-Net.git DGNL
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
        folder if it exists)\n"

        # RCDNet
        cp model-modifications/RCDNet/rainheavytest.py model-modifications/RCDNet/srdata.py ./RCDNet/RCDNet_code/for_spa/src/data
        cp model-modifications/RCDNet/utility.py RCDNet/RCDNet_code/for_spa/src/

        # HRR
        mkdir -p ./HRR/.ckpt
        cp ./model-modifications/HRR/test.py HRR/
        printf "Download the pretrained HeavyRainRemovel model from
        https://www.dropbox.com/s/h8x6xl6epc45ngn/HeavyRain-stage2-2019-05-11-76_ckpt.pth.tar?dl=0
        then move 'HeavyRain-stage2-2019-05-11-76_ckpt.pth.tar' into the HRR/.ckpt folder\n"

        # DGNL
        cp ./model-modifications/DGNL/infer.py DGNL/
        printf "OPTIONALLY download the pretrained DGNL models from
        https://drive.google.com/drive/folders/1BzLzZZFhz2EZyK7HmWPQzZmbxJudS_zJ?usp=sharing
        then move 4000.pth into ./ckpt/DGNLNet/ and 60000.pth into ./ckpt/DGNLNet_fast/.
        They are already included in this repo\n"
    fi

    if [[ $2 == "images" ]]; then
        # setup image directory
        mkdir -p images
        cd images
        mkdir -p rainy clean output clean-orig rainy-orig
        cd output
        mkdir -p ${models_versions[@]}
    fi

    if [[ $2 == "images-files" ]]; then
        # setup files for processing images in images directory
        cp sample_copy.sh images/copy.sh
        cp sample_Metrics.ipynb images/Metrics.ipynb
        cp sample_RunModels.ipynb images/RunModels.ipynb
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

if [[ $model == "RCDNet" ]]; then
    ./run.sh RCDNet-rain100h $2
    ./run.sh RCDNet-spa $2
fi

if [[ $model == "RCDNet-rain100h" ]]; then
(
    fcount=$(ls -l ./images/rainy/*.* | wc -l)
    echo $fcount
    cpu='--cpu'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    printf "Running RCDNet with rain100H weights\n"
    conda activate RCDNet
    cd RCDNet/RCDNet_code/for_spa/src/
    rm -f ../experiment/RCDNet_test/results/*
    python3 main.py --data_test RainHeavyTest  \
                    --ext img \
                    --scale 2 \
                    --pre_train ../../../Pretrained\ Model/rain100H/model_best.pt \
                    --model RCDNet \
                    --test_only \
                    --save_results \
                    --save RCDNet_test \
                    --data_range 1-${fcount} \
                    $cpu
    mv ../experiment/RCDNet_test/results/*_SR.png ../../../../images/output/RCDNet-rain100h/
    rm -f ../experiment/RCDNet_test/results/*
)
fi

if [[ $model == "RCDNet-spa" ]]; then
(
    fcount=$(ls -l ./images/rainy/*.* | wc -l)
    echo $fcount
    cpu='--cpu'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    printf "Running RCDNet with SPA data weights\n"
    conda activate RCDNet
    cd RCDNet/RCDNet_code/for_spa/src/
    rm -f ../experiment/RCDNet_test/results/*
    python3 main.py --data_test RainHeavyTest  \
                    --ext img \
                    --scale 2 \
                    --pre_train ../../../Pretrained\ Model/SPA-Data/model_best.pt \
                    --model RCDNet \
                    --test_only \
                    --save_results \
                    --save RCDNet_test \
                    --data_range 1-${fcount} \
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

    ./run.sh ED-v3rain100h $2
    ./run.sh ED-v4rain100h $2
    ./run.sh ED-v3rain1400 $2
    ./run.sh ED-v4rain1400 $2
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
if [[ $model == "ED-v3rain100h" ]]; then
(
    cpu='--no_gpu True'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    conda activate ED
    cd ED

    printf "Running EfficientDerain v3_rain100H\n"
    python ./validation.py \
        --load_name "./models/v3_rain100H/v3_rain100H.pth" \
        --save_name "../images/output/ED-v3rain100h" \
        --baseroot "../images" \
        $cpu


)
fi
if [[ $model == "ED-v4rain100h" ]]; then
(
    cpu='--no_gpu True'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    conda activate ED
    cd ED

    printf "Running EfficientDerain v4_rain100H\n"
    python ./validation.py \
        --load_name "./models/v4_rain100H/v4_rain100H.pth" \
        --save_name "../images/output/ED-v4rain100h" \
        --baseroot "../images" \
        $cpu


)
fi
if [[ $model == "ED-v3rain1400" ]]; then
(
    cpu='--no_gpu True'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    conda activate ED
    cd ED

    printf "Running EfficientDerain v3_rain1400\n"
    python ./validation.py \
        --load_name "./models/v3_rain1400/v3_rain1400.pth" \
        --save_name "../images/output/ED-v3rain1400" \
        --baseroot "../images" \
        $cpu


)
fi
if [[ $model == "ED-v4rain1400" ]]; then
(
    cpu='--no_gpu True'
    if [[ $2 == "gpu" ]]; then
        cpu=''
    fi
    conda activate ED
    cd ED

    printf "Running EfficientDerain v4_SPA\n"
    python ./validation.py \
        --load_name "./models/v4_rain1400/v4_rain1400.pth" \
        --save_name "../images/output/ED-v4rain1400" \
        --baseroot "../images" \
        $cpu


)
fi

################################################################################
# HeavyRainRemoval
################################################################################
if [[ $model == "HRR" ]]; then
(
    conda activate HRR
    cd HRR
    python test.py
)
fi

################################################################################
# DGNL
################################################################################

if [[ $model == "DGNL" ]]; then
(
    conda activate DGNL
    cd DGNL
    python infer.py
)
fi