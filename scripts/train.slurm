#!/bin/bash
#SBATCH --job-name=nnunet_train_501
#SBATCH --output=/mnt/data/home/myhoke615/ppv_zadanie/logs/%x_%j.out
#SBATCH --error=/mnt/data/home/myhoke615/ppv_zadanie/logs/%x_%j.err
#SBATCH --partition=GPU
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=24:00:00

# Activate scratch if available
if [[ -f .activate_scratch ]]; then
	source .activate_scratch
fi


# Activate conda environment
source ~/.bashrc
conda activate nnunet

# nnUNet paths
export nnUNet_raw="/mnt/data/home/myhoke615/ppv_zadanie/nnunet_data/nnUNet_raw"
export nnUNet_preprocessed="/mnt/data/home/myhoke615/ppv_zadanie/nnunet_data/nnUNet_preprocessed"
export nnUNet_results="/mnt/data/home/myhoke615/ppv_zadanie/nnunet_data/nnUNet_results"

# Log GPU model for traceability
nvidia-smi --query-gpu=name --format=csv,noheader || true

# Train fold 0 with 3d_fullres
stdbuf -oL -eL nnUNetv2_train 501 3d_fullres 0