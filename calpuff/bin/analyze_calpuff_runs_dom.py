#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on June 9, 2022
Kontroluje calpuff.lst subory, analyzuje runy avypluva rerun list pre jednu domenu, 
plus statistiku runov (trvanie CPU a elapsed time)
@author: p2993
"""

import os
import pandas as pd

year = 2024
dom = 'bb1'
group = 'heat'
ggroups = ['rd','bd','no','os']

for ggroup in ggroups:
    lstdir = f'/work/users/p2993/calpuff/{dom}/lst/{group}/{ggroup}'
    #inpdir = f'/users/p2993/cpf_proc/calpuff/{dom}/{group}/{ggroup}'
    inpdir = f'/users/p2993/dbase_calpuff/source_arb/volemarb_data/{dom}/{ggroup}'
    rerunfile = f'/users/p2993/cpf_proc/calpuff/{dom}/rerun-{group}-{ggroup}.dat'
    
    print(f"Running CALPUFF check files for domain: {dom} - {ggroup} ...\n")
    
    missing = []
    incomplete = []
    cputimes = []
    elapsedtimes = []
    
    if os.path.exists(rerunfile):
        with open(rerunfile) as f_obj:
            inpfiles = f_obj.readlines()
        
        inpfiles = list(map(lambda x:x[:-1], inpfiles))
        statfile = f'/users/p2993/cpf_proc/calpuff/{dom}/stats-{dom}-{group}-{ggroup}_rerun.dat'
        if len(inpfiles) == 0:
            exit("Rerun file is empty. Quitting execution...\n")
        
    else:
        inpfiles = sorted(os.listdir(inpdir))
        inpfiles = list(map(lambda x:x[9:], inpfiles))
        statfile = f'/users/p2993/cpf_proc/calpuff/{dom}/stats-{dom}-{group}-{ggroup}.dat'
    
    for file in inpfiles:
        body = file[:-4]
        
        if os.path.exists(f'{lstdir}/{body}.lst'):
            with open(f'{lstdir}/{body}.lst') as f:
                lns = f.readlines()
            
            if 'CPU' in lns[-1].split():
                cputimes.append(float(lns[-1].split()[2]))
                elapsedtimes.append(float(lns[-3].split()[3]))
            else:
                incomplete.append(f'{body}.inp')
        else:
            missing.append(f'{body}.inp')   
            
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
    
    print(f"{ggroup}: {len(missing)} missing files, {len(incomplete)} incomplete files \n\n")


