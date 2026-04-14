#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on 26.1.2023

Tento skript submituje rerun padnutych calpuff jobov
zdrojov. 

@author: p2993
"""

import subprocess
import os

dom = 'kosice'
group = 'heat'
ggroup = 'fh'
hdir = f'/users/p2993/cpf_proc/calpuff/{dom}/{group}/{ggroup}'
memory = '5GB'
rerunfile = f'/users/p2993/cpf_proc/calpuff/{dom}/rerun-{group}-{ggroup}.dat'
if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        inpfiles = f_obj.readlines()   

inpfiles = list(map(lambda x:x[:-1], inpfiles))

slurmdir = f'/users/p2993/cpf_proc/calpuff/{dom}/submit'
if not os.path.exists(slurmdir):
    os.makedirs(slurmdir)
logdir = f'/work/users/p2993/calpuff/{dom}/logs'
if not os.path.exists(logdir):
    os.makedirs(logdir)
    
line1 = "#!/bin/bash\n"

i=1
for file in inpfiles:
    
    args = ['sbatch','--partition=long','--ntasks=1',f'--mem={memory}',
            '--time=23:00:00']
    slurmscript = f"{slurmdir}/submit-{i}.sh"
    body = file[:-4]
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name={body}\n")
        f.write(f"#SBATCH --output={logdir}/{body}.log\n" )
        f.write(f"\ncalpuff {hdir}/{file}\n")
    i = i+1
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    
 