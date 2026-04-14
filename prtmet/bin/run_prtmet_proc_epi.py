#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Submitovanie prtmet_proc.py

@author: p2993
"""

import subprocess
import os

dom = 'bratislava'
year = 2023
timeout = '20:00:00'
# adresar pre zapis submitovacieho skriptu:
submitdir = '/users/p2993/cpf_proc/prtmet'
# adresar pre logy:
logdir = f'/work/users/p2993/prtmet/{dom}/logs'

# Pocet pozadovanych vypoctovych jadier:
cpus = 1
    
if not os.path.exists(logdir):
    os.makedirs(logdir)

# Vytvorenie a zapis submitovacieho skriptu:
line1 = "#!/bin/bash\n"
    
args = ["sbatch"]
# Submitovaci skript - zapis:
slurmscript = f"{submitdir}/submit-{dom}.sh"

with open(slurmscript, 'w') as f:
    f.write(line1)
    f.write(f"#SBATCH --job-name=metproc_{dom}\n")
    f.write("#SBATCH --partition=user\n")
    f.write(f"#SBATCH --output={logdir}/{dom}_{year}.log\n" )
    f.write(f"#SBATCH --cpus-per-task={cpus}\n")
    f.write("#SBATCH --mem-per-cpu=4GB\n")
    f.write(f"#SBATCH --time={timeout}\n")
    f.write(f"\n{submitdir}/bin/prtmet_proc_epi.py {dom}\n")

# Pridanie exe prava na skript:
subprocess.run(['chmod','+x',slurmscript])

# Spustenie  skriptu do queue: 
args.append(slurmscript)
output = subprocess.run(args, capture_output=True, text=True)
print (output.stderr)
print (output.stdout)
    
 