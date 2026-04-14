#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025-04-16
Skript na extrahovanie timeseries z diskretnych receptorov v domene. V tomto pripade
specialne pre Slovnaft, ide len o mrakodrapy.
nasledny plot_timeseries_graphs_SLOVNAFT.py bude vykreslovat grafy
"""
import pandas as pd
import sys
import os
import numpy as np
import yaml
import re


year = 2021
spcs = ['PM10','PM25','NOx','SO2','C6H6']
maindir = f"/data/users/p6278/calpost/{year}/bratislava/neis/timeseries"
zdroj = 'slovnaft'
#zdroj = 'spalovna'
#spcs = ['BaP']
# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','jelsava','zarnovicanb','martin','prievidza', 'bratislava']
dom = 'bratislava'

datadir = f"{maindir}/{zdroj}"



#############################################################################
#### Vygenerovanie nazvov receptorov mrakodrapov:   
r = ['A','B','C']
v = [2,25,50,75,100,150,200, 250]
n = []
for i in v:
    for j in r:
        n.append(f"{j}_{i}")
##########################
    
if dom in manbackg:
    suff = '-man'
else:
    suff = ''
    
# Receptory stanic pouzite v CALPUFFe (normalny beh, vsetky NEIS):
with open(f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}/station_rec.yml') as file:
    rec = yaml.full_load(file)
nrec = len(rec)

# Receptory pouzite pre Slovnaft
recfile = '/data/oko/katka/point_sources/bratislava/drec_file.dat'
with open(recfile) as f:
    cely = f.readlines()
mr = cely[-24:]    
nrec = len(mr)

# Zapis hodinovych, dennych a rocnych prispevkov do excelu
postdir = f'/users/p2993/cpf_proc/postproc/{year}/{dom}'
if not os.path.exists(postdir):
    os.makedirs(postdir)
writer = pd.ExcelWriter(f'{postdir}/rec_timeseries_{zdroj}.xlsx')
    
idx = pd.date_range(start=f'{year}-01-01 01:00:00', end=f'{year}-12-31 22:00:00',freq='1H')

for spc in spcs:
    print (f"Working on domain: {dom}, spc: {spc} ....\n\n")
    
    cpfspc = spc.lower()

# Nacitanie a uprava timeseries 

    if os.path.exists(f"{datadir}/tseries_{cpfspc.lower()}_1hr_conc.dat"):
        with open (f"{datadir}/tseries_{cpfspc.lower()}_1hr_conc.dat") as f_obj:
            al = f_obj.readlines()
    # Po odseparovani hlavicky mame zoznam riadkov v textovom tvare:
    al = al[14:]
    # Poslednych nrec udajov v kazdom riadku su receptory mrakodrapov. Vytvorim z nich tabulku:
    
    rctab = pd.DataFrame(columns=list(range(nrec)), index=idx)
    i = 0
    for ind in idx:
        recs = re.split('\s+',al[i].strip())
        rctab.loc[ind] = recs[-nrec:]
        i = i+1
    rctab = rctab.astype(np.float64)
    rctab.columns = n
    rctab.to_excel(writer, sheet_name=spc)
      
writer.save()
    
    
    
    