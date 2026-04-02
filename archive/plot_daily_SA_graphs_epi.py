#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vykreslovanie grafov 
@author: p2993
Dost upravena verzia povodneho skriptu pre epizody CAMS NCP projektu. 
Vykresluje iba denne grafy. 

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

year = 2023
spcs = ['PM10']
#spcs = ['BaP']
# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','jelsava','zarnovicanb','martin','prievidza', 'bratislava']
doms = ['bratislava'] 
#doms = ['trencin','prievidza']
#doms = ['kosice']
#doms = ['ruzomberok','zilina']
#doms = ['hnusta','jelsava','juznyhont', 'zarnovicanb','zvolen','krompachy']
#doms = ['kysuce']  POZOR! nEMAME  odlozene timeseries  pre kysuce
nofugitive = ['martin','povazie','pohronie','hnusta','spis','trencin']
epi1 = ['2023-02-06', '2023-02-07', '2023-02-08', '2023-02-09', '2023-02-10',
       '2023-02-11', '2023-02-12', '2023-02-13', '2023-02-14', '2023-02-15',
       '2023-02-16', '2023-02-17', '2023-02-18', '2023-02-19', '2023-02-20',
       '2023-02-21', '2023-02-22', '2023-02-23', '2023-02-24', '2023-02-25']
epi2 = ['2023-09-06', '2023-09-07', '2023-09-08', '2023-09-09', '2023-09-10',
       '2023-09-11', '2023-09-12', '2023-09-13', '2023-09-14']
epi = epi1
epiname = 'epi1'
# Kvoli adresaru NEIS dat a road dat potrebujeme este taketo oznacenie:
epi_neis = {'epi1':'feb', 'epi2':'sept'}

epitrafname = {'epi1':'BA_2023_CAMS_FEB', 'epi2':'BA_2023_CAMS_SEP'}

if epiname == 'epi2':
    groups = ['road','neis']
    title1 = 'Episode 2: September 6-14, 2023'
else:
    groups = ['road','heat', 'neis']
    title1 = 'Episode 1: February 6-25, 2023'

def sum_cpf_group(dom, group, spc, nrec, epi):
    al = {}
    rctab = {}
    idx = pd.date_range(start=f'{epi[0]} 01:00:00', end=f'{epi[-1]} 22:00:00',freq='1H')
    if spc == 'NO2':
        cpfspc = 'nox'
    else:
        cpfspc = spc.lower()
    if group == 'heat':
        datadir = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}/{group}/timeseries"
    else:
        datadir = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}/{group}/timeseries/{epi_neis[epiname]}"
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
         
def process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily):
    
    # Cesta k vstupom:
    #atmodir = "/data/users/p6065/atmostreet/Results/DOM_2021_zilinsky_kraj/SectorContribution"
    '''
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
    '''
    atmodir = f"/data/users/p6065/ATMOSTREET/Results/{epitrafname[epiname]}/Traffic"
    datafile = {}
    datafile['road'] = f"{atmodir}/{spc.upper()}_HourlyTimeseries_IFDM_Indicators.csv"
    datafile['backg'] = f"/data/users/p2993/data_cpf/rio/{year}/{dom}/minpoint_{epiname}_tseries{suff}.csv"
    
    pics = f"/data/users/p2993/data_cpf/pics/{year}/{dom}/graphs"
    if not os.path.exists(pics):
         os.makedirs(pics)
    
            
    # Procesing tseries:
    # AMS:
    
    ams_monthly = ams_daily.resample('M').mean()
    # backg:
    backg = pd.read_csv(f"{datafile['backg']}", index_col='times')
    backg.index = pd.to_datetime(backg.index) 
    
    # heat, neis (v CALPUFFe moze byt viac DR ako AMS pre konkretne spc):
    eoicodes = list(map(lambda x: x['EolStationCode'], rec))
    heat_daily = sum_cpf_group(dom, 'heat', spc, len(rec),epi)
    neis_daily = sum_cpf_group(dom, 'neis', spc, len(rec),epi)
    heat_daily.columns = eoicodes
    neis_daily.columns = eoicodes
    # road:
    datename = 'Unnamed: 0'
    
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
        if epiname == 'epi1':
            sa_daily = pd.concat([backg_daily, heat_daily[[ii]], road_daily[[ii]], neis_daily[[ii]]], axis=1)
            sa_daily = sa_daily[sa_daily.index.year == year]
            sa_daily = sa_daily.iloc[:-2,:]
                
            sa_monthly = sa_daily.resample('M').mean()
            sa_monthly.columns = ['Regional', 'Residential','Road transport', 'Industry']  
            
            sa_daily['model'] = sa_daily.sum(axis=1)
            sa_daily['ams'] = ams_daily[ii].astype(float) 
        
            sa_daily.columns = ['Regional', 'Residential','Road transport', 'Industry',  \
                                    'Model','AMS' ]
        else:
            sa_daily = pd.concat([backg_daily, road_daily[[ii]], neis_daily[[ii]]], axis=1)
            sa_daily = sa_daily[sa_daily.index.year == year]
            sa_daily = sa_daily.iloc[:-1,:]
                
            sa_monthly = sa_daily.resample('M').mean()
            sa_monthly.columns = ['Regional', 'Road transport', 'Industry']  
            
            sa_daily['model'] = sa_daily.sum(axis=1)
            sa_daily['ams'] = ams_daily[ii].astype(float)
            sa_daily.columns = ['Regional', 'Road transport', 'Industry', 'Model','AMS']
        
        plt.rcParams.update({'font.size': 10})
        plt.rcParams.update({'xtick.labelsize': 10})
        plt.rcParams.update({'ytick.labelsize': 10})  
        
        if epiname == 'epi1':
            ngroups = ['Regional', 'Residential','Road transport', 'Industry']
            colorsD = ['turquoise','purple','red','orange']
        else:
            ngroups = ['Regional', 'Road transport', 'Industry']
            colorsD = ['turquoise','red','orange']
        # Kreslenie:
        
        # Denne grafy  
        
        figname = f"{pics}/sa_daily-{epiname}-{ii}-{spc}.png"
        title = f"{title1} - {eoi[ii]}\n"
    
        plt.rcParams.update({'font.size': 14})
        plt.rcParams.update({'xtick.labelsize': 14})
        plt.rcParams.update({'ytick.labelsize': 14})    
        
        ax = sa_daily[ngroups].plot.area( color=colorsD,ylim = (0,55))
        sa_daily[['AMS']].plot(ax=ax, figsize=(15,5), title=title, rot=0, legend=False,color='black')
        
        
        ax.legend(ncol=5, fontsize=10,loc='upper center',bbox_to_anchor=(0.5,-0.1),shadow=True)
        ax.set_ylabel(unit(spc))
        ax.set_xlabel('')
        ax.grid(color='grey',which='both',  axis='y', alpha=0.5)
        plt.savefig(figname, dpi=300, bbox_inches='tight')
        plt.show()
        '''
        # Mesacne grafy
        mnths = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        sa_monthly.index = mnths
        figname = f'{pics}/sa_monthly_{ii}-{spc}.png'
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
        '''
        # Zapis SA a statistik do excelu:
        sa_daily.to_excel(writer, sheet_name=f'daily_{spc}_{ii}_{epiname}')
        sa_ann = sa_daily.mean()
        # Stats:
        sa_ann['r'] = sa_daily['AMS'].corr(sa_daily['Model'])
        sa_ann['rmse'] = rmse(sa_daily['Model'],sa_daily['AMS'])
        sa_ann['bias'] = bias(sa_daily['Model'],sa_daily['AMS'])
        sa_ann.to_excel(writer, sheet_name=f'annual_{spc}_{ii}')

#############################################################################
# Spracovanie AMS dat:
def process_ams(spc, rec):
    amsfile = f"/data/oko/krajc/dbase_calpuff/ams.data/{dom}-{spc}-{epiname}.csv"
    ams = pd.read_csv(amsfile)
    ams.set_index('Unnamed: 0', inplace=True)
    lst = list(ams.columns)
    
    # Vytriedim receptory z CALPUFFu podla dostupnych  AMS MERANI:
    eoi = {}
    for i in range(nrec):
        if rec[i]['EolStationCode'] in ams.columns:
            eoi[rec[i]['EolStationCode']] = f"{rec[i]['City']}, {rec[i]['Street']}" 
   
    ams_daily = pd.DataFrame(index=ams.index)
    for i in eoi.keys():
        ams_daily[i] = ams[i].astype(np.float64)
      
    ams_daily.index = pd.to_datetime(ams_daily.index)
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
        rec = yaml.full_load(file)
    nrec = len(rec)
       
    if nrec == 0:
        print (f"No AMS stations in domain: {dom}. No model time series available.\n ")
    else:
        # Zapis dennych a rocnych SA do excelu
        writer = pd.ExcelWriter(f'/data/oko/krajc/SA/SA_{dom}_{epiname}.xlsx')
        for spc in spcs:
            print (f"Working on domain: {dom}, spc: {spc} ....\n\n")
            # Nacitam tabulku AMS hodnot:
            eoi, ams_daily, amsr_daily = process_ams (spc, rec)
            ams_daily = ams_daily.resample('D').mean()
            
            process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily)
        
        writer.save()
    
    
    
    