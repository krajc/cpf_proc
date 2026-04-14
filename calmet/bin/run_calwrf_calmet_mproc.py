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

dom = 'zvolen'
year = 2021

partition = 'long'
disk = '/data/oko/krajc'
submitdir = '/users/p2993/cpf_proc/calmet'
logdir = f'/work/users/p2993/calmet/{dom}/logs'
rerunfile = f'{submitdir}/rerun{year}_{dom}.inp'

timeouts = {
    'user':'23:59:00',
    'long':'2-00:00:00'}

timeout = timeouts[partition]

if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        dates = f_obj.readlines()
        cpus = 40
        tag = "rerun"
else:
    cpus = 40
    tag = ''
    
if not os.path.exists(logdir):
    os.makedirs(logdir)
    
line1 = "#!/bin/bash\n"
    
args = ["sbatch"]
slurmscript = f"{submitdir}/submit-{dom}-{tag}.sh"

with open(slurmscript, 'w') as f:
    f.write(line1)
    f.write(f"#SBATCH --job-name=calmet_{dom}\n")
    f.write(f"#SBATCH --partition={partition}\n")
    f.write(f"#SBATCH --output={logdir}/{dom}_{year}_{tag}.log\n" )
    f.write(f"#SBATCH --cpus-per-task={cpus}\n")
    f.write("#SBATCH --mem-per-cpu=4GB\n")
    f.write(f"#SBATCH --time={timeout}\n")
    f.write(f"\n{submitdir}/bin/calwrf_calmet_mproc.py {dom} {disk}\n")

subprocess.run(['chmod','+x',slurmscript])
args.append(slurmscript)
output = subprocess.run(args, capture_output=True, text=True)
print (output.stderr)
print (output.stdout)
    
 