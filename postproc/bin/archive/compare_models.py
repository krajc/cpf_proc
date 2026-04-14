#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 12:06:39 2022

Porovnava  sektorove koncentracie CALPUFF vs ATMOSTREET
"""

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.io.img_tiles as cimgt
import xarray as xr
import pandas as pd
import geopandas as gpd
import sys
import os

doms = ('martin','ruzomberok','zilina','kysuce','orava')

sys.path.append('/data/oko/krajc/python/libs')
import plot_conc_v5

# Nacitanie vseobecnych dat z externej kniznice

# Nacitanie vseobecnych dat z externeho skriptu:
crsLCC = plot_conc_v5.crsLCC
unit = plot_conc_v5.unit_string
interpol = plot_conc_v5.interpolacia
opis = plot_conc_v5.opis
# Dictionary s civilnymi nazvami domen:
domname = plot_conc_v5.domname

ggroups = {
    'heat':['fh', 'nfh'],
    'neis':['annual','seasonal', 'fugitive'],
    'road':[]
}

cpfa = {
      'neis': 'Industry',
      'heat': 'Residential',
      'road': 'Traffic'
}

# Import projekcie do cartopy:
lcc = ccrs.LambertConformal(central_longitude=crsLCC['lon_0'], central_latitude=crsLCC['lat_0'],
                            standard_parallels=(crsLCC['lat_1'], crsLCC['lat_2']), 
                            false_easting=crsLCC['x_0'])

def plotting (proj, C, spc, figtitle, amstab, outfile, aspect,lev):
       
    plt.rcParams.update({'font.size': 16})
    plt.rcParams.update({'xtick.labelsize': 16})
    plt.rcParams.update({'ytick.labelsize': 16})
    plt.rcParams['figure.figsize'] = 15, 15*aspect
    
    mapsource = cimgt.Stamen(style='terrain')
    # Vymenim extent lalo za extent v lcc (predtym mi toto neslo, preto bol lalo):
    # extent = get_lalo_extent_from_xarray(C)
    extent = [C.x.values.min(), C.x.values.max(), C.y.values.min(), C.y.values.max()]
    
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.add_image(mapsource, 13, interpolation='bilinear')
 
    a = C.plot.pcolormesh( alpha = 0.4, linewidth=0, 
                          antialiased=True, add_colorbar=False)
    cb = plt.colorbar(a,label=unit(spc),  orientation="vertical",
                      shrink=0.62)
    
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
    
    amstab.plot(ax=ax,transform=ccrs.PlateCarree(), marker='o', edgecolor='black',
            facecolor='red', markersize=12 )

    for x, y, label in zip(amstab.lon, amstab.lat, amstab.location):
        ax.text(x, y, f' AMS {label}', fontsize=11,  transform=ccrs.PlateCarree())

    plt.savefig(outfile, dpi=300, bbox_inches='tight')    
    plt.show()

# Staticke data:

stations = pd.read_csv('/data/oko/krajc/GIS/ams/stanice_2022.csv') 
stations = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.lon, stations.lat))

# Domena a data specificke pre domenu:
    
dom = 'martin'
year = 2021
group = 'heat'

specs = ['PM10','PM25','NO2']

for dom in doms:
    show_st = stations[stations['city']==dom.upper()]
                
    # Cesta k vstupom:
    datadir = {}
    datadir['atmostr'] = f"/data/oko/AtmostreetPostproc/{year}/Sectors"
    if dom == 'kysuce' and  group=='heat':
        datadir['calpuff'] = f'/data/users/p2828/calpost/{dom}'
    else:
        datadir['calpuff'] = f"/data/users/p2993/data_cpf/netcdf/{dom}"
    
    # Cesta k vystupom:
    pics = f"/data/users/p2993/data_cpf/pics/{dom}/conc"
    if not os.path.exists(pics):
        os.makedirs(pics)
    
    # Nacitanie dat:
    conc = {}
    # calpuff:
    con = xr.open_dataset(f"{datadir['calpuff']}/annual-{dom}-{year}-{group}-{ggroups[group][0]}.nc")
    
    for ggroup in ggroups[group][1:]:
        ginp = xr.open_dataset(f"{datadir['calpuff']}/annual-{dom}-{year}-{group}-{ggroup}.nc")
        con = con + ginp
    
    conc['calpuff'] = con.fillna(0.0)
    conc['calpuff'].to_netcdf(f'/data/users/p2993/data_cpf/netcdf_groups/{dom}-{group}.nc')
    conc['calpuff']['NO2'] = conc['calpuff']['NOx']
    del conc['calpuff']['NOx']
    del conc['calpuff']['BaP']
    del conc['calpuff']['SO2']
    
    # atmostreet:
    conc['atmostr'] = xr.open_dataset(f"{datadir['atmostr']}/{dom}-{cpfa[group]}.nc")
    
    # Interpolacia calpuff do rovnakeho rastra ako atmostreet:
    concinter = conc['calpuff'].interp_like(conc['atmostr'], method='linear')
    
    # rozdiel:
    concdif = concinter - conc['atmostr']
    concdifp = concdif * 100/concinter
    
    seip = (concdif.dims['x'],concdif.dims['y'])
    sizex = 10
    asp = seip[1]/seip[0]
     
    for spc in specs:
        cif = concdif[spc]        
        figname = f"{pics}/calpuff-atmost_{spc}_{dom}_{group}.png"
        #fstring = f"(c > {filt[spc]} {unit(spc)})\n"
        fstring = "(CALPUFF - Atmostreet)"
        figtitle = f"Priemerné ročné koncentrácie {spc} - {opis[group]}\n{fstring}"    
        levs = 0
        plotting(lcc, cif , spc, figtitle, show_st,    figname, asp,levs)
        #plotting(lcc, cif , spc, figtitle, show_st,    figname, asp, 0)

      
