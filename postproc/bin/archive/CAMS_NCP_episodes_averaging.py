#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 11:56:39 2025

Skript pre ucely SA v CAMS NCP projekte
Pocita domenove priemery prispevkov a vykresluje grafy za jednotlive epizody

@author: p2993
"""

import xarray as xr
import matplotlib.pyplot as plt
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
epi = epi2
epiname = 'epi2'
road_epi = {'epi1':'BA_2023_CAMS_FEB', 'epi2':'BA_2023_CAMS_SEP'}
neis_epi = {'epi1':'feb', 'epi2':'sept'}
year = 2023
inpdir = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}"
outdir = "/data/users/p2993/data_cpf/pics/2023/bratislava"
ctotal = f"/data/users/p2993/data_cpf/netcdf_groups/{year}/{dom}-{epiname}-total-man.nc"
datafile = {}
datafile['road'] = f"/data/oko/AtmostreetPostproc/{year}/{road_epi[epiname]}/Sectors/{dom}-Traffic.nc"
datafile['neis'] = f"{inpdir}/mean-{dom}-{year}-{neis_epi[epiname]}-neis.nc"
datafile['heat'] = f"{inpdir}/mean-{dom}-{year}-heat.nc"

if epiname == 'epi1':
    groups = ['road', 'neis','heat']
    title = 'Episode 1: February 6-25, 2023\n'
else:
    groups = ['road', 'neis']
    title = 'Episode 2: September 6-14, 2023\n'
    
conc = {}
for group in groups:
    conc[group] = xr.open_dataset(datafile[group])
    conc[group] = conc[group].where(conc[group] >=0)
    conc[group] = conc[group].fillna(0.0)
    
concT = xr.open_dataset(ctotal)
cT = round(float(concT.PM10.mean()),2)


# Domain mean contributions:
contrib = []
for group in groups:
    ctg = float(conc[group].PM10.mean())
    contrib.append(round(ctg, 2))

cbg = cT - sum(contrib)
contrib.append(cbg)

plt.rcParams.update({'font.size': 14})
plt.rcParams.update({'xtick.labelsize': 14})
plt.rcParams.update({'ytick.labelsize': 14})  

figure, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))

if epiname == 'epi1':
    
    dats = ax.bar(['Road transport','Industry','Residential','Regional'], contrib,  
            color=['red','yellow','purple', 'turquoise'])   
    ax.grid(color='grey',which='both', linestyle=':', linewidth=1.0, axis='y', alpha=0.5)
    ax.set_ylabel(unit('PM10'))
    ax.set_yscale('log')
    ax.set_yticks([0.1, 1, 10])
    ax.bar_label(dats, padding=3)
    ax.set_title(title)
    
    plt.savefig(f'{outdir}/Epi1_SA_mean_mean.png',dpi=350, bbox_inches='tight')
else:
    
    dats = ax.bar(['Road transport','Industry','Regional'], contrib,  
            color=['red','yellow', 'turquoise'])   
    ax.grid(color='grey',which='both', linestyle=':', linewidth=1.0, axis='y', alpha=0.5)
    ax.set_ylabel(unit('PM10'))
    ax.set_yscale('log')
    ax.set_yticks([0.1, 1, 10])
    ax.bar_label(dats, padding=3)
    ax.set_title(title)
    
    plt.savefig(f'{outdir}/Epi2_SA_mean_mean.png',dpi=350, bbox_inches='tight')
#ax.bar(['Road transport','Industry','Residential heating'], contrib[:-1],  
#        color=['red','yellow','purple']) 

#