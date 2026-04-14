#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 07:56:49 2025

@author: p2993
"""

import cartopy.crs as ccrs
from cartopy.io.img_tiles import OSM
from cartopy.io.img_tiles import GoogleTiles
import matplotlib.pyplot as plt
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

dom = 'bratislava'
year = 2021
pthsl = f'/data/users/p2993/data_cpf/netcdf/{year}/{dom}'
group = 'neis'
pics = f"/data/users/p2993/data_cpf/pics/{year}/{dom}/maps"
if not os.path.exists(pics):
    os.makedirs(pics)

concsl = xr.open_dataset(f'{pthsl}/{dom}-{year}-{group}-slovnaft.nc')
concsp = xr.open_dataset(f'{pthsl}/{dom}-{year}-{group}-spalovna.nc')


pth = f'/data/users/p2993/data_cpf/netcdf/{dom}'

cheat = xr.open_dataset(f'{pth}/{dom}-{year}-heat.nc')

cneis = xr.open_dataset(f'{pth}/{dom}-{year}-neis.nc')
benzen = xr.open_dataset(f'{pth}/{dom}-{year}-neis_c6h6-annual.nc')
cneis['C6H6'] = benzen['C6H6']

cneis_res = cneis - concsl
# Celkove priemerne rocne koncentracie !!! chyba mi tu total. Treba si premysliet co s tym. 
cheat = xr.open_dataset(f'{pth}/{dom}-sa-heat-man.nc')
croad = xr.open_dataset(f'{pth}/{dom}-sa-road-man.nc')
cneis = xr.open_dataset(f'{pth}/{dom}-sa-neis-man.nc')
crio = xr.open_dataset(f'{pth}/{dom}-sa-neis-man.nc')

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

stations = pd.read_csv('/data/oko/krajc/GIS/ams/stanice_2022.csv') 
stations = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.lon, stations.lat))

i=0  
subdom = lsubs[i]
extent = [b.loc[i]['minx'],b.loc[i]['maxx'],b.loc[i]['miny'],b.loc[i]['maxy']]
asp = (extent[1]-extent[0])/(extent[3]-extent[2])
show_st = gpd.overlay(stations, subs[subs.index==i].to_crs(4326), how='intersection')

spc = 'SO2'
c = cneis[spc]
c.rio.write_crs(lcc, inplace=True)
# Hodinove prekrocenia (pocet)
ch = c > 350
chn = ch.sum('times')
cif = chn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/{spc}-exceed-h.png"
figtitle = f"Pocet prekroceni hodinovej hodnoty 350 {units} {spc}\n"
     
plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)


# Denne prekrocenia (pocet)
cd = c.resample({'times':'D'}).mean() > 125
cdn = cd.sum('times')
cif = cdn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/{spc}-exceed-d.png"
figtitle = f"Pocet prekroceni priemernej dennej hodnoty 125 {units} {spc}\n"

plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)

# Zimny priemer
winter1 = c.sel(times=slice(f"{year}-01-01", f"{year}-03-31"))
winter2 = c.sel(times=slice(f"{year}-10-01", f"{year}-12-31"))
winter = xr.concat([winter1, winter2], dim='times')
c_wint = winter.mean('times')
ctmp = c_wint.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/{spc}-winter_mean.png"
figtitle = f"Priemerna zimna koncentracia {spc} ({units}) \n"

plotting(lcc, c_wint , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)

spc = 'NOx'
c = cneis[spc] # !!!!!! Tu treba uvazovat aj s ostatnymi sektormi!
c.rio.write_crs(lcc, inplace=True)
# Hodinove prekrocenia (pocet)
ch = c > 200
chn = ch.sum('times')
cif = chn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/{spc}-exceed-h.png"
figtitle = f"Pocet prekroceni hodinovej hodnoty 350 {units} NO2\n"
     
plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)


# Denne prekrocenia (pocet)
cd = c.resample({'times':'D'}).mean() > 50
cdn = cd.sum('times')
cif = cdn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/{spc}-exceed-d.png"
figtitle = f"Pocet prekroceni priemernej dennej hodnoty 50 {units} NO2\n"

plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)

# rocny priemer (vratane dopravy a kurenisk)
cif = c.mean('times')
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/{spc}-annual_mean.png"
figtitle = f"Priemerna rocna koncentracia NO2 ({units}) \n"

plotting(lcc, cif , spc, figtitle, show_st,    figname, asp,lmin , lmax, extent, units)

# NEIS PLUS SPALOVNA
########################################################
cnew = cneis + concsp
spc = 'SO2'
c = cnew[spc]
c.rio.write_crs(lcc, inplace=True)
# Hodinove prekrocenia (pocet)
ch = c > 350
chn = ch.sum('times')
cif = chn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/new-{spc}-exceed-h.png"
figtitle = f"Pocet prekroceni hodinovej hodnoty 350 {units} {spc}\npo realizacii\n"
     
plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)


# Denne prekrocenia (pocet)
cd = c.resample({'times':'D'}).mean() > 125
cdn = cd.sum('times')
cif = cdn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/new-{spc}-exceed-d.png"
figtitle = f"Pocet prekroceni priemernej dennej hodnoty 125 {units} {spc}\npo realizacii\n"

plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)

# Zimny priemer
winter1 = c.sel(times=slice(f"{year}-01-01", f"{year}-03-31"))
winter2 = c.sel(times=slice(f"{year}-10-01", f"{year}-12-31"))
winter = xr.concat([winter1, winter2], dim='times')
c_wint = winter.mean('times')
ctmp = c_wint.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/new-{spc}-winter_mean.png"
figtitle = f"Priemerna zimna koncentracia {spc} ({units}) \npo realizacii\n"

plotting(lcc, c_wint , spc, figtitle, show_st,    figname, asp,lmin, lmax, extent, units)

spc = 'NOx'
c = cslnew[spc] # !!!!!! Tu treba uvazovat aj s ostatnymi sektormi!
c.rio.write_crs(lcc, inplace=True)
# Hodinove prekrocenia (pocet)
ch = c > 200
chn = ch.sum('times')
cif = chn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/new-{spc}-exceed-h.png"
figtitle = f"Pocet prekroceni hodinovej hodnoty 350 {units} NO2\npo realizacii\n"
     
plotting(lcc, ctmp , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)


# Denne prekrocenia (pocet)
cd = c.resample({'times':'D'}).mean() > 50
cdn = cd.sum('times')
cif = cdn
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/new-{spc}-exceed-d.png"
figtitle = f"Pocet prekroceni priemernej dennej hodnoty 50 {units} NO2\npo realizacii\n"

plotting(lcc, cif , spc, figtitle, show_st,    figname, asp,1, lmax, extent, units)

# rocny priemer (vratane dopravy a kurenisk)
cif = c.mean('times')
ctmp = cif.rio.clip(subs.geometry[i])
#ctmp = cif.rio.clip(domshape.geometry[i])
ctmp = ctmp.where(ctmp > 0)
lmin = float(ctmp.min())
lmax = float(ctmp.max())
units = unit(spc)
figname = f"{pics}/new-{spc}-annual_mean.png"
figtitle = f"Priemerna rocna koncentracia NO2 ({units}) \npo realizacii\n"
plotting(lcc, cif, spc, figtitle, show_st,    figname, asp,lmin, lmax, extent, units)