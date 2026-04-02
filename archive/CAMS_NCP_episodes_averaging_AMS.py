#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 11:56:39 2025

Skript pre ucely SA v CAMS NCP projekte
Na zaklade .xlsx suboru s casovymi radmi prispevkov v bodoch stanic (vyprodukovanym
v plot_daily_SA_graphs_epi.py) kresli grafy priemernych prispevkov za epizodu 
v bodoch AMS stanic. 
                                   
@author: p2993
"""

import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import yaml
import sys
sys.path.append('/users/p2993/python/libs')
import plot_conc_BA

unit = plot_conc_BA.unit_string


dom = 'bratislava'
epi1 = ['2023-02-06', '2023-02-07', '2023-02-08', '2023-02-09', '2023-02-10',
       '2023-02-11', '2023-02-12', '2023-02-13', '2023-02-14', '2023-02-15',
       '2023-02-16', '2023-02-17', '2023-02-18', '2023-02-19', '2023-02-20',
       '2023-02-21', '2023-02-22', '2023-02-23', '2023-02-24', '2023-02-25']
epi2 = ['2023-09-06', '2023-09-07', '2023-09-08', '2023-09-09', '2023-09-10',
       '2023-09-11', '2023-09-12', '2023-09-13', '2023-09-14']
epi = epi1
epiname = 'epi1'
road_epi = {'epi1':'BA_2023_CAMS_FEB', 'epi2':'BA_2023_CAMS_SEP'}
neis_epi = {'epi1':'feb', 'epi2':'sept'}
year = 2023
inpdir = "/data/oko/krajc/SA"
outdir = "/data/users/p2993/data_cpf/pics/2023/bratislava"

if epiname == 'epi1':
    groups = ['Regional', 'Residential', 'Road transport', 'Industry']
    colors = ['turquoise','purple','red','yellow']
    title = 'Episode 1: February 6-25, 2023\n\n'
else:
    groups = ['Regional', 'Road transport', 'Industry']
    colors = ['turquoise','red','yellow']
    title = 'Episode 2: September 6-14, 2023\n\n'
    
# AMS metadata
with open(f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}/station_rec.yml') as file:
    rec = yaml.full_load(file)

amss = {}
for lst in rec:
    amss[lst['EolStationCode']] = lst['Street']

t = pd.DataFrame(columns=groups + ['AMS'], index=amss.values())    

for ams in amss.keys():
    tab = pd.read_excel(f"{inpdir}/SA_bratislava_{epiname}.xlsx", 
                        sheet_name=f"daily_PM10_{ams}_{epiname}", index_col='Unnamed: 0')
    
    tab = tab[groups + ['AMS']].mean()
    t.loc[amss[ams]] = list(tab)


### Kreslenie

plt.rcParams.update({'font.size': 14})
plt.rcParams.update({'xtick.labelsize': 14})
plt.rcParams.update({'ytick.labelsize': 14}) 

ax = t.iloc[:,:-1].plot(figsize = (10, 5), kind='bar', stacked=True, \
                            title=title, rot=20, legend =False, color=colors)
ax.plot(t.index, t['AMS'],linestyle='None', marker='o', color='orange', markersize=10, \
                  markeredgecolor='black', label='AMS')
ax.grid(color='grey',which='both', linestyle=':', linewidth=1.0, axis='y', alpha=0.5)
ax.legend(ncol=5, fontsize=10, loc='upper center',bbox_to_anchor=(0.5,1.1))
ax.set_ylabel(unit('PM10'))

plt.savefig(f'{outdir}/{epiname}_SA_mean_AMS.png',dpi=350, bbox_inches='tight')
