#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Dec 12, 2022:
    Multiproc verzia submitovania CALPUFF runov
Dec 20, 2022:
    Toto je takmer identicka verzia calpuff_mproc_heat.py, pridana je 
    iba cast ktora nahraza kompletny zoznam files podmnozinou files na 
    zaklade rerun suboru. Po otestovani moze nahradit povodny skript ako
    jeho univerzalnejsia verzia
@author: p2993
"""

import os
import sys
import yaml
import subprocess
from multiprocessing import Pool, cpu_count
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('year', type=int)
parser.add_argument('domena', type=str)
parser.add_argument('group', type=str)
parser.add_argument('ggroup', type=str)
parser.add_argument('batchsize', type=int)
parser.add_argument('batchnumber', type=int)
parser.add_argument('disk', type=str)

args = parser.parse_args()

def run_calpuff(file):
   
    print(f"Running CALPUFF {file}...\n")        
    output = subprocess.run(['calpuff',f"{cpfdir}/{file}"], capture_output=True, text=True)
    if (output.returncode != 0):
        print(f"{file}: CALPUFF error {output.stderr}\n ...exiting execution\n")
        sys.exit(1)
    
    #clean_scratch(dom, date)
    
def final_cleanup():
    if os.path.exists(f'{scratchdir}/oko001'):
        os.removedirs(f'{scratchdir}/oko001/tmp')
        #os.removedirs(f'{scratchdir}/p2993')

# nasekanie files na 40 CPU useky:
def distribution_list(origlist, batchsize):
    # looping till length of origlist
    for i in range(0, len(origlist), batchsize):
        yield origlist[i:i + batchsize]
        
start_time = time.perf_counter()

year = args.year
disk = args.disk
dom = args.domena
group = args.group
ggroup = args.ggroup
#ggroups = ('fh','nfh')
rerunfile = f'/work/users/oko001/cpf_proc/calpuff/{dom}/rerun-{group}-{ggroup}.dat'

# Vytvorenie files ak existuje rerun subor:
if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        files = f_obj.readlines()
        files = list(map(lambda x: x[9:-5]+'.inp', files))
    
   
cpfdir = '/work/users/oko001/cpf_proc/calpuff'

scratchdir = "/scratch"
wrkdir = f'{scratchdir}/oko001'
#tmpdir = f'{scratchdir}/p2993/tmp'
tmpdir = '/work/users/oko001/tmp'
cpfdir = f'/work/users/oko001/cpf_proc/calpuff/{dom}/inp/{group}/{ggroup}'
outdir = f'/work/users/oko001/data_cpf/calpuff/{year}/{dom}/{group}/{ggroup}'
lstdir = f'/work/users/oko001/cpf_proc/calpuff/{dom}/lst/{group}/{ggroup}'

# Multiprocessing:
batchlists = list(distribution_list(files, args.batchsize))
# setup local TMPDIR (kedze pool mozat iba na jednom node, staci tmpdir nasetovat tu):
os.environ['TMPDIR'] = tmpdir
#number_of_cores = cpu_count() n
number_of_cores = int(os.environ['SLURM_CPUS_PER_TASK'])   
#number_of_cores = int(os.environ['SLURM_NTASKS'])   
print(f'Number of cores: {number_of_cores}\n')
print(f'Batch number {args.batchnumber}\n')

with Pool(number_of_cores) as pool:
    pool.map(run_calpuff, batchlists[args.batchnumber])

finish_time = time.perf_counter()
cputime = (finish_time-start_time)/3600
print(f"Program finished in {cputime: .2f} hours\n")
# Removing scratchdir:
final_cleanup()

         

        
