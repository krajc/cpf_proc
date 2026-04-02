#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vykreslovanie grafov 
@author: p2993
2023-09-20:
    Zmena skriptu plot_daily_SA_graphs.py: namiesto modulu na spracovanie textovych timeseries dat
    je funkcia sample_grid, ktora interpoluje gridove data do bodov stanic
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
import xarray as xr

unit = plot_conc_BA.unit_string
opis = plot_conc_BA.opis
# Dictionary s civilnymi nazvami domen:
domname = plot_conc_BA.domname
codes = utils_v1.codes
rmse = utils_v1.rmse
bias = utils_v1.bias
trim = utils_v1.trimming

ggroups = {
    'heat':['fh','nfh'],
    'neis':['annual','seasonal','fugitive'],
    'road':[]
    }

year = 2021
spcs = ['PM10','PM25','NO2','BaP']

# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','jelsava','zarnovicanb','martin','prievidza', 
            'bratislava', 'kosice']
doms = ['martin'] 
#doms = ['trencin','prievidza']
doms = ['kosice']
#doms = ['ruzomberok','zilina']
#doms = ['hnusta','jelsava','juznyhont', 'zarnovicanb','zvolen','krompachy']
#doms = ['kysuce']  POZOR! nEMAME  odlozene timeseries  pre kysuce
nofugitive = ['martin','povazie','pohronie','hnusta','spis','trencin']



def sample_grid(dom, group, spc, rec, eolcodes):
    if group == 'neis' and dom == 'kosice':
        ncfile = f"/data/users/p2993/data_cpf/netcdf/{dom}/{dom}-{year}-{group}-corr.nc"
    else:
        ncfile = f"/data/users/p2993/data_cpf/netcdf/{dom}/{dom}-{year}-{group}.nc"
    grd = xr.open_dataset(ncfile)
    s = pd.DataFrame(columns=eolcodes, index=pd.date_range(start=f'{year}-01-01 01:00:00', end=f'{year}-12-31 22:00:00',freq='1H'))
    for i in rec.index:
         xy = grd[spc].interp(x=rec['x'][i]*1000, y=rec['y'][i]*1000, method='linear').to_dataframe()
         s[rec['EolStationCode'][i]] = xy[spc]
    return(s.resample('D').mean())
         
def process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily):
    
    # Cesta k vstupom:
    #atmodir = "/data/users/p6065/atmostreet/Results/DOM_2021_zilinsky_kraj/SectorContribution"
    if dom == 'ruzomberok':
        atmodir = "/data/users/p6065/atmostreet/Results/Ruzomberok_2021_Traffic/SectorContribution"
    elif dom == 'banskabystrica':
        atmodir = "/data/users/p6065/atmostreet/Results/BanskaBystrica_2021_Traffic/SectorContribution"
    elif dom == 'zilina':
        atmodir = "/data/users/p6065/atmostreet/Results/Zilina_2021_Traffic/SectorContribution"
    else:
        atmodir = "/data/users/p6065/atmostreet/Results/SR_2021_traffic_fixed/SectorContribution"
    datafile = {}
    datafile['road'] = f"{atmodir}/{spc.upper()}_Traffic_hourly.csv"
    datafile['backg'] = f"/data/users/p2993/data_cpf/rio/{dom}/minpoint_tseries{suff}.csv"
    
    
    pics = f"/data/users/p2993/data_cpf/pics/{dom}/graphs"
    if not os.path.exists(pics):
         os.makedirs(pics)
    
            
    # Procesing tseries:
    # AMS:
    ams_monthly = ams_daily.resample('M').mean()
    # backg:
    backg = pd.read_csv(f"{datafile['backg']}", index_col='times')
    backg.index = pd.to_datetime(backg.index) 
    
    # heat, neis (v CALPUFFe moze byt viac DR ako AMS pre konkretne spc):
    eolcodes = list(rec['EolStationCode'])
    if spc == 'NO2':
        spccpf = 'NOx'
    else:
        spccpf = spc
    heat_daily = sample_grid(dom, 'heat', spccpf, rec, eolcodes)
    neis_daily = sample_grid(dom, 'neis', spccpf, rec, eolcodes)
    
    # road:
    
    #if spc=='BaP' and atmodir == "/data/users/p6065/atmostreet/Results/SR_2021_traffic/pureSectors" :
    if spc=='BaP':
        datename = 'Unnamed: 0'
    else:
        datename = 'date'
    
    road_df = pd.read_csv(f"{datafile['road']}", index_col=datename)
    road_df.index = pd.to_datetime(road_df.index)
    #road_df = road_df.drop(columns=['Unnamed: 0'], axis=1)
    road_daily = road_df[eoi].resample('D').mean()
    if spc == 'BaP':
        road_daily = road_daily/1000
    
    # tabulka SA:
    
    if spc == 'BaP':
        # ams pozadovky:
        backg_daily = amsr_daily[['SK0006R']].astype(np.float64)
    else:
        backg_daily = backg[[spc]].astype(np.float64)
    
    for ii in eoi.keys():
    
        sa_daily = pd.concat([backg_daily, heat_daily[[ii]], road_daily[[ii]], neis_daily[[ii]]], axis=1)
        sa_daily = sa_daily[sa_daily.index.year == year]
        #sa_daily = sa_daily.drop(['2022-01-01'],axis=0)
            
        sa_monthly = sa_daily.resample('M').mean()
        sa_monthly.columns = ['Regionálne pozadie', 'Lokálne vykurovanie','Cestná doprava', 'NEIS']  
        
        sa_daily['model'] = sa_daily.sum(axis=1)
        sa_daily['ams'] = ams_daily[ii].astype(float) 
        
        if spc == 'PM10':
            sa_daily['limit'] = 50.0
            sa_daily.columns = ['Regionálne pozadie', 'Lokálne vykurovanie', 'Cestná doprava','NEIS',  \
                                    'Model','AMS', 'Limitná hodnota' ]
        else:
            sa_daily.columns = ['Regionálne pozadie', 'Lokálne vykurovanie', 'Cestná doprava','NEIS',  \
                                    'Model','AMS']
        
        plt.rcParams.update({'font.size': 10})
        plt.rcParams.update({'xtick.labelsize': 10})
        plt.rcParams.update({'ytick.labelsize': 10})  
        colorsD = ['blue','orange','green','red','purple','brown','black']
        colorsM = ['blue','orange','green','red']  
        
        # Kreslenie:
        
        # Denne grafy  
        if spc != 'BaP':
            figname = f"{pics}/interp_sa_daily-{ii}-{spc}{suff}.png"
            title = f"Príspevky jednotlivých skupín zdrojov k priemerným denným koncentráciám {spc}\
                \n{eoi[ii]}\n"
        
            ax = sa_daily.plot(figsize=(15,5), title=title, rot=45, legend=False, color=colorsD)
            ax.legend(ncol=2, fontsize=12,loc='upper center',bbox_to_anchor=(0.5,0.98),shadow=True)
            ax.set_ylabel(unit(spc))
            ax.set_xlabel('')
            plt.savefig(figname, dpi=300, bbox_inches='tight')
            plt.show()
        
        # Mesacne grafy
        mnths = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        sa_monthly.index = mnths
        figname = f'{pics}/interp_sa_monthly_{ii}-{spc}-corr{suff}.png'
        title = f"Príspevky jednotlivých skupín zdrojov k priemerným mesačným koncentráciám {spc}\
            \n{eoi[ii]}\n"
        ax = sa_monthly.plot(figsize = (10, 5), kind='bar', stacked=True, \
                            title=title, rot=45, legend=False)
        ax.plot(mnths, ams_monthly[ii],linestyle='None', marker='o', color='yellow', \
                  markeredgecolor='black', label='AMS')
        ax.legend(ncol=1, fontsize=10, loc='upper center',bbox_to_anchor=(0.5,0.99), shadow=True)
        
        ax.set_xticklabels(mnths)
        ax.set_ylabel(unit(spc))
        
        plt.savefig(figname, dpi=300, bbox_inches='tight')
        plt.show()
        # Zapis SA a statistik do excelu:
        sa_daily.to_excel(writer, sheet_name=f'daily_{spc}_{ii}')
        sa_ann = sa_daily.mean()
        # Stats:
        sa_ann['r'] = sa_daily['AMS'].corr(sa_daily['Model'])
        sa_ann['rmse'] = rmse(sa_daily['Model'],sa_daily['AMS'])
        sa_ann['bias'] = bias(sa_daily['Model'],sa_daily['AMS'])
        sa_ann.to_excel(writer, sheet_name=f'annual_{spc}_{ii}')

#############################################################################
# Spracovanie AMS dat:
def process_ams(spc, rec):
    amsfile = "/data/oko/krajc/dbase_calpuff/ams.data/denne_2021_vsetkyAMS_vsetkyZL.xlsx"
    ams = pd.read_excel(amsfile, sheet_name=f"{spc.lower()}")
    ams = ams.drop([0], axis=0)
    lst = list(ams.columns)
    lst[0] = 'date'
    ams.columns = lst
    ams.set_index('date', inplace=True)
    
   
    # Vytriedim receptory z CALPUFFu podla dostupnych  AMS MERANI:
    eoi = {}
    for i in range(nrec):
        if rec['EolStationCode'][i] in ams.columns:
            eoi[rec['EolStationCode'][i]] = f"{rec['City'][i]}, {rec['Street'][i]}" 
   
    ams_daily = pd.DataFrame(index=ams.index)
    for i in eoi.keys():
        ams_daily[i] = ams[i].astype(np.float64)
    
    # Pripravim tabulku pozadovych hodnot (dolezita len pre BaP)
    amsr_daily = pd.DataFrame(index=ams.index)
    for regid in ['SK0004R','SK0006R']:
        if regid in ams.columns:
            amsr_daily[regid] = (ams[regid].astype(np.float64))
    
    return eoi, ams_daily, amsr_daily
#############################################################################    
 
for dom in doms: 
    if dom in manbackg:
        suff = '-man'
    else:
        suff = ''
    
    # Receptory stanic pouzite v CALPUFFe:
    with open(f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}/station_rec.yml') as file:
        recdict = yaml.full_load(file)
    nrec = len(recdict)
    rec = pd.DataFrame.from_dict(recdict)
    if dom == 'bratislava':
        rec = rec.drop(labels=6, axis=0)
  
    if nrec == 0:
        print (f"No AMS stations in domain: {dom}. No model time series available.\n ")
    else:
        # Zapis dennych a rocnych SA do excelu
        writer = pd.ExcelWriter(f'/data/oko/krajc/SA/SA_{dom}.xlsx')
        for spc in spcs:
            print (f"Working on domain: {dom}, spc: {spc} ....\n\n")
            # Nacitam tabulku AMS hodnot:
            eoi, ams_daily, amsr_daily = process_ams (spc, rec)
            
            
            process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily)
        
        writer.save()
    
    
    
    