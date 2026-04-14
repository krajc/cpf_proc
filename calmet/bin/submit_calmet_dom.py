#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 09:22:18 2022

Tento skript submituje skript  create_calmet_files_new.py - vytvara submit.sh
jednotlivo pre domenu a den, teda 365 jobov. Jeden submit bezi OK a rychlo, 
ale vsetky naraz zahltia filesystem I/O operaciami, az padaju nody a oper joby.
Preto som urobila aj sekvencny create_calmet_files_seq.py, ktory skpusti 
vsetky dni za sebou a spusta sa pomocou ~/slurm/bin/calmet_seq.sh ako jeden job

@author: p2993
"""

import subprocess
import os
import pandas as pd

dom = 'velka_ida'
year = 2021
hdir = '/users/p2993/calmet/bin'
memory = '5GB'

slurmdir = f'/work/users/p2993/calmet/{dom}/submit'
whattorun = f'{hdir}/create_calmet_files_new.py'
if not os.path.exists(slurmdir):
    os.makedirs(slurmdir)
logdir = f'/work/users/p2993/calmet/{dom}/logs'
if not os.path.exists(logdir):
    os.makedirs(logdir)
    
line1 = "#!/bin/bash\n"

# generate day lists:
idx = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31',freq='1D')

for d  in idx:
    dd = f'{d.day:02d}'
    mm = f'{d.month:02d}'
    args = ['sbatch','--partition=user','--ntasks=1',f'--mem={memory}',
            '--time=03:00:00']
    slurmscript = f"{slurmdir}/submit-{mm}-{dd}.sh"
    
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name={dom}-{mm}-{dd}\n")
        f.write(f"#SBATCH --output={logdir}/{dom}-{mm}-{dd}.log\n" )
        f.write(f"{whattorun} {dom} {mm} {dd}\n")
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    
 