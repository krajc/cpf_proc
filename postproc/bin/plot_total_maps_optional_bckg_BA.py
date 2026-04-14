#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 12:06:39 2022

Skript na vykreslenie .nc poli pre celkove koncentracie.
Okrem obrazkov produkuje .nc subory s celkovymi koncentraciami (rocny priemer)
a .csv subory s timeseries pre bod pozadia (min. bod z rio)

"""

import cartopy.crs as ccrs
from cartopy.io.img_tiles import OSM
import matplotlib.pyplot as plt
import cartopy.io.img_tiles as cimgt
import xarray as xr
import pandas as pd
import geopandas as gpd
import sys
import os
import rioxarray


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

cpfa = {
      'neis': 'Industry',
      'heat': 'Residential',
      'road': 'Traffic'
}
limit = {
    'PM10' : 40.0,
    'PM25' : 20.0,
    'BAP'  : 1.0,
    'NO2'  : 40.0,
    'BEN'  : 5.0
    }
newlimit = {
    'PM10' : 20.0,
    'PM25' : 10.0,
    'BAP'  : 1.0,
    'NO2'  : 20.0,
    'BEN'  : 3.4
    }

# Import projekcie do cartopy:
lcc = ccrs.LambertConformal(central_longitude=crsLCC['lon_0'], central_latitude=crsLCC['lat_0'],
                            standard_parallels=(crsLCC['lat_1'], crsLCC['lat_2']), 
                            false_easting=crsLCC['x_0'])

 
def plotting (proj, C, spc, figtitle, amstab, mark, outfile, aspect,lev):
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
    if len(lev) == 0:
        cmap = plt.get_cmap('jet', 20)
    else:
        cmap = 'jet'
    plt.rcParams.update({'font.size': 16})
    plt.rcParams.update({'xtick.labelsize': 16})
    plt.rcParams.update({'ytick.labelsize': 16})
    plt.rcParams['figure.figsize'] = 15, 15*aspect
    
    hranica = gpd.read_file('/data/oko/krajc/GIS/admin_hranice/sr_1.shp')
    
    mapsource = OSM()
    mapsource = cimgt.GoogleTiles(
    url='https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
    )
   # mapshade = GoogleTiles(style='terrain')
    #mapsource = cimgt.Stamen(style='terrain')
    # Vymenim extent lalo za extent v lcc (predtym mi toto neslo, preto bol lalo):
    # extent = get_lalo_extent_from_xarray(C)
    #extent = [C.x.values.min(), C.x.values.max(), C.y.values.min(), C.y.values.max()]
    
    poly = domshape.geometry.iloc[0]
    minx, miny, maxx, maxy = poly.bounds
    extent = [minx, maxx, miny, maxy]
    
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
   # ax.add_image(mapsource, 14, interpolation='bilinear')
    ax.add_image(mapsource, 14)
       
    if len(lev) != 0:
        a = C.plot.pcolormesh( alpha = 0.4, vmin=lev[0], vmax=lev[1], cmap=cmap,linewidth=0, 
                              antialiased=True, add_colorbar=False)
        cb = plt.colorbar(a,label=unit(spc),  orientation="vertical",
                          shrink=0.62)
        
    else: 
        a = C.plot.pcolormesh( alpha = 0.4, cmap=cmap,linewidth=0, 
                              antialiased=True, add_colorbar=False)
        cb = plt.colorbar(a,label=unit(spc),  orientation="vertical",
                          shrink=0.62)
    
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
# V tomto subore su dopredu manualne vybrane body z RIO mapy ako pozadie:
riopoints = gpd.read_file("/data/oko/krajc/dbase_calpuff/geodat/background_points/doms_with_bckg_point_coords.gpkg")
riopoints.index = list(map(lambda x: x.lower(), riopoints['domname']))

  # Domena a data specificke pre domenu:
    
year = 2024
# Mesta kde chceme aby sa stanice volali podla ulic:
amsmesta = ['martin','zilina','ruzomberok','kosice','krompachy','banskabystrica','trencin',
            'bratislava','nitra','presov']
# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','zarnovicanb','martin','prievidza', 'bratislava',
            'krompachy','kosice','nitra', 'juznyhont']

doms = ['banskabystrica','zarnovicanb','martin','prievidza']
doms = ['bratislava']
'''
doms = ['kosice', 'krompachy']
doms = ['hnusta','jelsava','pohronie','brezno','juznyhont','jskotlina', 'zarnovicanb','zvolen',
        'krompachy']
'''
groups = ['heat', 'road','neis']

spcs = ['PM10','PM25','NO2','BAP', 'BEN']

exportRIO = 0   # ak chcem vzorkovat casove rady pre pozadie z RIO, hodnota = 1

for dom in doms:
    if dom == 'kosice':
        levs = {
            'BAP':[0,7],
            'PM10':[12,40],
            'PM25':[12,20],
            'NO2':[0,40]
            }
    else:
        levs = {'BAP':[],'PM10':[],'PM25':[],'NO2':[],'BEN':[] }
        
    domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
    if dom in amsmesta:
        show_points = gpd.overlay(stations, domshape.to_crs(4326), how='intersection')
        mark = 'a'
    else:
        show_points = gpd.overlay(mesta, domshape.to_crs(4326), how='intersection')
        show_points.columns =   ['ShowOnMap', 'cat', 'geometry']
        mark = 'b'        
    # Cesta k vstupom:
    datafile = {}
    #datafile['road'] = f"/data/oko/AtmostreetPostproc/{year}/Sectors/{dom}-{cpfa['road']}.nc"
    datafile['road'] = f"/data/users/p2993/data_cpf/netcdf_road/annual-{dom}-{year}-road.nc"
    datafile['neis'] = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}/annual-{dom}-{year}-neis.nc"
    datafile['heat'] = f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}/annual-{dom}-{year}-heat.nc"
    datafile['rio'] = f"/data/users/p2993/data_cpf/rio/{year}/{dom}/cutout-orig.nc"
    
    # Nacitanie slovnaftu - benzen
    slov = xr.open_dataset(f"/data/users/p2993/data_cpf/netcdf/{year}/{dom}//annual-bratislava-2024-neis-slovnaft-c6h6.nc")
    # Nacitanie dat CALPUFF, ATMOSTREET:
    conc = {}
    for group in groups:
        conc[group] = xr.open_dataset(datafile[group])
        conc[group] = conc[group].where(conc[group] >=0)
        conc[group] = conc[group].fillna(0.0)
       
    # Pridanie benzenu zo slovnaftu:
    conc['neis']['BEN']  = slov['c6h6']
    
    # orezanie ATMOSTREET dat na calpuff domenu:
    conc['road'] = conc['road'].rio.clip(domshape.geometry.values)
        
    # Interpolacia heat a neis do mriezky ATMOSTREET:
    for group in ['heat','neis']:
        conc[group] = conc[group].interp_like(conc['road'])
        conc[group]['NO2'] = conc[group]['NOx'] 
        conc[group]['BAP'] = conc[group]['BaP']
        del conc[group]['NOx']
        del conc[group]['BaP']
        
    # Kureniska nemaju benzen, treba ho doplnit ako nulovy
    conc['heat']['BEN'] = conc[group]['BAP']*0.0
      
    # Nacitanie RIO:
    rio = xr.open_dataset(datafile['rio'])
    rio['ben'] = 0.0 * rio['bap']
    rioMean = rio.mean('times')
    
    
    minval = {}
    if dom not in manbackg:
        suff = ''
       
        # Najdenie minima:
        for par in list(rioMean.data_vars)[1:]:
            minarr = rioMean[par].where(rioMean[par]==rioMean[par].min(), drop=True).squeeze()
            minval[par] = [float(minarr),float(minarr.coords['x']), float(minarr.coords['y'])]
    else:
        suff = '-man'
        minarr = rioMean.interp(x=riopoints['lcc_x'][dom], y=riopoints['lcc_y'][dom], method='nearest')
        for par in list(rioMean.data_vars)[1:]:
            minval[par] = [float(minarr[par]),float(minarr.coords['x']), float(minarr.coords['y'])]
    
    
    # Vytvorenie backg datasetu s konstantnymi hodnotami:
    conc['backg'] = conc['road'].copy()
    for spc in spcs:
        conc['backg'][spc] = conc['backg'][spc]*0 + minval[spc.lower()][0]
    
    # Celkova koncentracia:
    concT = conc['backg']+conc['heat']+conc['road']+conc['neis']
    # Zapis do .nc pre neskorsie pouzitie (je potrebne pre plot_sector_maps.py, kde sa pocitaju aj
    ncgroups = f"/data/users/p2993/data_cpf/netcdf_groups/{year}"
    if not os.path.exists(ncgroups):
        os.makedirs(ncgroups)
    # Totaly:
    concT.to_netcdf(f"{ncgroups}/{dom}-total{suff}.nc")
    # Percentualne podiely sektorov na totaloch:
    for group in groups:
        concp = conc[group]*100/concT
        concp.to_netcdf(f"{ncgroups}/{dom}-sa-{group}{suff}.nc")
        
    # Export timeseries pre bod minval pre neskorsie pouzitie v plot_daily_SA_graphs.py:
    if exportRIO ==1:
        ams = {}
        for spc in spcs:
            spcl = spc.lower()
            ams[spc] = rio[spcl].interp(x=minval[spcl][1], y=minval[spcl][2]).to_dataframe()
            ams[spc] = ams[spc].drop(['x','y'], axis=1)
        allspc = pd.concat([ams['PM10'],ams['PM25'],ams['NO2'],ams['BAP'], ams['BEN']], axis=1)
        allspc.columns = spcs
        allspc.to_csv(f"/data/users/p2993/data_cpf/rio/{year}/{dom}/minpoint_tseries{suff}.csv")    
    
    seip = (concT.dims['x'],concT.dims['y'])
    sizex = 10
    asp = seip[1]/seip[0]
    
    cmap = 'cubehelix_r'
    #cmapp = 'CMRmap_r'
    
    # Cesta k vystupom:
    pics = f"/data/users/p2993/data_cpf/pics/{year}/{dom}/conc{suff}"
    if not os.path.exists(pics):
        os.makedirs(pics)    
    
    for spc in spcs:
        
        lims = [limit[spc], newlimit[spc]]  
        #lims = [0, limit[spc], newlimit[spc]]
        for lim in lims:
            cif = concT[spc].where(concT[spc] > lim) 
                
            figname = f"{pics}/{spc}-{year}-{dom}-total-{lim}.png"
            fstring = f"(c > {lim} {unit(spc)})\n"
            #fstring = ""
            figtitle = f"Priemerné ročné koncentrácie {spc} - {year} - celkové\n{fstring}"    
            
           
            plotting(lcc, cif , spc, figtitle, show_points,mark, figname, asp,levs[spc])
            #plotting(lcc, cif , spc, figtitle, show_st,    figname, asp, 0)

### >>>>>>>> Vykreslovanie subgroups <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    





