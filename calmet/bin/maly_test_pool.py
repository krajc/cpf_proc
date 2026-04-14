#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 15:56:46 2022

@author: p2993
"""

import os
import time
from multiprocessing import Pool, cpu_count

start_time = time.perf_counter()

# function you want to run in parallel:
def myfunction(a):
    print(f'Processing parameter: {a}\n')
    time.sleep(60)
    return a*a

# list of tuples to serve as arguments to function:
args = list(range(80))

# number of cores you have allocated for your slurm task:
number_of_cores = int(os.environ['SLURM_CPUS_PER_TASK'])
#number_of_cores = int(os.environ['SLURM_NTASKS'])

#
#number_of_cores = cpu_count() # if not on the cluster you should do this instead
print(f"Number of cores: {number_of_cores}\n")

# multiprocssing pool to distribute tasks to:
with Pool(number_of_cores) as pool:
    # distribute computations and collect results:
    results = pool.map(myfunction, args)
    
finish_time = time.perf_counter()
cputime = finish_time-start_time
print(f"Program finished in {cputime: .0f} seconds\n")