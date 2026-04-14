#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 09:22:18 2022

Tento skript submituje zakladny (prvy) run CALPUFF pre urcitu group a ggroup
zdrojov. 
Dec 12, 2022: Pridane TMPDIR do  /scratch na prislusnom node

@author: p2993
"""

import subprocess
import os

dom = 'ruzomberok'
group = 'heat'
ggroup = 'fh'
hdir = f'/users/p2993/cpf_proc/calpuff/{dom}/{group}/{ggroup}'
memory = '5GB'
scratchdir = "/scratch"
tmpdir = f'{scratchdir}/p2993/tmp'
    
inpfiles = sorted(os.listdir(f'{hdir}'))

slurmdir = f'/work/users/p2993/calpuff/{dom}/submit/{group}/{ggroup}'
if not os.path.exists(slurmdir):
    os.makedirs(slurmdir)
logdir = f'/work/users/p2993/calpuff/{dom}/logs/{group}/{ggroup}'
if not os.path.exists(logdir):
    os.makedirs(logdir)
    
line1 = "#!/bin/bash\n"

i=1
for file in inpfiles:
    
    args = ['sbatch','--partition=user','--ntasks=1',f'--mem={memory}',
            '--time=20:00:00']
    slurmscript = f"{slurmdir}/submit-{i}.sh"
    body = file[:-4]
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name={body}\n")
        f.write(f"#SBATCH --output={logdir}/{body}.log\n" )
        f.write(f"export TMPDIR={tmpdir}")
        f.write(f"\ncalpuff {hdir}/{file}\n")
    i = i+1
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    
 