#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 12:06:39 2022

Skript na vykreslenie ucinkov maximalnych opatreni na redukciu emisii z lokalnych 
kurenisk. 
Vykresluje mapy koncentracii prekroceni priemernych rocnych hodnot,
Percentualny pokles po opatreniach a mapy prekroceni po opatreniach. 

"""

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.io.img_tiles import OSM
from cartopy.io.img_tiles import GoogleTiles
from cartopy.io.img_tiles import Stamen
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
limit = {
    'PM10' : 40.0,
    'PM25' : 20.0,
    'BaP'  : 1.0
    }

# Import projekcie do cartopy:
lcc = ccrs.LambertConformal(central_longitude=crsLCC['lon_0'], central_latitude=crsLCC['lat_0'],
                            standard_parallels=(crsLCC['lat_1'], crsLCC['lat_2']), 
                            false_easting=crsLCC['x_0'])

def plotting (proj, C, spc, figtitle, amstab, outfile, aspect, cbarunit, cmap, cmin, cmax, mark):
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
    
    #cmap = plt.get_cmap('jet', 20)
    #cmap = 'Reds_r'
    plt.rcParams.update({'font.size': 16})
    plt.rcParams.update({'xtick.labelsize': 16})
    plt.rcParams.update({'ytick.labelsize': 16})
    plt.rcParams['figure.figsize'] = 20, 20*aspect
    
    hranica = gpd.read_file('/data/oko/krajc/GIS/admin_hranice/sr_1.shp')
    mapsource = OSM()
    #mapsource = Stamen(style='terrain', cache=True)
    # Vymenim extent lalo za extent v lcc (predtym mi toto neslo, preto bol lalo):
    # extent = get_lalo_extent_from_xarray(C)
    extent = [C.x.values.min(), C.x.values.max(), C.y.values.min(), C.y.values.max()]
    
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.add_image(mapsource, 13, interpolation='bilinear')
  
    a = C.plot.pcolormesh( alpha = 0.4, cmap=cmap,linewidth=0, vmin=cmin, vmax=cmax,
                          antialiased=True, add_colorbar=False)
    cb = plt.colorbar(a,label=cbarunit,  orientation="vertical", shrink=0.62)
    
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
    
   # Vykreslenie AMS alebo miest:
    if mark == 'b':
        for x, y, label in zip(amstab.geometry.x, amstab.geometry.y, amstab.ShowOnMap):
            ax.text(x, y, f' {label}', fontsize=11,color='black', horizontalalignment='right',
                    transform=ccrs.PlateCarree()) 
    else:
        amstab.plot(ax=ax,transform=ccrs.PlateCarree(), marker='o', edgecolor='black',
                facecolor=None, markersize=14 )
        for x, y, label in zip(amstab.geometry.x, amstab.geometry.y, amstab.ShowOnMap):
            ax.text(x, y, f' {label}', fontsize=11,color='black', horizontalalignment='right',
                    transform=ccrs.PlateCarree())

    ax.add_geometries(hranica.geometry, crs=ccrs.epsg(5514), edgecolor='k', facecolor='none')
    # Biela maska mimo hranic kraja:
    m = plot_conc_v5.background_gdf(hranica)
    ax.add_geometries(m.geometry,crs=ccrs.epsg(5514),facecolor='white' )
    
    plt.savefig(outfile, dpi=300, bbox_inches='tight')    
    plt.show()

# Staticke data:
stations = gpd.read_file('/data/oko/krajc/dbase_calpuff/ams.data/ams2022.gpkg').to_crs(4326)
mesta = gpd.read_file("/data/oko/krajc/GIS/mesta_nazvy_SK/SK-mesta_pre_domeny.gpkg")

# Domena a data specificke pre do menu:
    

year = 2021
group = 'heat'
amsmesta = ['martin','zilina','ruzomberok','kosice','krompachy','banskabystrica']

# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','zarnovicanb','martin','prievidza', 'bratislava','kosice',
            'krompachy','nitra','juznyhont']

doms = ['banskabystrica','zarnovicanb','martin','prievidza','hnusta']
doms = ['nitra']

opatr = ['real','all']

scenar = {
    'real': 1,
    'all':2,
    'dry':3
    }

specs = ['PM10','PM25','BaP']

cmeas = {}
concp = {}
conctm = {}
for dom in doms:
    if dom == 'kosice':
        mx = {
            'BaP':7,
            'PM10':40,
            'PM25':20
            }
    else:
        levs = {'BaP':[],'PM10':[],'PM25':[],'NO2':[] }
        
    if dom in manbackg:
        suff = '-man'
    else:
        suff = ''
        
    domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
    if dom in amsmesta:
        show_points = gpd.overlay(stations, domshape.to_crs(4326), how='intersection')
        mark = 'a'
    else:
        show_points = gpd.overlay(mesta, domshape.to_crs(4326), how='intersection')
        show_points.columns =   ['ShowOnMap', 'cat', 'geometry']
        mark = 'b'   
                      
    # Cesta k vstupom:
    data = f"/data/users/p2993/data_cpf/netcdf/{dom}"
    
    # Cesta k vystupom:
    pics = f"/data/users/p2993/data_cpf/pics/{dom}/scenare{suff}"
    if not os.path.exists(pics):
        os.makedirs(pics)
        
    # Nacitanie dat:
   
    conct = xr.open_dataset(f"/data/users/p2993/data_cpf/netcdf_groups/{dom}-total{suff}.nc")
    conct = conct.fillna(0.0)
    # zakladny scenar
    conc0 = xr.open_dataset(f"{data}/annual-{dom}-{year}-{group}.nc")
    conc0 = conc0.where(conc0 >= 0)
    conc0 = conc0.fillna(0.0)
    conc0 = conc0.interp_like(conct)
    # Po opatreniach
    for meas in opatr:
        print(f"Working on dom: {dom} - scenario: {meas} ....\n")
        cmeas[meas] = xr.open_dataset(f"{data}/annual-{dom}-{year}-{group}-{meas}.nc")
        cmeas[meas] = cmeas[meas].where(cmeas[meas] >= 0)
        cmeas[meas] = cmeas[meas].fillna(0.0)
        cmeas[meas] = cmeas[meas].interp_like(conct)
    
        # Rozdiel heat:
        conc = cmeas[meas] - conc0
        # Redukcia celkovych koncentracii po opatreniach v percentach totalu:
        concp[meas] = conc * 100 / conct
        # Celkove koncentracie po opatreniach:
        conctm[meas] = conct + conc

    seip = (conct.dims['x'],conct.dims['y'])
    sizex = 10
    asp = seip[1]/seip[0]
  
    # ############# rocny priemer ####
    
    #for spc in specs[group]:    
    for spc in specs:
        if dom == 'kosice':
            cmin, cmax = limit[spc], mx[spc]
        else:
            cmin, cmax = limit[spc], float(conct[spc].max())
            '''
        # Mapa totalov v basic scenari - prekrocenia limitov- POZN:toto je presunute do plot_total_maps:
        cmap = 'jet'
        cif = conct[spc].where(conct[spc] > limit[spc])
        figname = f"{pics}/{spc}-{year}-{dom}-abovelim.png"
        fstring = f"(c > {limit[spc]} {unit(spc)})\n"
        figtitle = f"Priemerné ročné koncentrácie {spc}\n{fstring}"    
        levs = 0
        cbarunit = unit(spc)
        plotting(lcc, cif , spc, figtitle, show_points,figname, asp,levs, cbarunit, cmap)
        '''
        
        scen = 0
        for meas in opatr:
            scen = scenar[meas] 
            cmap = 'jet'
           
            # Mapa totalov po opatreniach - prekrocenia limitov:
            cif = conctm[meas][spc].where(conctm[meas][spc] > limit[spc])
            
            figname = f"{pics}/{spc}-{year}-{dom}-{scen}-abovelim.png"
            fstring = f"(Scenár {scen}: c > {limit[spc]} {unit(spc)})\n"
            figtitle = f"Priemerné ročné koncentrácie {spc}\n{fstring}"    
            
            cbarunit = unit(spc)
            plotting(lcc, cif , spc, figtitle, show_points,figname, asp, cbarunit, cmap, cmin, cmax, mark)
            '''
            # Percentualny pokles:
            cmap = 'jet_r'
            cif = concp[meas][spc].where(concp[meas][spc] < -10)
            
            figname = f"{pics}/{spc}-{year}-{dom}-{scen}-percentdrop.png"
            #fstring = f"(c > {filt[spc]} {unit(spc)})\n"
            fstring = f"(Scenár {scen}: pokles o viac ako 10 %)"
            figtitle = f"Priemerné ročné koncentrácie {spc} \n{fstring}"    
            cbarunit = '%'
            plotting(lcc, cif , spc, figtitle, show_points,figname, asp, cbarunit, cmap, cmin, cmax)
                   
           '''
               


