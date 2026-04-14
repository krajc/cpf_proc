#!/users/p6065/anaconda3/envs/supergeo/bin/python


# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 15:16:23 2019

Skript vykresluje profil met. premennejv zadanom bode z aerolog merani a
z roznych simulacii

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

from metpy.calc import wind_components
from metpy.units import units

crsLCC = plot_conc_v3.crsLCC

#### VYPOCET KOMPONENTOV RYCHLOSTI (ws a wd su lists)
def vetry(ws, wd):
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

#units = {'mht':'Mixing height (m)', 'stab':'Static stability','wspeed':'Wind speed (m/s)'}
names = {'mht':'Mixing height', 'stab':'Static stability', 'wspeed': 'Horizontal wind'}

# Nacitam meteostanice a urobim z tabulky geodataframe s projekciou LCCcpf:
station_list = '/users/p2993/dbase_calpuff/met.data/automaticke_stanice_2gen.txt'
sts = pd.read_csv(station_list, sep='\t')
gdf = gpd.GeoDataFrame(sts, geometry=gpd.points_from_xy(sts.lon, sts.lat))
gdf.crs = 4324
gdf.to_crs(crsLCC, inplace=True)

year = 2021

dom = "poprad"

# Nacitam hranice domeny:
domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
domshape.crs = crsLCC
# Vyber podmnoziny stanic pre domenu:
std = gpd.overlay(gdf,domshape, how='intersection' )

# Nacitam .nc data:
pth = f"/data/users/x2022/prtmet/{dom}"
#xds = xr.open_dataset(f"{pth}/2D-{dom}-{year}.nc")
# Uz predspracovane data v jednom bode obsahujuce aj sondaz:
aer = xr.open_dataset('/users/p2993/barborka/model_vs_aero_poprad_cubic.nc')
xd4 = xr.open_dataset(f"{pth}/4D-{dom}-{year}.nc")
xd4['wspeed'] = np.sqrt(np.square(xd4['u'])+np.square(xd4['v']))
levels = xd4.coords['z'].values

#### Definicia casoveho rozsahu a kroku pre kreslenie:
start, end, step = f"{year}-12-12 00:00:00", f"{year}-12-20 23:00:00", '12H'
rng = list(pd.date_range(start, end, freq=step))
ymax = 1000 # max. vyska na zobrazovanie
xmax = 20  # rozsah x osi (rychlost vetra)

# Kreslenie profilov:
nrows = 3
ncols= int(len(rng)/nrows)
# Poloha sipok
xx = 15.
xpos = [xx,xx,xx,xx,xx,xx,xx,xx,xx,xx]
fig,ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*3,nrows*7))
r = 0

for ii in range(nrows):
    for jj in range(ncols):
        
        ax[ii,jj].set_title('day: '+ str(rng[r])[8:10] + ' hour: ' + str(rng[r])[11:13])
        
        p = aer.sel(times=rng[r])
        pdf = p.to_dataframe()
        pdf['z'] = pdf.index
        pdf.plot(ax=ax[ii, jj], y='z', x='wspeed', label=std['name'][1], grid=True, 
                       xlim=(0,xmax), ylim=(0, ymax), legend=False, sharey=True, color='blue')
        # Pridanie sondaze:
        pdf.plot(ax=ax[ii, jj], y='z', x='wspeeda', label='SONDA', grid=True, 
                       xlim=(0,xmax), ylim=(0, ymax), legend=False, sharey=True, color='red')
        # Pridanie sipok:
        ax[ii,jj].quiver(xpos, pdf['z'], pdf['u'], pdf['v'], color='blue')
        us, vs = vetry(list(pdf['wspeeda']), list(pdf['wdira']))
        ax[ii,jj].quiver(xpos, pdf['z'], us, vs, color='red')
        ax[ii,jj].set_xlabel('')
        r = r+1
handles, labels = ax[0,0].get_legend_handles_labels()
fig.legend(handles, labels, ncol=3, loc=(0.3,0.93),prop={'size': 14})
fig.suptitle(f"Wind speed profiles, days: {start[:11]} - {end[:11]}", fontsize=22)

            



