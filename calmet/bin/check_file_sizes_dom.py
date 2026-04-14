#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 08:37:44 2022
Kontroluje calmet.dat subory a vypluva rerun list pre jednu domenu
@author: p2993
"""

import os

import yaml
import calendar

year = 2024
dom = 'ruzomberok'
#disk =  '/data/users/p2993'
disk = '/data/oko/krajc'
outdir = f'{disk}/data_cpf/calmet/{year}a'             # !!!!!!!!!!!!!!!!!!!!!!
sizefile = f'/users/p2993/cpf_proc/calmet/calmetfilesize_{dom}.yml'
rerunfile = f'/users/p2993/cpf_proc/calmet/rerun{year}_{dom}.inp'

print(f"Running CALMET check files for domain: {dom} ...\n")

size={}
sizes = []
for file in  os.listdir(f'{outdir}/{dom}')[:10]:
    sizes.append(os.path.getsize(f'{outdir}/{dom}/{file}'))
size[dom] = max(sizes)

missing = []

for month in range(1,13):
    ndays = calendar.monthrange(year, month)
    ndays = ndays[1]   
    for day in range(1, ndays+1):
        fil = f"{outdir}/{dom}/{year}-{month:02d}-{day:02d}.dat"
        if os.path.exists(fil):
            s = os.path.getsize(fil)
            if s != size[dom]:
                missing.append(f'{year}-{month:02d}-{day:02d}\n')
                print(f'{s}, {dom} {month} {day}')
        else:
            missing.append(f'{year}-{month:02d}-{day:02d}\n')
            print(f'{dom} {month} {day}')
        
        # Tato cas je docasna, uz je zakomponovana v create_calmet_files:
        aux = f"{outdir}/{dom}/{year}-{month:02d}-{day:02d}.dat.aux"
        if os.path.exists(aux):
            os.remove(aux)

with open(sizefile, 'w') as file:
    yaml.dump(size, file)

with open(rerunfile, 'w') as f:
    for line in missing:
        f.write(line)
