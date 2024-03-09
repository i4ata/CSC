#!/bin/bash
#SBATCH --time=20:00:00
#SBATCH --job-name=csc_hw
#SBATCH --mem=8000
module load Python/3.9.6-GCCcore-11.2.0
module load tqdm/4.64.0-GCCcore-11.3.0

python stv.py

