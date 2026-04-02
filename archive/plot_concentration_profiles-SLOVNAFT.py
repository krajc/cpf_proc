#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025-04-16
Spracovanie timeseries tabuliek a produkcia grafov z diskretnych receptorov
Bratislava Slovnaft (iba receptory mrakodrapov)
"""
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('/users/p2993/python/libs')
import plot_conc_BA
import utils_v1
import os
import numpy as np
import yaml
import re

unit = plot_conc_BA.unit_string
opis = plot_conc_BA.opis
# Dictionary s civilnymi nazvami domen:
domname = plot_conc_BA.domname
codes = utils_v1.codes
rmse = utils_v1.rmse
bias = utils_v1.bias
trim = utils_v1.trimming

year = 2021
spcs = ['PM10','PM25','NOx','SO2','C6H6']
dom = 'bratislava'
zdroje = ['slovnaft','spalovna']
#zdroj = 'spalovna'
vysky = [2,25,50,75,100,150,200, 250]
recs = ['A','B','C']
postdir = f'/users/p2993/cpf_proc/postproc/{year}/{dom}'

pics = f"/data/users/p2993/data_cpf/pics/{year}/{dom}/graphs"
if not os.path.exists(pics):
     os.makedirs(pics)

writer = pd.ExcelWriter(f'{postdir}/rec_timeseries_summary.xlsx')

# sucet prispevku Slovnaft a nova spalovna:
bigt_h = pd.DataFrame(columns=spcs, index=vysky)
bigt_d = pd.DataFrame(columns=spcs, index=vysky)
bigt_r = pd.DataFrame(columns=spcs, index=vysky)


for spc in spcs:
    d = {}
    for zdroj in zdroje:
        d[zdroj] = pd.read_excel(f'{postdir}/rec_timeseries_{zdroj}.xlsx', sheet_name=spc, index_col='Unnamed: 0')
    tot = d[zdroje[0]] + d[zdroje[1]]
    
    dht = pd.DataFrame(columns=vysky, index=tot.index)
    
    for h in vysky:
        # Maximum z trojice receptorov:
        dht[h] = list(map(lambda x,y,z: max(x, y, z),tot[f'A_{h}'],tot[f'B_{h}'],tot[f'C_{h}']))
    
    dht.to_excel(writer, sheet_name=spc)        
    
    # Maximalne hodinove hodnoty:
    dht_max = dht.max() 
    # Maximalne denne hodnoty:
    ddt_max = dht.resample('D').mean().max()  
    
    bigt_h[spc] = dht_max
    bigt_d[spc] = ddt_max
    bigt_r[spc] = dht.mean()

bigt_h.to_excel(writer, sheet_name='hour_max_tot')
bigt_d.to_excel(writer, sheet_name='day_max_tot')
bigt_r.to_excel(writer, sheet_name='ann_mean_tot')

# Pre kazdy zdroj zvlast:
big_h = {}
big_d = {}
    
for zdroj in zdroje:    
    
    big_h[zdroj] = pd.DataFrame(columns=spcs, index=vysky)
    big_d[zdroj] = pd.DataFrame(columns=spcs, index=vysky)
    
    for spc in spcs:
        
        d = pd.read_excel(f'{postdir}/rec_timeseries_{zdroj}.xlsx', sheet_name=spc, index_col='Unnamed: 0')        
        dh = pd.DataFrame(columns=vysky, index=d.index)
        
        for h in vysky:
            
            dh[h] = list(map(lambda x,y,z: max(x, y, z),d[f'A_{h}'],d[f'B_{h}'],d[f'C_{h}']))
                
        # Maximalne hodinove hodnoty:
        dh_max = dh.max() 
        # Maximalne denne hodnoty:
        dd_max = dh.resample('D').mean().max()  
        
        big_h[zdroj][spc] = dh_max
        big_d[zdroj][spc] = dd_max
    
    big_h.to_excel(writer, sheet_name='hour_max_cezo')
    big_d.to_excel(writer, sheet_name='day_max_cezo')

writer.save()

plt.style.use('bmh')
'''
plt.rcParams.update({'font.size': 10})
plt.rcParams.update({'xtick.labelsize': 10})
plt.rcParams.update({'ytick.labelsize': 10}) 
''' 
colors1 = ['blue','orange','green']
spcs1 = ['PM10', 'PM25','C6H6']
colors2 = ['purple','red']  
spcs2 =   ['NOx', 'SO2']  
    # Kreslenie:

fig, ax = plt.subplots(2,1, figsize = (10,14))

for i in range(len(spcs1)):    
    ax[0].plot(bigt_h[spcs1[i]], bigt_h.index, color=colors1[i], label=spcs1[i])
ax[0].legend(loc='upper right', fontsize=20) 
ax[0].set_ylabel('výška (m)',fontsize=15 ) 
ax[0].set_xlabel(unit('PM10'),fontsize=15 ) 
for i in range(len(spcs2)):    
    ax[1].plot(bigt_h[spcs2[i]], bigt_h.index, color=colors2[i], label=spcs2[i])
ax[1].legend(loc='upper right', fontsize=20) 
ax[1].set_ylabel('výška (m)',fontsize=15 ) 
ax[1].set_xlabel(unit('PM10'),fontsize=15 )  

plt.suptitle('Max. hodinová koncentrácia', fontsize=20)
plt.savefig(f'{pics}/1h_max_slovnaft_tot.png',dpi=300, bbox_inches='tight' )
plt.show()

fig, ax = plt.subplots(2,1, figsize = (10,14))

for i in range(len(spcs1)):    
    ax[0].plot(bigt_d[spcs1[i]], bigt_d.index, color=colors1[i], label=spcs1[i])
ax[0].legend(loc='upper right', fontsize=20) 
ax[0].set_ylabel('výška (m)',fontsize=15 ) 
ax[0].set_xlabel(unit('PM10'),fontsize=15 ) 
for i in range(len(spcs2)):    
    ax[1].plot(bigt_d[spcs2[i]], bigt_d.index, color=colors2[i], label=spcs2[i])
ax[1].legend(loc='upper right', fontsize=20) 
ax[1].set_ylabel('výška (m)',fontsize=15 ) 
ax[1].set_xlabel(unit('PM10'),fontsize=15)  

plt.suptitle('Max. denná koncentrácia',fontsize=20)
plt.savefig(f'{pics}/1d_max_slovnaft_tot.png',dpi=300, bbox_inches='tight' )
plt.show()





