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
            where date='{termin[:-3]}' and si.si.ci=1 and si.si.cc='SK' and si.si.ii={ii}")
    if sqr.shape[0] > 0:
        ff = sqr['ff'][0]
        dd = sqr['dd'][0]
    else:
        ff = np.nan
        dd = np.nan  
    return ff, dd

def select_auto(termin):
    sqr = obs.query(f"select ws_avg, wd_avg, si.name from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
                    where date='{termin[:-3]}'  and ii={ii} and MINUTE(date)=0")
    if sqr.shape[0] > 0:
        ff = sqr['ws_avg'][0]
        dd = sqr['wd_avg'][0]
    else:
        ff = np.nan
        dd = np.nan  
    return ff, dd

#units = {'mht':'Mixing height (m)', 'stab':'Static stability','wspeed':'Wind speed (m/s)'}
names = {'mht':'Mixing height', 'stab':'Static stability', 'wspeed': 'Horizontal wind'}

# Nacitam meteostanice a urobim z tabulky geodataframe s projekciou LCCcpf:
station_list = '/users/p2993/dbase_calpuff/met.data/automaticke_stanice_2gen.txt'
sts = pd.read_csv(station_list, sep='\t')
gdf = gpd.GeoDataFrame(sts, geometry=gpd.points_from_xy(sts.lon, sts.lat))
gdf.crs = 4324
gdf.to_crs(crsLCC, inplace=True)

year = 2023
dom = "bratislava"
epifile = f"/users/p2993/cpf_proc/calmet/rerun{year}_{dom}.inp"
if os.path.exists(epifile):
    with open(epifile) as f_obj:
        dates = f_obj.readlines()
dates = list(map(lambda x: x[:-1], dates))
datehrs = []
for date in dates:
    for hr in range(24):
        datehrs.append(f'{date} {hr:02d}:00:00')

# Nacitam hranice domeny:
domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
domshape.crs = crsLCC
# Vyber podmnoziny stanic pre domenu:
std = gpd.overlay(gdf,domshape, how='intersection' )
iis = list(std.ii)

# Nacitam .nc data:
pth = f"/data/oko/krajc/data_cpf/prtmet/{dom}"

xd4 = xr.open_dataset(f"{pth}/4D-{dom}-{year}.nc")
xd4['wspeed'] = np.sqrt(np.square(xd4['u'])+np.square(xd4['v']))
levels = xd4.coords['z'].values
# Vyberiem iba epizody a prvu hladinu:
xde = xd4.sel(times = datehrs, z = levels[0])

#### model-obs tables for different stations ii
tab = {}
missing = {}
missingA = {}

for ii in iis:
    # Interpolate xde to station points
    clm = xde.interp(x=float(std[std.ii==ii].geometry.x), 
                     y=float(std[std.ii==ii].geometry.y), method='cubic').to_dataframe()
    clm.drop(columns=['z', 'spatial_ref','x', 'y'], inplace = True)
    clm['ff'] = 0
    clm['dd'] = 0
    counter = 0
    countera = 0
    for datehr in datehrs:
        wsp, wdir = None, None
        wsp, wdir = select_auto(datehr)
        #print(f"{wsp}, {wdir}\n")
        if wsp == None:
            print("Selecting from SYNOP ... \n")
            wsp, wdir = select_synop(datehr)
            countera = countera + 1
            if np.isnan(wsp):
                print("No data in SYNOP and AUTO!\n ")
                counter = counter + 1
                
        clm['ff'][datehr] = wsp
        clm['dd'][datehr] = wdir
    missing[ii] = counter 
    missingA[ii] = countera
    tab[ii] = clm.copy() 

# Add column with wind dir from CALMET (wdirc) and save to csv
for ii in iis: 
    tmp = v2s(tab[ii]['u'], tab[ii]['v'])
    tab[ii]['wdirc'] = tmp[1]
    tab[ii].to_csv(f"/data/oko/krajc/data_cpf/prtmet/{dom}/validate-{ii}.csv")
        
            



