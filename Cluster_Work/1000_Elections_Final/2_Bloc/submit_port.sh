#!/bin/bash

# This script is meant to act as a sentinel to submit
# jobs to the slurm scheduler. The main idea is that the
# running script will be the one that calls the process
# that takes up the most time 



# ==============
# JOB PARAMETERS
# ==============

# This is the identifier that slurm will use to help
# keep track of the jobs. Please make sure that this
# does not exceed 80 characters.
job_name="portland_trial_$(date '+%d-%m-%Y@%H:%M:%SET')"

# This controls how many jobs the scheduler will
# see submitted at the same time.
max_concurrent_jobs=10

# This is the name of the script that will be run
# to actually process all of the files and do the 
# you may need to modify the call to this script
# on line 167 or so
running_script_name="port_test.sh"


# ==================
# RUNNING PARAMETERS
# ==================

n_elections=1000

output_dir="Port_outputs"
log_dir="Port_logs"

alpha_poc_matrix=("1 1")

alpha_wp_matrix=("1 1")

cohesion_poc_matrix=("0.8 0.2" \
"0.6 0.4" \
"0.6 0.4" \
"0.8 0.2" \
"0.8 0.2" \
"0.6 0.4" )

cohesion_wp_matrix=("0.1 0.9" \
"0.25 0.75" \
"0.4 0.6" \
"0.4 0.6" \
"0.3 0.7" \
"0.3 0.7" )

candidates_matrix=("2 10" \
                   "6 8" \
                   "5 5" \
                   "3 8" \
                   "3 10" \
                   "4 10")

# ===============================================================
# Ideally, you should not need to modify anything below this line
# However, you may need to modify the call on line 167
# ===============================================================


mkdir -p "${output_dir}"
mkdir -p "${log_dir}"

job_ids=()
job_index=0

echo "========================================================"
echo "The job name is: $job_name"
echo "========================================================"

# This function will generate a label for the log and output file
generate_file_label() {
    local candidates="$1"
    local alpha_poc="$2"
    local alpha_wp="$3"
    local cohesion_poc="$4"
    local cohesion_wp="$5"
    local n_elections="$6"


    # Use string substistution to replace spaces with dashes
    # This will make the files nicer to work with in the command line
    echo "cand_${candidates// /-}"\
        "apoc_${alpha_poc// /-}"\
        "awp_${alpha_wp// /-}"\
        "copoc_${cohesion_poc// /-}"\
        "cowp_${cohesion_wp// /-}"\
        "n_elec_${n_elections// /-}"\
        | tr ' ' '_'
    # The tr command replaces spaces with underscores so that
    # the file names are a bit nicer to read
}

# Indentation modified for readability

for i in "${!alpha_poc_matrix[@]}"; do
for j in "${!alpha_wp_matrix[@]}"; do
    alpha_poc="${alpha_poc_matrix[$i]}"
    alpha_wp="${alpha_wp_matrix[$j]}"
    
    # Cohesion parameters are grouped by their index, so we loop through them separately
    for l in "${!cohesion_poc_matrix[@]}"; do
        cohesion_poc="${cohesion_poc_matrix[$l]}"
        cohesion_wp="${cohesion_wp_matrix[$l]}"
        
        for m in "${!candidates_matrix[@]}"; do
            candidates="${candidates_matrix[$m]}"
   
            file_label=$(generate_file_label \
                "$candidates" \
                "$alpha_poc" \
                "$alpha_wp" \
                "$cohesion_poc" \
                "$cohesion_wp" \
                "$n_elections"
            )
            
            log_file="${log_dir}/${file_label}.log"
            output_file="${output_dir}/${file_label}.txt"

            # Waits for the current number of running jobs to be
            # less than the maximum number of concurrent jobs
            while [[ ${#job_ids[@]} -ge $max_concurrent_jobs ]] ; do
                # Check once per minute if there are any open slots
                sleep 60
                # We check for the job name, and make sure that squeue prints
                # the full job name up to 100 characters
                job_count=$(squeue --name=$job_name --Format=name:100 | grep $job_name | wc -l)
                if [[ $job_count -lt $max_concurrent_jobs ]]; then
                    break
                fi
            done

            # Some logging for the 
            for job_id in "${job_ids[@]}"; do
                if squeue -j $job_id 2>/dev/null | grep -q $job_id; then
                    continue
                else
                    job_ids=(${job_ids[@]/$job_id})
                    echo "Job $job_id has finished or exited."
                fi
            done

            # This output will be of the form "Submitted batch job 123456"
            job_output=$(sbatch --job-name=${job_name} \
                --output="${log_file}" \
                --error="${log_file}" \
                $running_script_name \
                    "$alpha_poc" \
                    "$alpha_wp" \
                    "$cohesion_poc" \
                    "$cohesion_wp" \
                    "$candidates" \
                    "$n_elections" \
                    "$output_file" \
                    "$log_file"
            )
            # Extract the job id from the output. The awk command
            # will print the last column of the output which is
            # the job id in our case
            # 
            # Submitted batch job 123456
            #                     ^^^^^^
            job_id=$(echo "$job_output" | awk '{print $NF}')
            echo "Job output: $job_output"
            # Now we add the job id to the list of running jobs
            job_ids+=($job_id)
            # Increment the job index. Bash allows for sparse
            # arrays, so we don't need to worry about any modular arithmetic
            # nonsense
            job_index=$((job_index + 1))
        done
    done
done
done

# This is just a helpful logging line to let us know that all jobs have been submitted
# and to tell us what is still left to be done
printf "No more jobs need to be submitted. The queue is\n%s\n" "$(squeue --name=$job_name)"
# Check once per minute until the job queue is empty
while [[ ${#job_ids[@]} -gt 0 ]]; do
    sleep 60
    for job_id in "${job_ids[@]}"; do
        if squeue -j $job_id 2>/dev/null | grep -q $job_id; then
            continue
        else
            job_ids=(${job_ids[@]/$job_id})
            echo "Job $job_id has finished or exited."
        fi
    done

    job_ids=("${job_ids[@]}")
done

echo "All jobs have finished."
