# Quick Start: nnUNet SLURM Training

## 1. Setup (one time only)

```bash

# Create conda environment from YAML
conda env create -f environment.yml

# Activate environment
conda activate nnunet

# Create logs directory
mkdir -p logs
```

**Verify setup:**
```bash
which nnUNetv2_plan_and_preprocess
ls -d nnunet_data/nnUNet_{raw,preprocessed,results}
```

---

## 2. Run Preprocessing

```bash
# Submit job
sbatch scripts/nnunet_preprocess.slurm

# Monitor
squeue -u $USER
tail -f logs/nnunet_preprocess_*.out

# When complete, check:
ls nnunet_data/nnUNet_preprocessed/Dataset501_BraTSFiltered/
```

---

## 3. Run Training

```bash
# Submit job (after preprocessing finishes)
sbatch scripts/train.slurm

# Monitor
squeue -u $USER
tail -f logs/nnunet_train_*.out

# Results location:
# ls nnunet_data/nnUNet_results/Dataset501_BraTSFiltered/
```

---

## 4. Monitor Jobs

```bash
# View all jobs
squeue -u $USER

# Check specific job
squeue -j JOB_ID --long

# Cancel a job
scancel JOB_ID

# View errors
grep error logs/*.err
```

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `conda not found` | `source ~/.bashrc` |
| `partition not found` | `sinfo` (then update SLURM script) |
| `nnUNetv2_train not found` | `conda activate nnunet` |
| `out of memory` | Increase `--mem` in SLURM script |
| `job timeout` | Increase `--time` in SLURM script |

---

## Change Dataset ID (if needed)

```bash
# Replace 501 with your dataset ID (e.g., 550)
sed -i 's/501/550/g' scripts/train.slurm
sed -i 's/501/550/g' scripts/nnunet_preprocess.slurm
```

---

## Adjust Resources (if needed)

Edit SLURM files and modify:
```bash
#SBATCH --mem=96G              # More memory
#SBATCH --time=48:00:00         # More time
#SBATCH --gres=gpu:2            # More GPUs
#SBATCH --cpus-per-task=16      # More CPU cores
```

---

## Output Locations

- **Logs**: `logs/`
- **Preprocessed**: `nnunet_data/nnUNet_preprocessed/Dataset501_BraTSFiltered/`
- **Results**: `nnunet_data/nnUNet_results/Dataset501_BraTSFiltered/`
