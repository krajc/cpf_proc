#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Dec 1, 2022:
Spustanie (submitovanie) calwrf a calmet, predtym uz musia byt pripravene
.inp subory v create_inp_files_only.py

@author: p2993
"""

import subprocess
import os
import pandas as pd
import time

start_time = time.perf_counter()

dom = 'ruzomberok'
year = 2021
clmdir = f'/users/p2993/cpf_proc/calmet/{dom}'
cwrdir = f'/users/p2993/cpf_proc/calwrf/{dom}'
memory = '4GB'

idx = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31',freq='1D')
dates = list(map(lambda x:str(x)[:10], idx ))    


slurmdir = f'/work/users/p2993/calmet/{dom}/submit'
if not os.path.exists(slurmdir):
    os.makedirs(slurmdir)
logdir = f'/work/users/p2993/calmet/{dom}/logs'
if not os.path.exists(logdir):
    os.makedirs(logdir)
    
line1 = "#!/bin/bash\n"


i=1
for date in dates[:40]:
    
    args = ['sbatch','--partition=user','--ntasks=1',f'--mem={memory}',
            '--time=03:00:00']
    slurmscript = f"{slurmdir}/submit-{i}.sh"
    
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name=day_{date}\n")
        f.write(f"#SBATCH --output={logdir}/{date}.log\n" )
        f.write ("\nmkdir -p /scratch/p2993\n")
        f.write(f"calwrf {cwrdir}/{date}.inp\n")
        f.write(f"calmet_ifort {clmdir}/{date}.inp\n")
    i = i+1
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    
 