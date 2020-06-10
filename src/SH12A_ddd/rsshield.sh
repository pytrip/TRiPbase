#!/bin/bash
# Submission script for embarrasingly parallel runs on a SLURM cluster.
# How to run:
#
# sbatch --array 0-40 rsshield.sh
# and you can monitor with
# squeue -r
#
#SBATCH --output=shieldhitJob.%j.out     # standard output file name
#SBATCH --error=shieldhitJob.%j.err      # standard error output file name
#SBATCH --ntasks=1
#SBATCH --contiguous

#echo Node ID       $SLURM_NODEID
#echo NTasks        $SLURM_NTASKS
#echo NNodes        $SLURM_NNODES
#echo LocalID       $SLURM_LOCALID
#echo Array task ID $SLURM_ARRAY_TASK_ID

shieldhit -N${SLURM_ARRAY_TASK_ID}
