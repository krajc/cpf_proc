#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""

@author: p2993
"""

import subprocess
import os
import time
import sys

# Specifikacia epizody
epi = ('2023-02-06','2023-02-25')
#epi = ('2023-09-06','2023-09-14')
dom = 'bratislava'
year = 2023
group = 'heat'
ggroup = 'fh'
partition = 'long'
disk = "/data/oko/krajc"      # alebo:
#disk = "/data/users/p2993"
submitdir = f'/users/p2993/cpf_proc/calpuff/{dom}/submit'
logdir = f'/work/users/p2993/calpuff/{dom}/logs'
rerunfile = f'/users/p2993/cpf_proc/calpuff/{dom}/rerun-{group}-{ggroup}.dat'
sourcedir = '/data/oko/krajc/dbase_calpuff/source_arb'
volemdir = f'{sourcedir}/{dom}/{year}/{ggroup}'
files = sorted(os.listdir(f'{volemdir}'))

timeouts = {
    'user':'23:59:00',
    'long':'5-00:00:00'}

timeout = timeouts[partition]

if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        sources = f_obj.readlines()
    ncpus = 40
    if len(sources) == 0:
        print("Rerun file is empty. Quitting execution...\n")
        sys.exit()
    tag = "_rerun"
    batchsize = 40
    nnodes = len(sources)//batchsize + 1
else:
    ncpus = 40
    tag = ''
    # Velkost "davky" na procesor:
    batchsize = 500
    nnodes = len(files)//batchsize + 1
    
if not os.path.exists(submitdir):
    os.makedirs(submitdir)
if not os.path.exists(logdir):
    os.makedirs(logdir)
     
exe = f"/users/p2993/cpf_proc/calpuff/bin/calpuff_mproc_{group}_epi{tag}.py"

for i in range(nnodes):    
    line1 = "#!/bin/bash\n"
        
    args = ["sbatch"]
    slurmscript = f"{submitdir}/batch{i}-{dom}-{group}-{ggroup}{tag}.sh"
    
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name={dom}_{ggroup}_{i}\n")
        f.write(f"#SBATCH --partition={partition}\n")
        f.write(f"#SBATCH --output={logdir}/{dom}_{year}_{ggroup}{tag}_{i}.log\n" )
        f.write(f"#SBATCH --cpus-per-task={ncpus}\n")
        f.write("#SBATCH --mem-per-cpu=4GB\n")
        f.write(f"#SBATCH --time={timeout}\n")
        f.write(f"{exe} {dom} {group} {ggroup} {batchsize} {i} {disk} {epi[0]} {epi[1]}\n")
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    time.sleep(5)
    
 