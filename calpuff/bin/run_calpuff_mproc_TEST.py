#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Dec 2, 2022:
Spustanie (submitovanie) calwrf a calmet pomocou calwrf_calmet_mproc.py.
Dec 7, 2022:
Pokial existuje rerun file (vyprodukovany v check_file_sizes.py),
spusti iba tereminy v rerun file. Inak spusti cely rok (365 dni)

@author: p2993
"""

import subprocess
import os

dom = 'ruzomberok'
year = 2021
group = 'heat'
ggroup = 'nfh'
timeout = '20:00:00'
submitdir = '/users/p2993/cpf_proc/calpuff'
logdir = f'/work/users/p2993/calpuff/{dom}/logs'
rerunfile = f'{submitdir}/rerun{year}_{dom}_{group}_{ggroup}.inp'
sourcedir = f'/data/oko/krajc/dbase_calpuff/source_arb'
volemdir = f'{sourcedir}/{dom}/{ggroup}'
files = sorted(os.listdir(f'{volemdir}'))

exe = f"\n{submitdir}/bin/calpuff_mproc_{group}_TEST.py"

if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        sources = f_obj.readlines()
        cpus = len(sources)
        tag = "_rerun"
else:
    cpus = 40
    tag = ''
    
if not os.path.exists(logdir):
    os.makedirs(logdir)
     
# Velkost "davky" na procesor:
batchsize = 40
nnodes = len(files)//batchsize + 1

for i in range(nnodes):    
    line1 = "#!/bin/bash\n"
        
    args = ["sbatch"]
    slurmscript = f"{submitdir}/submit-batch{i}-{dom}-{group}-{ggroup}{tag}.sh"
    
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name={dom}_{ggroup}_{i}\n")
        f.write("#SBATCH --partition=user\n")
        f.write(f"#SBATCH --output={logdir}/{dom}_{year}_{ggroup}{tag}_{i}.log\n" )
        f.write(f"#SBATCH --cpus-per-task={cpus}\n")
        f.write("#SBATCH --mem-per-cpu=4GB\n")
        f.write(f"#SBATCH --time={timeout}\n")
        f.write(f"{exe} {dom} {group} {ggroup} {batchsize} {i}\n")
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    
 