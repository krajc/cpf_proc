#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vykreslovanie grafov 
@author: p2993
2023-09-20:
    Zmena skriptu plot_daily_SA_graphs.py: namiesto modulu na spracovanie textovych timeseries dat
    je funkcia sample_grid, ktora interpoluje gridove data do bodov stanic
2023-09-26:
    Pridane nacitavanie RIO dat z manualne vybranych bodov 
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
    'heat':['bd','rd','os','no'],
    'neis':['annual','seasonal','fugitive'],
    'road':[]
    }

year = 2024
#pozadie = 'rio' # alternativa 'rio'
# Vzhladom na moznost chybajuceho stlpca date vo vystupoch Atmostreet vytvrorim daterange
indx = pd.date_range(f"{year}-01-01 00:00:00",f"{year}-12-31 23:00:00", freq='1H' )
indxd = pd.date_range(f"{year}-01-01 00:00:00",f"{year}-12-31 23:00:00", freq='1D' )
spcs = ['PM10','PM25','NO2','BaP']
spcs = ['PM10','PM25', 'NO2']
#doms = ['ruzomberok','zilina']
#doms = ['hnusta','jelsava','juznyhont', 'zarnovicanb','zvolen','krompachy']
#doms = ['kysuce']  POZOR! nEMAME  odlozene timeseries  pre kysuce
nofugitive = ['martin','povazie','pohronie','hnusta','spis','trencin']
# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','zarnovicanb','martin','prievidza', 'bratislava',
            'kosice', 'krompachy','nitra','juznyhont']
doms = ['martin']
doms = ['kosice']
doms = ['banskabystrica','zarnovicanb','martin','prievidza']
doms = ['bratislava']

def sample_grid(dom, group, spc, rec, eolcodes):
    ncfile = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}/{dom}-{year}-{group}.nc"
    grd = xr.open_dataset(ncfile)
    s = pd.DataFrame(columns=eolcodes, index=pd.date_range(start=f'{year}-01-01 01:00:00', end=f'{year}-12-31 22:00:00',freq='1H'))
    for i in rec.index:
         xy = grd[spc].interp(x=rec['x'][i]*1000, y=rec['y'][i]*1000, method='linear').to_dataframe()
         s[rec['EolStationCode'][i]] = xy[spc]
    return(s.resample('D').mean())
         
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
    '''
    datafile = {}
       
    if spc in ('PM10', 'PM25'):
        atmodir = "/data/users/p2993/data_cpf/timeseries_road"
        datafile['road'] = f"{atmodir}/{spc}-total-{dom}-{year}.csv"
        road_df = pd.read_csv(f"{datafile['road']}")
        road_df.index = indxd
        road_daily = road_df[eoi]
        
    else:
            
        atmodir = "/data/users/p6065/ATMOSTREET/Results/2024/Bratislava_2024/Traffic"
        datafile['road'] = f"{atmodir}/{spc.upper()}_HourlyTimeseries_ATMO-Street_Indicators.csv"
        road_df = pd.read_csv(f"{datafile['road']}")
        road_df.index = indx
        road_daily = road_df[eoi].resample('D').mean()
    
    if spc == 'BaP':
        road_daily = road_daily/1000    
    
    datafile['rio'] = f"/data/users/p2993/data_cpf/rio/{year}/{dom}/minpoint_tseries{suff}.csv"
    datafile['cmaq'] = f"/data/users/p2993/data_cpf/cmaq/{year}/{dom}/cmaq-daily-backg-{dom}-{year}.csv"
    
    pics = f"/data/users/p2993/data_cpf/pics/{year}/{dom}/graphs"
    if not os.path.exists(pics):
         os.makedirs(pics)
          
    # Procesing tseries:
    # AMS:
    ams_monthly = ams_daily.resample('M').mean()
    # backg:
    brio = pd.read_csv(f"{datafile['rio']}", index_col='times')
    brio.index = pd.to_datetime(brio.index) 
    bcmaq = pd.read_csv(f"{datafile['cmaq']}", index_col='times')
    bcmaq.index = pd.to_datetime(bcmaq.index) 
    # heat, neis (v CALPUFFe moze byt viac DR ako AMS pre konkretne spc):
    eolcodes = list(rec['EolStationCode'])
    if spc == 'NO2':
        spccpf = 'NOx'
    else:
        spccpf = spc
    heat_daily = sample_grid(dom, 'heat', spccpf, rec, eolcodes)
    neis_daily = sample_grid(dom, 'neis', spccpf, rec, eolcodes)
    
    # road:
    '''
    #if spc=='BaP' and atmodir == "/data/users/p6065/atmostreet/Results/SR_2021_traffic/pureSectors" :
    if spc=='BaP':
        datename = 'Unnamed: 0'
    else:
        datename = 'date'
    '''
    
    # tabulka SA:
    
    if spc == 'BaP':
        # ams pozadovky:
        backg_daily = amsr_daily[['SK0006R']].astype(np.float64)
    else:
        brio_daily = brio[[spc]].astype(np.float64)
        bcmaq_daily = bcmaq[[spc]].astype(np.float64)
        
    for ii in eoi.keys():
        sa_daily = pd.concat([brio_daily, bcmaq_daily,heat_daily[[ii]],road_daily[[ii]],neis_daily[[ii]]] , axis=1)
        sa_daily = sa_daily[sa_daily.index.year == year]
        #sa_daily = sa_daily.drop(['2022-01-01'],axis=0)
        sa_daily.columns =  ['RIO', 'CMAQ','heating','traffic','NEIS'] 
        sa_monthly = sa_daily.resample('M').mean()
        
        
        sa_daily['total_RIO'] = sa_daily['RIO'] + sa_daily['heating']+sa_daily['traffic']+sa_daily['NEIS']
        sa_daily['total_CMAQ'] = sa_daily['CMAQ'] + sa_daily['heating']+sa_daily['traffic']+sa_daily['NEIS']
        sa_daily['AMS'] = ams_daily[ii].astype(float) 
        sa_daily_plt = sa_daily.drop(columns=['heating','traffic','NEIS']).copy()
        
        
                
        plt.rcParams.update({'font.size': 10})
        plt.rcParams.update({'xtick.labelsize': 10})
        plt.rcParams.update({'ytick.labelsize': 10})  
        colorsD = ['blue','orange','green','red','black']
        colorsM = ['blue','orange','green','red']  
        
        # Kreslenie:
        
        # Denne grafy  
        if spc != 'BaP':
            figname = f"{pics}/interp_sa_daily-{ii}-{spc}-comp.png"
            title = f"Príspevky jednotlivých skupín zdrojov k priemerným denným koncentráciám {spc}\
                \n{eoi[ii]}\n"
        
            ax = sa_daily_plt.plot(figsize=(15,5), title=title, rot=45, legend=False, color=colorsD)
            ax.legend(ncol=2, fontsize=12,loc='upper center',bbox_to_anchor=(0.5,0.98),shadow=True)
            ax.set_ylabel(unit(spc))
            ax.set_xlabel('')
            plt.savefig(figname, dpi=300, bbox_inches='tight')
            plt.show()
        
        # Mesacne grafy
        mnths = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        sa_monthly.index = mnths
        rplot = sa_monthly[['RIO', 'heating','traffic','NEIS']]
        cplot = sa_monthly[['CMAQ','heating','traffic','NEIS']]          
        
        figname = f'{pics}/interp_sa_monthly_{ii}-{spc}-comp.png'
        title = f"Príspevky jednotlivých skupín zdrojov k priemerným mesačným koncentráciám {spc}\
            \n{eoi[ii]}\n\n"
        ax = rplot.plot(figsize = (10, 5), kind='bar', stacked=True, color=colorsM,\
                            title=title, rot=45, legend=False)
        # 2. Record how many bar segments exist before adding the second set
        n_patches_first = len(ax.patches)

        # 3. Plot the second dataframe (Ghost/Hatched) on the same 'ax'
        cplot.plot(kind='bar',stacked=True, ax=ax, color=colorsM, alpha=0.4, \
                         hatch='//', edgecolor='white', legend=False,  rot=45)

        # 4. Shift the second set of bars horizontally
        shift = 0.15  # Adjust this value for more or less overlap
        for i in range(n_patches_first, len(ax.patches)):
            patch = ax.patches[i]
            patch.set_x(patch.get_x() + shift)
        
        ax.plot(mnths, ams_monthly[ii],linestyle='None', marker='o', color='yellow', \
                  markeredgecolor='black', label='AMS')
        ax.legend(ncol=5, fontsize=9, loc='lower center',bbox_to_anchor=(0.5,0.99))
        
        ax.set_xticklabels(mnths)
        ax.set_ylabel(unit(spc))
        
        plt.savefig(figname, dpi=300, bbox_inches='tight')
        plt.show()
        

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
    '''
    # v CALPUFF receptoroch pre bratislavu vystupuje Rovinka Slovnaft a Rovinka Rovinka
    # pod rovnakym EolStationCode. Jednu (Slovnaft) treba odstranit
    if dom == 'bratislava':
        rec = rec.drop(labels=6, axis=0)
        nrec = nrec-1 
        rec.index = list(range(nrec))
    '''
    if nrec == 0 and dom != 'juznyhont':
        print (f"No AMS stations in domain: {dom}. No model time series available.\n ")
    else:
        # Zapis dennych a rocnych SA do excelu
        
        for spc in spcs:
            print (f"Working on domain: {dom}, spc: {spc} ....\n\n")
            # Nacitam tabulku AMS hodnot:
            eoi, ams_daily, amsr_daily = process_ams (dom, spc, rec)
            
            
            process_domain(dom, spc, rec, eoi, ams_daily, amsr_daily)
        
       
    
    
    
    