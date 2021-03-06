#!/bin/bash

#SBATCH --job-name="20YEAR_MONTH"
#SBATCH -t 20:00:00
#SBATCH -p coaps_q
##SBATCH -p genacc_q
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --mem=64G
#SBATCH --mail-type=END,FAIL
##SBATCH --mail-type=ALL

module load intel openmpi

start_date_str="20YEAR-MONTH-01"
#start_date_str="2010-01-01" # Just for testing
end_date_str="2020-01-01"
output_path="/gpfs/home/osz09/scratch/globaldebris"
run_name="TenYears_YesWinds_YesDiffusion_NoUnbeaching_20YEAR_MONTH"
inc_per_run=30

# Shouldn't be necessary to modify anything after this
t=0
c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")

c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
end_date_sec=$(date --date="${end_date_str}" "+%s")

c_end_date_sec=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%s")

# Here it decides if the next end date is the final END DATE or CURRENT DATE + increment
if [ $c_end_date_sec -lt $end_date_sec ]
then
  c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
else
  c_end_date=$(date --date="${end_date_str}" "+%Y-%m-%d")
fi

while [ $c_start_date_sec -lt $end_date_sec ]
do
  echo "====================== NEW RUN t=$t ================================"
  if [ $t -eq  0 ]
  then
    # In this case it is only running inc_per_run days normally
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python GlobalModel.py ${c_start_date}:0 ${c_end_date}:0 True True False ${run_name}_${c_start_date}_${c_end_date}"
  else
    # In this case it should start from the previous locations
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python GlobalModel.py ${c_start_date}:0 ${c_end_date}:0 True True False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
  fi
  echo $cmd
#  `$cmd > 'CurrentRun20YEAR_MONTH.log'`
  t=$[$t+$inc_per_run]
  prev_start_date=$c_start_date
  prev_end_date=$c_end_date
  c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
  c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
  c_end_date_sec=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%s")
  # Here it decides if the next end date is the final END DATE or CURRENT DATE + increment
  if [ $c_end_date_sec -lt $end_date_sec ]
  then
      c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
  else
      c_end_date=$(date --date="${end_date_str}" "+%Y-%m-%d")
  fi
done

# This code is for merging the outputs of the prevoius runs
#cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 2_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
#cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 2_MergeRuns.py 2014-12-02:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
#echo $cmd
#`$cmd > 'Merge_20YEAR_MONTH.log'`

# This code is for removing all the previously generated files
#cmd="rm  ${output_path}/${run_name}_*"
#echo $cmd
#`$cmd`

# This code is for removing all temporal folders
# These are the 'temporal' folders from OP
#cmd="rm -rf ${output_path}/out-*"
#echo $cmd
#`$cmd`

