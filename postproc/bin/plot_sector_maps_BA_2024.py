#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 12:06:39 2022

Skript na vykreslenie .nc poli pre jednotlive sektory. Zalozeny na povodnom 
4_calpuff_plot_details_LCC.py. 

"""

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.io.img_tiles as cimgt
from cartopy.io.img_tiles import OSM
from cartopy.io.img_tiles import GoogleTiles
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
    'heat':['rd', 'bd', 'os', 'no'],
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

def plotting (proj, C, spc, figtitle, amstab, outfile, aspect,lev,units):
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
    if lev == 0:
        cmap = plt.get_cmap('jet', 20)
    else:
        cmap = 'jet'
    plt.rcParams.update({'font.size': 16})
    plt.rcParams.update({'xtick.labelsize': 16})
    plt.rcParams.update({'ytick.labelsize': 16})
    plt.rcParams['figure.figsize'] = 20, 20*aspect
    
    hranica = gpd.read_file('/data/oko/krajc/GIS/admin_hranice/sr_1.shp')
    #mapsource = cimgt.Stamen(style='terrain')
    mapsource = OSM()
    mapsource = cimgt.XYZTiles(
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
    )
    # Vymenim extent lalo za extent v lcc (predtym mi toto neslo, preto bol lalo):
    # extent = get_lalo_extent_from_xarray(C)
    extent = [C.x.values.min(), C.x.values.max(), C.y.values.min(), C.y.values.max()]
    
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.add_image(mapsource, 14, interpolation='bilinear')
       
    if lev != 0:
        a = C.plot.pcolormesh( alpha = 0.4, levels=lev, cmap=cmap,linewidth=0, 
                              antialiased=True, add_colorbar=False)
        cb = plt.colorbar(a,label=units,  orientation="vertical",
                          shrink=0.62)
        cb.set_ticks(lev)
    else: 
        a = C.plot.pcolormesh( alpha = 0.4, cmap=cmap,linewidth=0, 
                              antialiased=True, add_colorbar=False)
        cb = plt.colorbar(a,label=units,  orientation="vertical",
                          shrink=0.62)
    
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
   
    # Vykreslenie AMS alebo miest:
    amstab.plot(ax=ax,transform=ccrs.PlateCarree(), marker='o', edgecolor='black',
            facecolor=None, markersize=14 )

    for x, y, label in zip(amstab.geometry.x, amstab.geometry.y, amstab.ShowOnMap):
        ax.text(x, y, f' {label}', fontsize=11,color='black', 
                transform=ccrs.PlateCarree())
    '''
    # Vykreslenie miest:
    
    show_mes.plot(ax=ax,transform=ccrs.PlateCarree(), marker='o', edgecolor='black',
            facecolor='white', markersize=13 )
    
    for x, y, label in zip(show_mes.geometry.x, show_mes.geometry.y, show_mes.name):
        ax.text(x, y, f' {label}', fontsize=11, color='black', 
                transform=ccrs.PlateCarree())  
    ''' 
   
    ax.add_geometries(hranica.geometry, crs=ccrs.epsg(5514), edgecolor='k', facecolor='none')
    # Biela maska mimo hranic kraja:
    m = plot_conc_v5.background_gdf(hranica)
    ax.add_geometries(m.geometry,crs=ccrs.epsg(5514),facecolor='white' )
    
    plt.savefig(outfile, dpi=300, bbox_inches='tight')    
    plt.show()

# Staticke data:

stations = gpd.read_file('/data/oko/krajc/dbase_calpuff/ams.data/ams2022.gpkg').to_crs(4326)
mesta = gpd.read_file("/data/oko/krajc/GIS/mesta_nazvy_SK/SK-mesta_pre_domeny.gpkg")
# Domena a data specificke pre domenu:
    

year = 2024
group = 'road'
amsmesta = ['martin','zilina','ruzomberok','kosice','krompachy','banskabystrica','bratislava',
            'zarnovicanb','zvolen','nitra','presov']
# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','zarnovicanb','martin','prievidza', 'bratislava',
            'krompachy','kosice','nitra','juznyhont']
doms = ['kysuce','orava', 'povazie','martin','ruzomberok','zilina']
doms = ['banskabystrica','hnusta','zarnovicanb','martin','prievidza','krompachy','kosice']
doms = ['bratislava']
#doms = ['prievidza','myjava','trencin','javorniky']
#doms = ['kosice', 'krompachy']
#doms = ['banskabystrica','hnusta','jelsava','pohronie','brezno','juznyhont','jskotlina']
#doms = ['juznyhont','jskotlina','kysuce','orava']
#doms = ['hnusta','jelsava','pohronie','brezno','juznyhont','jskotlina', 'zarnovicanb','zvolen']
        
specs = ['PM10','PM25','NOx','BaP']


if group == 'road':
    specs.append('NO2')
    specs.remove('NOx')

#specs = ['PM10','PM25','BaP']   

for dom in doms:
    if dom not in manbackg:
        suff = ''
    else:
        suff = '-man'
        
    domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
    if dom in amsmesta:
        show_points = gpd.overlay(stations, domshape.to_crs(4326), how='intersection')
    else:
        show_points = gpd.overlay(mesta, domshape.to_crs(4326), how='intersection')
        show_points.columns =   ['ShowOnMap', 'cat', 'geometry']      
    
    # Cesta k vstupom:
    datadir = {}
    datadir['road'] = f"/data/users/p2993/data_cpf/netcdf_road"
    #datadir['neis'] = f"/data/oko/AtmostreetPostproc/{year}/Sectors"
    datadir['neis'] = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}"
    datadir['heat'] = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}"
    
    # Cesta k vystupom:
    pics = f"/data/users/p2993/data_cpf/pics/{year}/{dom}/conc{suff}"
    if not os.path.exists(pics):
        os.makedirs(pics)
        
    # Nacitanie dat:
    data = datadir[group]
    if group == 'road':
        conc = xr.open_dataset(f"{data}/annual-{dom}-{year}-road.nc")
        conc['NOx'] = conc['NO2']
        conc['BaP'] = conc['BAP']
    else:
        conc = xr.open_dataset(f"{data}/annual-{dom}-{year}-{group}.nc")
        
    conc = conc.where(conc >= 0)
    conc = conc.fillna(0.0)
    seip = (conc.dims['x'],conc.dims['y'])
    sizex = 10
    asp = seip[1]/seip[0]
    
    # Nacitanie percentualnych dat:
    concp = xr.open_dataset(f'/data/users/p2993/data_cpf/netcdf_groups/{year}/{dom}-sa-{group}{suff}.nc')
    concp['NOx'] = concp['NO2']
    concp['BaP'] = concp['BAP']
    cmap = 'cubehelix_r'
    #cmapp = 'CMRmap_r'
    
    # ############# rocny priemer ####
    for spc in specs:
        
        if group == 'road':
            cif = conc[spc]
            
        else:
            ci = interpol(conc[spc], 5)
            cif= ci
        
        figname = f"{pics}/{spc}-{year}-{dom}-{group}-per.png"
        fstring = f"{opis[group]}"
        figtitle = f"Percentuálny podiel na celkových koncentráciách {spc} - {year}\n{fstring}"   
        levs = 0
        units = '%'
        plotting(lcc, concp[spc] , spc, figtitle, show_points,  figname, asp,levs, units)
        
        
        figname = f"{pics}/{spc}-{year}-{dom}-{group}.png"
        #fstring = f"(c > {filt[spc]} {unit(spc)})\n"
        fstring = ""
        figtitle = f"Priemerné ročné koncentrácie {spc} - {year} - {opis[group]}\n{fstring}"    
        units = unit(spc)
        levs = 0
        plotting(lcc, cif , spc, figtitle, show_points,  figname, asp,levs, units)
        #plotting(lcc, cif , spc, figtitle, show_st,    figname, asp, 0)

### >>>>>>>> Vykreslovanie subgroups <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
'''        
zoznamfile = '/data/oko/krajc/dbase_calpuff/source/{}/zoznam_{}_all'.format(dom,group)
with open (zoznamfile) as f_obj:
    zoznam = f_obj.readlines()
    
for i in range(0,len(zoznam)):
    ggroup, num = re.split("\t",zoznam[i])
    if ggroup == 'Total':
        break
    gginp ="{}/annual-{}-{}-{}-{}.nc".format(data,domena,year,group,ggroup)
    # Nacitam koncentracie 
    conc = xr.open_dataset(gginp)
    # Vyrobim vsetky zoomlevels:
    c = {}
    c['z0'] = conc
    for i in zoom.keys():
       c[i] = conc.sel(x=slice(zoom[i][0], zoom[i][1]), 
                        y=slice(zoom[i][2], zoom[i][3]))
        
    for spc in specs[group]:
        
        for z in c.keys():
            
            if group != 'road':
                cif = interpol(c[z][spc], 5)
            else:
                cif = c[z][spc]
            
            figname = "{}/{}-{}-{}-{}-{}.png".format(pics,spc, year, dom,ggroup, z)
            figtitle = "Priemerné ročné koncentrácie {} - {}\n ({} - {})\n".format(
                    spc,  year, opis[group], opis[ggroup[len(dom)+1:]])
            
            plot_conc_v1.plot_cartopy_rast (lcc, cif , spc, figtitle, stations, 
                                                          figname, asp)

    

# CALPUFF plus RIO

ci = interpol(total)
cif= ci

figname = "{}/{}-{}-{}-point-rio.png".format(pics,spc, year, dom)
figtitle = "Celkové priemerné ročné koncentrácie {} \n".format(
        spc,  year, filt, unit(spc))

plot_conc_v1.plot_cartopy_rast (lcc, cif , spc, figtitle, stations,  
                                              figname, asp)

'''
    
    





