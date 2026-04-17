#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Aug 13, 2025: 
    Added vesion 5 parameters IFRADJ a ISLOPE
Jul 9, 2025:
    Pridanie parametra terrad a sposobu zadavania domenovych parametrov
    Ak je terrad = 999, pusta sa template s defaultnym terrad 1km, ako to bolo nastavene v minulosti. 
Apr 25, 2025: 
    pridanie parametra ztop }vysvetlenie vid calmet_mproc_v2.py)
Dec 2, 2022:
Spustanie (submitovanie) calwrf a calmet pomocou calwrf_calmet_mproc.py.
Dec 7, 2022:
Pokial existuje rerun file (vyprodukovany v check_file_sizes.py),
spusti iba tereminy v rerun file. Inak spusti cely rok (365 dni)

@author: p2993
"""

import subprocess
import os

'''
domset dictionary is evolving (adding new parameters that can be modified).
There is always a new template file and a new version of calmet_mproc_vX.py, 
corresponding to added parameters. calmet_proc.py used in this script is always 
linked the latest version of calmet_proc_vX.py (X corresponting to version number)
In order to keep backward compatibility, there is the dictionary domset, where new
parameters are added. If one would want to use an older version, the newly added 
parameters should be set to 999. 

'''
domset = {
    'dom': 'ruzomberok',
    'year': 2024,
    'ztop': 3000,
    'terrad': 2.5,
    'ikine': 1, 
    'ifradj': 1,
    'islope':1
}

    

partition = 'user'
#disk = '/data/oko/krajc'
disk = '/data/users/oko001'
calmetdir = '/users/oko001/cpf_proc/calmet'
#submitdir = '/users/p2993/cpf_proc/calmet'
submitdir = '/work/users/oko001/cpf_proc/calmet'
logdir = f'/work/users/oko001/cpf_proc/calmet/logs/{domset["dom"]}/logs'
rerunfile = f'{submitdir}/rerun{domset["year"]}_{domset["dom"]}.inp'
# timeouts for partitions 
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

if not os.path.exists(submitdir):
    os.makedirs(submitdir)   
    
line1 = "#!/bin/bash\n"
    
args = ["sbatch"]
slurmscript = f"{submitdir}/submit-{domset['dom']}-{tag}.sh"

with open(slurmscript, 'w') as f:
    f.write(line1)
    f.write(f"#SBATCH --job-name=calmet_{domset['dom']}\n")
    f.write(f"#SBATCH --partition={partition}\n")
    f.write(f"#SBATCH --output={logdir}/{domset['dom']}_{domset['year']}_{tag}.log\n" )
    f.write(f"#SBATCH --cpus-per-task={cpus}\n")
    f.write("#SBATCH --mem-per-cpu=4GB\n")
    f.write(f"#SBATCH --time={timeout}\n")
    f.write(f"\n{calmetdir}/bin/calmet_mproc.py {domset['dom']} {disk} {domset['year']} {domset['ztop']} {domset['terrad']} \
            {domset['ikine']} {domset['ifradj']} {domset['islope']}\n")

subprocess.run(['chmod','+x',slurmscript])
args.append(slurmscript)
output = subprocess.run(args, capture_output=True, text=True)
print (output.stderr)
print (output.stdout)
    
 