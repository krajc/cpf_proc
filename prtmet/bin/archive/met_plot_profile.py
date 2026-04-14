#!/users/p6065/anaconda3/envs/supergeo/bin/python


# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 15:16:23 2019

Skript vykresluje profil met. premennejv zadanom bode

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

crsLCC = plot_conc_v3.crsLCC

units = {'mht':'Mixing height (m)', 'stab':'Static stability','wspeed':'Wind speed (m/s)'}
names = {'mht':'Mixing height', 'stab':'Static stability', 'wspeed': 'Horizontal wind'}

# Nacitam meteostanice a urobim z tabulky geodataframe s projekciou LCCcpf:
station_list = '/users/p2993/dbase_calpuff/met.data/automaticke_stanice_2gen.txt'
sts = pd.read_csv(station_list, sep='\t')
gdf = gpd.GeoDataFrame(sts, geometry=gpd.points_from_xy(sts.lon, sts.lat))
gdf.crs = 4324
gdf.to_crs(crsLCC, inplace=True)

year = 202

dom = "poprad"
spcs = ['mht','stab', 'wspeed']

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
ymax = 1500 # max. vyska na zobrazovanie
xmax = 20   # rozsah x osi (rychlost vetra)

# Dataframe s profilmi na vykreslovanie
dfplt = pd.DataFrame(index = levels)
dfplt['z'] = dfplt.index
ncols= int(len(rng)/3)
colors = ['green','blue']
# Kreslenie profilov: 
fig,ax = plt.subplots(nrows=3, ncols=ncols, figsize=(ncols*3,20))
r = 0

for ii in range(3):
    for jj in range(ncols):
        
        ax[ii,jj].set_title('day: '+ str(rng[r])[8:10] + ' hour: ' + str(rng[r])[11:13])
        # Pridanie oboch stanic z modelu:
        for i in std.index:
            p = xd4.sel(times=rng[r]).interp(x=std.geometry[i].x, y=std.geometry[i].y, method='cubic')
            pdf = p.to_dataframe()
            dfplt[std['name'][i]] = pdf[['wspeed']]
            #p.to_netcdf(f'{pth}/prof-{std.ii[i]}-{std.name[i]}-hourly.nc')
            dfplt.plot(ax=ax[ii, jj], y='z', x=std['name'][i], label=std['name'][i], grid=True, 
                           xlim=(0,xmax), ylim=(0, ymax), legend=False, sharey=True, color=colors[i])
        # Pridanie sondaze:
        p = aer.sel(times=rng[r])
        pdf = p.to_dataframe()
        dfplt['SONDA'] = pdf[['wspeeda']]
        dfplt.plot(ax=ax[ii, jj], y='z', x='SONDA', label='SONDA', grid=True, color='red',
                       xlim=(0,xmax), ylim=(0, ymax), legend=False, sharey=True)
        #ax[ii,jj].quiver(dfplt[std['name'][i]], dfplt['z'], dfplt['u'], dfplt['v'], units='height', width=0.01)
        ax[ii,jj].set_xlabel('')
        r = r+1
handles, labels = ax[0,0].get_legend_handles_labels()
fig.legend(handles, labels, ncol=3, loc=(0.3,0.93),prop={'size': 14})
fig.suptitle(f"Wind speed profiles, days: {start[:11]} - {end[:11]}", fontsize=22)

            



