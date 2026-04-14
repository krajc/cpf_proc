#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


Vykreslovanie grafov 
@author: p2993
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

ggroups = {
    'heat':['fh','nfh'],
    'neis':['annual','seasonal','fugitive'],
    'road':[]
    }

year = 2021
spcs = ['PM10','PM25','NO2','BaP']

stdict = {
    'ruzomberok':['SK0008A'],
    'zilina':['SK0020A'],
    'martin': ['SK0039A'],
    'kysuce': ['SK0071A'],
    'orava': ['NoCode-88203'],
    'povazie':[],
    'kosice':['SK0018A','SK0267A','SK0264A'],
    'krompachy':['SK0265A']
    }
doms = ['martin','ruzomberok','zilina','orava','povazie'] 
doms = ['krompachy']

nofugitive = ['martin','povazie']

def sum_cpf_group(dom, group, spc, nrec):
    al = {}
    rctab = {}
    idx = pd.date_range(start=f'{year}-01-01 01:00:00', end=f'{year}-12-31 22:00:00',freq='1H')
    if spc == 'NO2':
        cpfspc = 'nox'
    else:
        cpfspc = spc.lower()
    datadir = f"/data/users/p2993/data_cpf/netcdf/{dom}/{group}/timeseries"
    # Nacitanie a uprava timeseries pre ggroups
    for ggroup in ggroups[group]:
        if os.path.exists(f"{datadir}/{ggroup}/tseries_{cpfspc.lower()}_1hr_conc.dat"):
            with open (f"{datadir}/{ggroup}/tseries_{cpfspc.lower()}_1hr_conc.dat") as f_obj:
                al[ggroup] = f_obj.readlines()
            # Po odseparovani hlavicky mame zoznam riadkov v textovom tvare:
            al[ggroup] = al[ggroup][14:]
            # Poslednych nrec udajov v kazdom riadku su receptory stanic. Vytvorim z nich tabulku:
            
            rctab[ggroup] = pd.DataFrame(columns=list(range(nrec)), index=idx)
            i = 0
            for ind in idx:
                recs = re.split('\s+',al[ggroup][i].strip())
                rctab[ggroup].loc[ind] = recs[-nrec:]
                i = i+1
            rctab[ggroup] = rctab[ggroup].astype(np.float64)
    # Scitanie timeseries za groups:
    if group == 'heat':
        rcdf = rctab['fh'] + rctab['nfh']
    else:
        if dom in nofugitive:
            rcdf = rctab['annual'] + rctab['seasonal']
        else:
            rcdf =  rctab['annual'] + rctab['seasonal'] + rctab['fugitive']
    
    return(rcdf.resample('D').mean())
         
def process_domain(dom, spc):
    
    # Cesta k vstupom:
    #atmodir = "/data/users/p6065/atmostreet/Results/DOM_2021_zilinsky_kraj/SectorContribution"
    if dom == 'ruzomberok':
        atmodir = "/data/users/p6065/atmostreet/Results/Ruzomberok_2021_Traffic/SectorContribution"
    elif dom == 'banskabystrica':
        atmodir = "/data/users/p6065/atmostreet/Results/BanskaBystrica_2021_Traffic/SectorContribution"
    else:
        atmodir = "/data/users/p6065/atmostreet/Results/SR_2021_traffic/pureSectors"
    datafile = {}
    datafile['road'] = f"{atmodir}/{spc.upper()}_Traffic_hourly.csv"
    datafile['backg'] = f"/data/users/p2993/data_cpf/rio/{dom}/minpoint_tseries.csv"
    datafile['ams'] = "/data/oko/krajc/dbase_calpuff/ams.data/denne_2021_vsetkyAMS_vsetkyZL.xlsx"
    
    pics = f"/data/users/p2993/data_cpf/pics/{dom}/graphs"
    if not os.path.exists(pics):
         os.makedirs(pics)
    
    eoi = stdict[dom]
    
    # Spracovanie AMS dat:
    ams = pd.read_excel(f"{datafile['ams']}", sheet_name=f"{spc.lower()}")
    ams = ams.drop([0], axis=0)
    lst = list(ams.columns)
    lst[0] = 'date'
    ams.columns = lst
    ams.set_index('date', inplace=True)
    ams_daily = pd.DataFrame(index=ams.index)
    for i in eoi:
        if i in lst:
            ams_daily[i] = ams[i].astype(np.float64)
        else:
            ams_daily[i] = np.nan
    ams_monthly = ams_daily.resample('M').mean()
        
    # ams meta:
    amsm = pd.read_excel(f"{datafile['ams']}", sheet_name="PM10".lower(), nrows=1)
    amsm.drop(columns=['EOI'], axis=1, inplace=True)
    amsm = amsm.transpose()
    amsm.columns = ['name']
        
    # Procesing tseries:
    
    # backg:
    backg = pd.read_csv(f"{datafile['backg']}", index_col='times')
    backg.index = pd.to_datetime(backg.index) 
    
    # heat, neis:
    # Receptory stanic pouzite v CALPUFFe:
    with open(f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}/station_rec.yml') as file:
        rec = yaml.full_load(file)
    nrec = len(rec)
    eoicodes = list(map(lambda x: x['EolStationCode'], rec))
    eoinames = list(map(lambda x: x['Street'], rec))
    heat_daily = sum_cpf_group(dom, 'heat', spc, nrec) 
    neis_daily = sum_cpf_group(dom, 'neis', spc, nrec)
    heat_daily.columns = eoicodes
    neis_daily.columns = eoicodes
    # road:
    if spc=='BaP':
        icolname = 'Unnamed: 0'
    else:
        icolname = 'date'
    road_df = pd.read_csv(f"{datafile['road']}", index_col=icolname)
    road_df.index = pd.to_datetime(road_df.index)
    #road_df = road_df.drop(columns=['Unnamed: 0'], axis=1)
    road_daily = road_df[eoi].resample('D').mean()
    if spc == 'BaP':
        road_daily = road_daily/1000
    
    # tabulka SA:
    
    if spc == 'BaP':
        # ams pozadovky:
        amsr_daily = ams[['SK0004R','SK0006R']].astype(np.float64)
        backg_daily = amsr_daily[['SK0006R']].astype(np.float64)
    else:
        backg_daily = backg[[spc]].astype(np.float64)
    
    for ii in eoi:
    
        sa_daily = pd.concat([backg_daily, heat_daily[[ii]], road_daily[[ii]], neis_daily[[ii]]], axis=1)
        sa_daily = sa_daily.drop(['2022-01-01'],axis=0)
            
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
        
        if ii in list(amsm.index):
            nejm = amsm['name'][ii]
        else:
            nejm = dom.upper()
        
        # Denne grafy  
        if spc != 'BaP':
            figname = f"{pics}/sa_daily-{eoi[0]}-{spc}.png"
            title = f"Príspevky jednotlivých skupín zdrojov k priemerným denným koncentráciám {spc}\
                \n{nejm}\n"
        
            ax = sa_daily.plot(figsize=(15,5), title=title, rot=45, legend=False, color=colorsD)
            ax.legend(ncol=2, fontsize=12,loc='upper center',bbox_to_anchor=(0.5,0.98),shadow=True)
            ax.set_ylabel(unit(spc))
            ax.set_xlabel('')
            plt.savefig(figname, dpi=300, bbox_inches='tight')
            plt.show()
        
        # Mesacne grafy
        mnths = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        sa_monthly.index = mnths
        figname = f'{pics}/sa_monthly_{ii}-{spc}.png'
        title = f"Príspevky jednotlivých skupín zdrojov k priemerným mesačným koncentráciám {spc}\
            \n{nejm}\n"
        ax = sa_monthly.plot(figsize = (10, 5), kind='bar', stacked=True, \
                            title=title, rot=45, legend=False)
        ax.plot(mnths, ams_monthly[ii],linestyle='None', marker='o', color='yellow', \
                  markeredgecolor='black', label='AMS')
        ax.legend(ncol=1, fontsize=10, loc='upper center',bbox_to_anchor=(0.5,0.99), shadow=True)
        
        ax.set_xticklabels(mnths)
        ax.set_ylabel(unit(spc))
        
        plt.savefig(figname, dpi=300, bbox_inches='tight')
        
        # Zapis SA a statistik do excelu:
        sa_daily.to_excel(writer, sheet_name=f'daily_{spc}_{ii}')
        sa_ann = sa_daily.mean()
        # Stats:
        sa_ann['r'] = sa_daily['AMS'].corr(sa_daily['Model'])
        sa_ann['rmse'] = rmse(sa_daily['Model'],sa_daily['AMS'])
        sa_ann['bias'] = bias(sa_daily['Model'],sa_daily['AMS'])
        sa_ann.to_excel(writer, sheet_name=f'annual_{spc}')

#############################################################################
for dom in doms: 
    
    if len(stdict[dom]) == 0:
        print (f"No AMS stations in domain: {dom}. No model time series available.\n ")
    else:
        # Zapis dennych a rocnych SA do excelu
        writer = pd.ExcelWriter(f'/data/oko/krajc/SA/SA_{dom}.xlsx')
        for spc in spcs:
            print (f"Working on domain: {dom}, spc: {spc} ....\n\n")
            process_domain(dom, spc)
        
        writer.save()
    
    
    
    