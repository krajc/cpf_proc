#!/bin/bash

#SBATCH --job-name=pool_test
#SBATCH --partition=user          
#SBATCH --mail-type=FAIL         
##SBATCH --ntasks=10
#SBATCH --cpus-per-task=80
#SBATCH --time=04:00:00         
##SBATCH --nodes=2
#SBATCH --mem-per-cpu=1GB             
#SBATCH --output=/users/p2993/cpf_proc/calmet/bin/tmp/pool.log
/users/p2993/cpf_proc/calmet/bin/maly_test_pool.py

