#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 12:06:39 2022

Skript na vykreslenie .nc poli pre celkove koncentracie aj sektorove.
Vykresluje subdomeny velkych domen

!!! spustat az po spusteni plot_total_maps.py

"""

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.io.img_tiles import OSM
import cartopy.io.img_tiles as cimgt
import xarray as xr
import pandas as pd
import geopandas as gpd
import sys
import os


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
sektor = {
      'neis': 'Zdroje NEIS',
      'heat': 'Lokálne vykurovanie',
      'road': 'Cestná doprava'
}
limit = {
    'PM10' : 40.0,
    'PM25' : 20.0,
    'BaP'  : 1.0,
    'NO2'  : 40.0
    }
newlimit = {
    'PM10' : 20.0,
    'PM25' : 10.0,
    'BaP'  : 1.0,
    'NO2'  : 20.0
    }

# Import projekcie do cartopy:
lcc = ccrs.LambertConformal(central_longitude=crsLCC['lon_0'], central_latitude=crsLCC['lat_0'],
                            standard_parallels=(crsLCC['lat_1'], crsLCC['lat_2']), 
                            false_easting=crsLCC['x_0'])

def plotting (proj, C, spc, figtitle, amstab, outfile, aspect,vmin, vmax, extent, units):
    '''
    Funkcia na vykreslovanie rastra xarray, Parametre:
    proj - projekcia vstupneho pola vo formate cartopy.crs
    C - xarray s mriezkou a hodnotami na zobrazenie v stlpci 'col'
    unit - string s jednotkami 
    figtitle - nazov mapy ktory chceme zobrazit
    amstab - pd dataframe s parametrami stanic na zobrazenie
    outfile - cesta k vyslednemu obrazku
    aspect - pomer vysky a sirky domeny
    lev - zoznam levelov pre vykreslovanie; ak lev = 0, nebudu specifikovane
    '''    
    #cmap = 'CMRmap_r'
    cmap = plt.get_cmap('jet', 20)
    
    plt.rcParams.update({'font.size': 14})
    plt.rcParams.update({'xtick.labelsize': 16})
    plt.rcParams.update({'ytick.labelsize': 16})
    plt.rcParams['figure.figsize'] = 15*aspect, 15
    
    hranica = gpd.read_file('/data/oko/krajc/GIS/admin_hranice/sr_1.shp')
    mapsource = OSM()
    # Vymenim extent lalo za extent v lcc (predtym mi toto neslo, preto bol lalo):
    # extent = get_lalo_extent_from_xarray(C)
       
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.add_image(mapsource, 13, interpolation='bilinear')
        
    a = C.plot.pcolormesh( alpha = 0.5, vmin=vmin, vmax=vmax, cmap=cmap,linewidth=0, 
                          antialiased=True, add_colorbar=False)
    cb = plt.colorbar(a,label=units,  orientation="vertical",
                      shrink=0.62)
   
    
    ax.set_title(figtitle, fontdict={'fontsize': '16', 'fontweight' : '4'})
    
    amstab.plot(ax=ax,transform=ccrs.PlateCarree(), marker='o', edgecolor='black',
            facecolor='red', markersize=12 )

    for x, y, label in zip(amstab.lon, amstab.lat, amstab.location):
        ax.text(x, y, f' AMS {label}', fontsize=9,  transform=ccrs.PlateCarree())

    ax.add_geometries(hranica.geometry, crs=ccrs.epsg(5514), edgecolor='k', facecolor='none')
    plt.savefig(outfile, dpi=300, bbox_inches='tight')    
    plt.show()

# Staticke data:

stations = pd.read_csv('/data/oko/krajc/GIS/ams/stanice_2022.csv') 
stations = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.lon, stations.lat))

# Domena a data specificke pre domenu:
    
year = 2021

groups = ['heat', 'road','neis']
spcs = ['PM10','PM25','NO2','BaP']
groups = ['neis']
dom = 'bratislava'
#show_st = stations[stations['city']==dom.upper()]
            

    # Cesta k vystupom:
pics = f"/data/users/p2993/data_cpf/pics/{dom}/conc-man/per"
if not os.path.exists(pics):
    os.makedirs(pics)

# Nacitanie dat:
conc = {}
for group in groups:
    conc[group] = xr.open_dataset(f'/data/users/p2993/data_cpf/netcdf/{dom}/{dom}-{year}-{group}.nc')
    conc[group] = conc[group].where(conc[group] >=0)
    conc[group] = conc[group].fillna(0.0)
c6h6=xr.open_dataset(f'/data/users/p2993/data_cpf/netcdf/{dom}/{dom}-{year}-{group}_c6h6-annual.nc')
conc['neis']['C6H6'] = c6h6['C6H6']


# Nacitanie subdomen:
subs = gpd.read_file(f"/data/oko/krajc/cpf_domeny/subdomains/{dom}.gpkg")
lsubs = list(subs['nazov'])
b = subs.bounds

# Vytvorenie a zapis gpkg suboru s obdlznikovymi sub. pre buduce pouzitie inde
bounding_box = subs.envelope
domshape = gpd.GeoDataFrame(gpd.GeoSeries(bounding_box), columns=['geometry'])
domshape.to_file(f"/data/oko/krajc/cpf_domeny/subdomains/{dom}_rectangles.gpkg", driver='GPKG')

cmap = 'cubehelix_r'
#cmapp = 'CMRmap_r'

for i in b.index:
    
    subdom = lsubs[i]
    extent = [b.loc[i]['minx'],b.loc[i]['maxx'],b.loc[i]['miny'],b.loc[i]['maxy']]
    asp = (extent[1]-extent[0])/(extent[3]-extent[2])
    show_st = gpd.overlay(stations, subs[subs.index==i].to_crs(4326), how='intersection')
    #for spc in specs[group]:    
    for spc in spcs:
        
        
### >>>>>>>> Vykreslovanie subgroups <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        for group in groups:
            cif = conc[group][spc]
            ctmp = conc[group][spc].rio.clip(subs.geometry[i])
            lmin = float(ctmp.min())
            lmax = float(ctmp.max())
            figname = f"{pics}/{spc}-{year}-{dom}-{i}-{group}-per.png"
        #fstring = f"(c > {filt[spc]} {unit(spc)})\n"
            fstring = f"{sektor[group]}\n"
            figtitle = f"Percentuálny podiel na celkových koncentráciách {spc} - {year}\n{fstring}"    
            units = '%'     
            plotting(lcc, cif , spc, figtitle, show_st,    figname, asp,lmin, lmax, extent, units)
    





