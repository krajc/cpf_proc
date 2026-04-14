#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on June 9, 2022
Kontroluje calpuff.lst subory, analyzuje runy avypluva rerun list pre jednu domenu, 
plus statistiku runov (trvanie CPU a elapsed time)
@author: p2993
"""

import os
import calendar
import pandas as pd

year = 2021
dom = 'jelsava'
prof = 'cconst'
group = 'heat'
ggroup = 'nfh'
lstdir = f'/work/users/p2993/calpuff/{dom}/harmo/{prof}/{group}/{ggroup}/lst'
inpdir = f'/users/p2993/calpuff/{dom}/harmo/{prof}/{group}/{ggroup}'
rerunfile = f'/users/p2993/calpuff/{dom}/rerun-{dom}-{group}-{ggroup}-{prof}.dat'
statfile = f'/users/p2993/calpuff/{dom}/stats-{dom}-{group}-{ggroup}-{prof}.dat'


missing = []
incomplete = []
cputimes = []
elapsedtimes = []
inpfiles = sorted(os.listdir(inpdir))

for file in inpfiles:
    body = file[:-4]
    
    if os.path.exists(f'{lstdir}/{body}.lst'):
        with open(f'{lstdir}/{body}.lst') as f:
            lns = f.readlines()
        
        if 'CPU' in lns[-1].split():
            cputimes.append(float(lns[-1].split()[2]))
            elapsedtimes.append(float(lns[-3].split()[3]))
        else:
            incomplete.append(file)
    else:
        missing.append(file)

df = pd.DataFrame(columns = ['cpu','elaps'])
df['cpu'] = cputimes
df['elaps'] = elapsedtimes
stats = pd.DataFrame(df.describe())
stats = round(stats/60,1)
stats.columns = ['CPU time (min)','Elapsed time (min)']
stats.to_csv(statfile, sep='\t')
    
with open(rerunfile, 'w') as f:
    for line in (incomplete + missing):
        f.write(f'{line}\n')


