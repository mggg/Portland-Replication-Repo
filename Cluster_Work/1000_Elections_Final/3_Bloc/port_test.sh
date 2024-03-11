#!/bin/bash

#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=8G
#SBATCH --mail-type=NONE
#SBATCH --mail-user=NONE

alpha_poc_params=$1
alpha_wp_params=$2
alpha_wm_params=$3
cohesion_poc_params=$4
cohesion_white_progressive_params=$5
cohesion_white_conservative_params=$6
candidates=$7
num_elections=$8
output_file=$9
log_file=${10}


echo --alpha_poc_params "$alpha_poc_params"
echo --alpha_wp_params "$alpha_wp_params"
echo --alpha_wm_params "$alpha_wm_params" 
echo --cohesion_poc_params "$cohesion_poc_params" 
echo --cohesion_white_progressive_params "$cohesion_white_progressive_params" 
echo --cohesion_white_conservative_params "$cohesion_white_conservative_params" 
echo --candidates "$candidates" 
echo --num_elections "$num_elections" 
echo --output_file "$output_file" 
echo --log_file "$log_file"

{
    python simulate_elections_zbz.py \
        --candidates "$candidates" \
        --alpha_poc_params "$alpha_poc_params" \
        --alpha_wp_params "$alpha_wp_params" \
        --alpha_wm_params "$alpha_wm_params" \
        --cohesion_poc_params "$cohesion_poc_params" \
        --cohesion_white_progressive_params "$cohesion_white_progressive_params" \
        --cohesion_white_conservative_params "$cohesion_white_conservative_params" \
        --num_elections "$num_elections"
} > "${output_file}"

sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU >> "$log_file" 2>> "$log_file"