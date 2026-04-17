#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025-05-15:
    Prechod z REM2 na REM3. 
    Vstupne data za celu SR, namiesto po krajoch ako pri REM2
2026-01-20: 
    Prechod z metid vo forme dictionary na nacitavanie zo suboru
@author: p2993
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import time
import os
import calendar
import sys


#sample_inp_volemar = "/users/ext33340/templates/volemarb.dat"

crsLCC = {
  'proj': 'lcc',
 'lat_1': 48.75,
 'lat_2': 49,
 'lat_0': 47.7,
 'lon_0': 19.5,
 'x_0': 200000,
 'y_0': 0,
 'ellps': 'WGS84',
 'units': 'm',
 'no_defs': True
 }

spcs = ['PM10', 'PM25', 'NOx', 'SO2', 'BaP']
SPCS = list(map(lambda x: x.upper(), spcs))
# Priemerne vysky budov (pre rd a bd urcene z analyza_vysok_budov.py, pre
# no: arbitrarne nizsia hodnota ako rd, pre os: priemer rd a bd)
h = {'rd': 7.3 , 'bd': 14.4 , 'no': 5, 'os': 10.8}

sourcedir = '/data/oko/krajc/dbase_calpuff/source_arb'
voltempl = f'{sourcedir}/bin/templates/volemarb.templ'

with open(voltempl, 'r') as f_obj:
    tmp = f_obj.readlines()

# Vyrez geodataframe podla hranic domeny
def cutout_domain(domena):
    domshp = gpd.read_file(f"/data/oko/krajc/cpf_domeny/{domena}_LCCcpf")
    emi.to_crs(crsLCC, inplace=True)
    domshp.to_crs(crsLCC, inplace=True)
    subset = gpd.sjoin(emi, domshp, how='inner', predicate='within')
    subset.drop(columns=['index_right', 'cat'], inplace=True)
    icol = list(range(subset.shape[0]))
    subset.index = icol
    return (subset)

def prepare_scaling_table(t):
    
    #vypocet koeficientov 
    t['diff'] = np.where(t[id_st] > 13, 0, 13-t[id_st])
    #t['diff'] = list(map(lambda x: np.where(x > 13, 0, 13-x),t[id_st] ))
    #priemerna rocna odchylka od 13C
    t_mean = t['diff'].mean()
    t['koef'] = (t['diff'] / (t_mean * t.shape[0])).round(5)
    #t['koef'] = list(map(lambda x: (x / (t_mean * t.shape[0])).round(5), t['diff']))
    return(t)


year = 2024
year0 = 2024          # Meteorologicky rok pre model REM3
dom = 'bb1'

if calendar.isleap(year):
    ndays = 366
else:
    ndays = 365
    
print(f"Running VOLEMARB files creation for domain: {dom} ...\n")

#rozlisenie gridu zdrojov
res=50
#id stanice, z ktorej chcem pouzit data:
metid = pd.read_excel("/data/oko/krajc/dbase_calpuff/met.data/meteo4domains_2021_2024.xlsx", sheet_name=f"meteo_{year}")
metid.index = metid['domname']
if dom not in metid.index:
    metid = pd.read_excel("/data/oko/krajc/dbase_calpuff/met.data/meteo4domains_2021_2024.xlsx", sheet_name='meteo_2021')
    metid.index = metid['domname']
    if dom not in metid.index:
        print (f"Domena {dom} nema pridelenu meteostanicu!\n")
        sys.exit(0)

id_st = metid['metid'][dom]
    
#subor s dennymi profilmi teplot zo vsetkych stanic
#tfile = "/data/oko/krajc_hpc3/stations_daily_temp.dat"
tfile = f"/data/oko/krajc/dbase_calpuff/met.data/stations_daily_temp_{year}.dat"
tdata = pd.read_csv(tfile,sep='|')
# volemarb vyzaduje julian day
tdata.index = list(range(1,ndays+1))
del tdata['Unnamed: 0']
# data mozu obsahovat chybajuce dni, treba to osetrit:
t = tdata[[str(id_st)]].copy()
t.columns = [id_st]
t[id_st]=t[id_st].interpolate(method='nearest')
nancount = t[id_st].isnull().sum()
if nancount > 0:
    print (f'Check missing days: {nancount} in total \n')
    

    
infofile = f"/work/users/oko001/cpf_proc/volemarb/heat_sources_{dom}_{year}.info"
number = {}

for houses in ['rd','bd','no','os']:
    print(f"Working on: {houses} ...\n")
# Shapefile s emisiami gridovych sstvorcov
    
    emifile = f"/data/oko/krajc/dbase_calpuff/source_arb/rem3_{year0}_{houses}.gpkg"
    emi = gpd.read_file(emifile)
    
    emi.columns = ['id_grid','x', 'y', 'elev','SO2','NOx','PM10','PM25','BaP', 'geometry']
    # Vyrez domeny:
    e = cutout_domain(dom)
    etab = prepare_scaling_table(t)
    
    outdir = f'/work/users/oko001/cpf_proc/volemarb/{dom}/{houses}'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    else:
        for fil in os.listdir(outdir):
            os.remove(f'{outdir}/{fil}')
            
    for ss in range(e.shape[0]):
        print(f"Source: {ss}\n")
        outfile = f'{outdir}/volemarb-{houses}-{ss:05d}.dat'
    
        o = tmp.copy()
        o[2] = f"\'Residential heating - {houses}\'\n"  
        o[9] = f"{year}  01 00 0000  {year}  {ndays}  23  3600\n"
        o[11] = str(SPCS).replace(',','') 
        o[11] = o[11][1:-1] + '\n'
        # pocet zdrojov v subore
        nsrc = 1
        # pocet modelovanych znecistujucich latok
        nse = len(spcs)
        o[10] = f' {nsrc} {nse}\n'
        # meno zdroja (plus user defined flag)
        name = f"\'{houses.upper()}{ss}\'"
        o.append(f"{name} 1\n")
        
        # Emission rates in g/s pocas 24h pre zdroj ss: 
        
        for spc in spcs:
            etab[spc] = etab['koef'] * e[spc][ss] * 1000 / (24*3600)
            #etab[spc] = list(map(lambda x))
            
        # Loop cez dni  do volemarb.dat:
        for i in etab.index:
            
            # Casove obdobie (1 den)
            o.append(f" {year} {i} 00 0000 {year} {i} 23  3600\n")
            # meno xkm ykm efheight groundelev sigmay sigmaz erates(g/s)
            x, y = e.x[ss]/1000, e.y[ss]/1000
            sigy, sigz = res/2.15, h[houses]/2.15
            estr = ""
            for spc in spcs:
                estr = estr + str(round(etab[spc][i], 5)) + ' '
            o.append(f"{name} {x:.3f} {y:.3f} {h[houses]:.1f} {float(e.elev[ss]):.1f} {sigy:.1f} {sigz:.1f} {estr}\n")
    
        textout = ''.join(o)    
        with open(outfile,'w') as f_obj:
            f_obj.write(textout)

    # Zapis poctu fh a nfh zdrojov do suboru:
    number[houses] = e.shape[0]

with open(infofile, 'w') as f_obj:
    for houses in number.keys():
        f_obj.write(f"{houses}\t{number[houses]}\n")
       
    



