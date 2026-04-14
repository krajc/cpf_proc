#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 08:37:44 2022

@author: p2993
"""

import os
import geopandas as gpd
import yaml
import calendar

d = gpd.read_file("/users/p2993/cpf_domeny/domeny_laea/domeny_laea.shp")
doms = list(map(lambda x: x.lower(),d['dom_name']))

year = 2021
outdir = '/data/users/p2993/data_cpf/calmet'
sizefile = '/users/p2993/calmet/calmetfilesizes.yml'
rerunfile = f'/users/p2993/slurm/rerun{year}.inp'

sizes = {}
missing = []
for dom in doms:
    sizes[dom] = os.path.getsize(f'{outdir}/{dom}/{year}-01-01.dat')
    
    for month in range(1,13):
        ndays = calendar.monthrange(year, month)
        ndays = ndays[1]   
        for day in range(1, ndays+1):
            fil = f"{outdir}/{dom}/{year}-{month:02d}-{day:02d}.dat"
            if os.path.exists(fil):
                s = os.path.getsize(fil)
                if s != sizes[dom]:
                    missing.append(f'{dom} {month} {day}\n')
                    print(f'{s}, {dom} {month} {day}')
            else:
                missing.append(f'{dom} {month} {day}\n')
                print(f'{dom} {month} {day}')
            
            # Tato cas je docasna, uz je zakomponovana v create_calmet_files:
            aux = f"{outdir}/{dom}/{year}-{month:02d}-{day:02d}.dat.aux"
            if os.path.exists(aux):
                os.remove(aux)

with open(sizefile, 'w') as file:
    yaml.dump(sizes, file)

with open(rerunfile, 'w') as f:
    for line in missing:
        f.write(line)
