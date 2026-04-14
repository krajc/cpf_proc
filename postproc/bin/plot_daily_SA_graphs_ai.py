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
    'heat':['bd','rd','os','no'],
    'neis':['annual','seasonal','fugitive'],
    'road':[]
    }
year = 2024
# Vzhladom na moznost chybajuceho stlpca date vo vystupoch Atmostreet vytvrorim daterange
indx = pd.date_range(f"{year}-01-01 00:00:00",f"{year}-12-31 23:00:00", freq='1H' )

spcs = ['PM10','PM25','NO2','BaP']

#spcs = ['BaP']
# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','jelsava','zarnovicanb','martin','prievidza', 'bratislava']
nofugitive = ['martin','povazie','pohronie','hnusta','spis','trencin']

doms = ['bratislava', 'kosice']

def sum_cpf_group(dom, group, spc, nrec):
    al = {}
    rctab = {}
    idx = pd.date_range(start=f'{year}-01-01 01:00:00', end=f'{year}-12-31 22:00:00',freq='1H')
    if spc == 'NO2':
        cpfspc = 'nox'
    else:
        cpfspc = spc.lower()
    datadir = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}/{group}/timeseries"
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
        rcdf = rctab['rd'] + rctab['bd']  + rctab['no']  + rctab['os']
    else:
        if dom in nofugitive:
            rcdf = rctab['annual'] + rctab['seasonal']
        else:
            rcdf =  rctab['annual'] + rctab['seasonal'] + rctab['fugitive']
    
    return(rcdf.resample('D').mean())
         
def process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily):
    
    datafile = {}
    
    if spc in ('PM10', 'PM25'):
        atmodir = "/data/users/p2993/data_cpf/timeseries_road"
        datafile['road'] = f"{atmodir}/{spc}-total-{dom}-{year}.csv"
        road_df = pd.read_csv(f"{datafile['road']}")
        road_df.index = indx
        road_daily = road_df[eoi]
    else:
            
        atmodir = "/data/users/p6065/ATMOSTREET/Results/Bratislava_2024/Traffic"
        datafile['road'] = f"{atmodir}/{spc.upper()}_HourlyTimeseries_ATMO-Street_Indicators.csv"
        road_df = pd.read_csv(f"{datafile['road']}")
        road_df.index = indx
        road_daily = road_df[eoi].resample('D').mean()
    
    if spc == 'BaP':
        road_daily = road_daily/1000    
        
    datafile['backg'] = f"/data/users/p2993/data_cpf/rio/{year}/{dom}/minpoint_tseries{suff}.csv"
    
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
    heat_daily = sum_cpf_group(dom, 'heat', spc, len(rec))
    neis_daily = sum_cpf_group(dom, 'neis', spc, len(rec))
    heat_daily.columns = eoicodes
    neis_daily.columns = eoicodes
    
    
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
            figname = f"{pics}/sa_daily-{ii}-{spc}.png"
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
        figname = f'{pics}/sa_monthly_{ii}-{spc}.png'
        title = f"Príspevky jednotlivých skupín zdrojov k priemerným mesačným koncentráciám {spc}\
            \n{eoi[ii]}\n"
        ax = sa_monthly.plot(figsize = (10, 5), kind='bar', stacked=True, color=colorsM,\
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
def process_ams(dom, spc, rec):
    amsfile = f"/data/oko/krajc/dbase_calpuff/ams.data/{dom}-{spc.upper()}-{year}.csv"
    ams = pd.read_csv(amsfile)
    ams["date"] = pd.to_datetime(ams['Unnamed: 0'])
    ams = ams.set_index("date")
    ams = ams.drop(['Unnamed: 0'], axis=1)
    ams = ams.resample('D').mean()
    # Vytriedim receptory z CALPUFFu podla dostupnych  AMS MERANI:
    eoi = {}
    for i in range(nrec):
        if rec[i]['EolStationCode'] in ams.columns:
            eoi[rec[i]['EolStationCode']] = f"{rec[i]['City']}, {rec[i]['Street']}" 
   
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
        rec = yaml.full_load(file)
    nrec = len(rec)
       
    if nrec == 0:
        print (f"No AMS stations in domain: {dom}. No model time series available.\n ")
    else:
        # Zapis dennych a rocnych SA do excelu
        writer = pd.ExcelWriter(f'/data/oko/krajc/SA/SA_{year}-{dom}.xlsx')
        for spc in spcs:
            print (f"Working on domain: {dom}, spc: {spc} ....\n\n")
            # Nacitam tabulku AMS hodnot:
            eoi, ams_daily, amsr_daily = process_ams (dom, spc, rec)
            
            
            process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily)
        
        writer.save()
    
    
    
    