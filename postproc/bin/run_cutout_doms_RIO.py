#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""


@author: p2993
"""

import subprocess
import os
import time

doms = ['po1', 'po2', 'po3', 'ke1', 'ke2', 'ke3']
year = 2024

timeout = '23:00:00'
#disk = "/data/oko/krajc"      # alebo:
disk = "/data/users/p2993"
submitdir = '/users/p2993/cpf_proc/postproc'
logdir = f'{submitdir}/logs'
    
if not os.path.exists(submitdir):
    os.makedirs(submitdir)
if not os.path.exists(logdir):
    os.makedirs(logdir)
     
exe = "/users/p2993/cpf_proc/postproc/bin/cutout_doms_RIO.py"

for dom in doms:    
    line1 = "#!/bin/bash\n"
        
    args = ["sbatch"]
    slurmscript = f"{submitdir}/RIO_cutout_{dom}.sh"
    
    with open(slurmscript, 'w') as f:
        f.write(line1)
        f.write(f"#SBATCH --job-name=rio_{dom}\n")
        f.write("#SBATCH --partition=long\n")
        f.write(f"#SBATCH --output={logdir}/RIO_cutout_{dom}.log\n" )
        f.write("#SBATCH --cpus-per-task=1\n")
        f.write("#SBATCH --mem-per-cpu=5GB\n")
        f.write(f"#SBATCH --time={timeout}\n")
        f.write(f"{exe} {dom} \n")
    
    subprocess.run(['chmod','+x',slurmscript])
    args.append(slurmscript)
    output = subprocess.run(args, capture_output=True, text=True)
    print (output.stderr)
    print (output.stdout)
    time.sleep(2)
    
 
