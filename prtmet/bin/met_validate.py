#!/users/p6065/anaconda3/envs/supergeo/bin/python


# -*- coding: utf-8 -*-
"""
Created Feb 2025

Skript pripravuje subory pre validaciu CALMET vetra v bodoch 
meterorologickych stanic v danej domene

@author: p2993
"""
import sys
sys.path.append('/users/p2993/python/libs')
import plot_conc_v3

import os
import subprocess

import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as colors

import pandas as pd
import geopandas as gpd

from metpy.calc import wind_components, wind_speed, wind_direction
from metpy.units import units

import sys
sys.path.append('/users/p6065/python-scripts')
from dbConnector import obs 


crsLCC = plot_conc_v3.crsLCC



#units = {'mht':'Mixing height (m)', 'stab':'Static stability','wspeed':'Wind speed (m/s)'}
names = {'mht':'Mixing height', 'stab':'Static stability', 'wspeed': 'Horizontal wind'}



year = 2024
dom = "ruzomberok"
'''
Switch aky druh bodov z domeny vyberame:
'met' - meteostanice
'arb' - arbitrary (teda vyber z mapy priamo suradnice)
'ams' - AMS
'''
points = 'met'
mypoints = {'P1':[19.143041,	48.747184], 'P2':[19.166871, 48.741983]}

pth = f"/data/oko/krajc/data_cpf/prtmet/{year}/{dom}"
# Nc files:
ncfs = [f"{pth}/terrad_1km_ikine_0/4D-{dom}-{year}.nc"]
setnames = ['set2']

start, end = f'{year}-01-01 00:00:00',  f'{year}-12-31 22:00:00'
dates = list(pd.date_range(start, end, freq='1H'))

def rectable(points):
    if points == 'met':
        # Nacitam meteostanice 
        station_list = '/users/p2993/dbase_calpuff/met.data/automaticke_stanice_2gen.txt'
        sts = pd.read_csv(station_list, sep='\t')
    elif points == 'ams':
        #Nacitam AMS stanice
        station_list = '/users/p2993/dbase_calpuff/ams.data/ams2024.xlsx'
        sts = pd.read_excel(station_list, sheet_name='calpuff')
    elif points == 'arb':
        sts = pd.DataFrame.from_dict(mypoints, orient='index')
        sts.columns = ['lon','lat']
        sts['id'] = sts.index
    # urobim z tabulky geodataframe s projekciou LCCcpf:
    gdf = gpd.GeoDataFrame(sts, geometry=gpd.points_from_xy(sts.lon, sts.lat))
    gdf.crs = 4326
    gdf.to_crs(crsLCC, inplace=True)
    return gdf
    
#### VYPOCET KOMPONENTOV RYCHLOSTI (ws a wd su lists)
def s2v(ws, wd):
    uu = []
    vv = []
    for speed, direction in zip(ws, wd):
        
        u, v = wind_components(speed * units('m/s') , direction * units.deg)
        if abs(u) < 0.1 * units('m/s'):
            u = 0.0 * units('m/s')
        if abs(v) < 0.1 * units('m/s'):
            v = 0.0 * units('m/s')
        uu.append(u.magnitude)
        vv.append(v.magnitude)
    return uu, vv

def v2s(u, v):
    u = list(u)
    v = list(v)
    direction = wind_direction (u * units('m/s'), v * units('m/s')).magnitude
    wspeed = wind_speed (u * units('m/s'), v * units('m/s')).magnitude
    return wspeed, direction

def select_synop(termin):
    sqr = obs.query(f"select si.si.ii, name, obs.obs_synop.ff, obs.obs_synop.dd from obs.obs_synop join si.si on obs.obs_synop.si=si.si.id \
            where date='{str(termin)[:-3]}' and si.si.ci=1 and si.si.cc='SK' and si.si.ii={ii}")
    if sqr.shape[0] > 0:
        ff = sqr['ff'][0]
        dd = sqr['dd'][0]
    else:
        ff = np.nan
        dd = np.nan  
    return ff, dd

def select_auto(termin):
    sqr = obs.query(f"select ws_avg, wd_avg, si.name from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
                    where date='{str(termin)[:-3]}'  and ii={ii} and MINUTE(date)=0")
    if sqr.shape[0] > 0:
        ff = sqr['ws_avg'][0]
        dd = sqr['wd_avg'][0]
    else:
        ff = np.nan
        dd = np.nan  
    return ff, dd    

# Geodataframe s bodmi:
gdf = rectable(points)
        
# Nacitam hranice domeny:
domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
domshape.crs = crsLCC
# Vyber podmnoziny stanic pre domenu:
std = gpd.overlay(gdf,domshape, how='intersection' )
# Zoznam bodov:
if points == 'met':
    stlpec = 'ii'
elif points == 'ams':
    stlpec = 'EolStationCode'
elif points == 'arb':
    stlpec = 'id'
ids = list(std[stlpec])

# Nacitam .nc data:


for i in range(len(ncfs)):
    xd4 = xr.open_dataset(ncfs[i])
    xd4['wspeed'] = np.sqrt(np.square(xd4['u'])+np.square(xd4['v']))
    levels = xd4.coords['z'].values
    # Vyberiem ibaprvu hladinu:
    xde = xd4.sel(times = dates, z = levels[0])
    
    #### model-obs tables for different stations ii
    tab = {}
    missing = {}
    missingA = {}
    
    for ii in ids:
        # Interpolate xde to station points
        clm = xde.interp(x=float(std[std[stlpec]==ii].geometry.x), 
                         y=float(std[std[stlpec]==ii].geometry.y), method='cubic').to_dataframe()
        clm.drop(columns=['z', 'spatial_ref','x', 'y'], inplace = True)
        clm['ff'] = None
        clm['dd'] = None
        
        if points == 'met':
            counter = 0
            countera = 0
            for date in dates:
                wsp, wdir = None, None
                wsp, wdir = select_auto(date)
                #print(f"{wsp}, {wdir}\n")
                if wsp == None:
                    print("Selecting from SYNOP ... \n")
                    wsp, wdir = select_synop(date)
                    countera = countera + 1
                    if np.isnan(wsp):
                        print("No data in SYNOP and AUTO!\n ")
                        counter = counter + 1
                        
                clm['ff'][date] = wsp
                clm['dd'][date] = wdir
            missing[ii] = counter 
            missingA[ii] = countera
        tab[ii] = clm.copy() 
    
    # Add column with wind dir from CALMET (wdirc) and save to csv
    for ii in ids: 
        tmp = v2s(tab[ii]['u'], tab[ii]['v'])
        tab[ii]['wdirc'] = tmp[1]
        tab[ii].to_csv(f"{pth}/validate-{setnames[i]}-{ii}.csv")
        




