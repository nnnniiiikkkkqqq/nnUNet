#!/bin/bash
#SBATCH --job-name=nnunet_preprocess_501
#SBATCH --output=/mnt/data/home/myhoke615/ppv_zadanie/logs/%x_%j.out
#SBATCH --error=/mnt/data/home/myhoke615/ppv_zadanie/logs/%x_%j.err
#SBATCH --partition=GPU
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00

# Activate scratch if available
if [[ -f .activate_scratch ]]; then
  source .activate_scratch
fi


# Activate conda environment
if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]]; then
  source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
  source ~/.bashrc
fi
conda activate nnunet

# nnUNet paths
export nnUNet_raw="/mnt/data/home/myhoke615/ppv_zadanie/nnunet_data/nnUNet_raw"
export nnUNet_preprocessed="/mnt/data/home/myhoke615/ppv_zadanie/nnunet_data/nnUNet_preprocessed"
export nnUNet_results="/mnt/data/home/myhoke615/ppv_zadanie/nnunet_data/nnUNet_results"

# Convert filtered_dataset into nnUNet raw structure
python "$(dirname "${BASH_SOURCE[0]}")/prepare_nnunet_braTS_filtered.py" \
  --source /mnt/data/home/myhoke615/ppv_zadanie/filtered_dataset \
  --dataset-id 501 \
  --dataset-name BraTSFiltered \
  --channel-name t2f \
  --label-map background:0 tumor:1 \
  --binarize-labels \
  --link-type symlink

# Plan and preprocess (3d only)
nnUNetv2_plan_and_preprocess -d 501 -c 3d_fullres --verify_dataset_integrity
