#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 12:06:39 2022

Skript na vykreslenie .nc poli pre celkove koncentracie.
Okrem obrazkov produkuje .nc subory s celkovymi koncentraciami (rocny priemer)
a .csv subory s timeseries pre bod pozadia (min. bod z rio)

"""

import cartopy.crs as ccrs
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

def plotting (proj, C, spc, figtitle, amstab, outfile, aspect,lev):
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
    plt.rcParams['figure.figsize'] = 15, 15*aspect
    
    hranica = gpd.read_file('/data/oko/krajc/GIS/admin_hranice/sr_1.shp')
    mapsource = cimgt.Stamen(style='terrain')
    # Vymenim extent lalo za extent v lcc (predtym mi toto neslo, preto bol lalo):
    # extent = get_lalo_extent_from_xarray(C)
    extent = [C.x.values.min(), C.x.values.max(), C.y.values.min(), C.y.values.max()]
    
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=proj)
    ax.add_image(mapsource, 13, interpolation='bilinear')
 
       
    if lev != 0:
        a = C.plot.pcolormesh( alpha = 0.4, levels=lev, cmap=cmap,linewidth=0, 
                              antialiased=True, add_colorbar=False)
        cb = plt.colorbar(a,label=unit(spc),  orientation="vertical",
                          shrink=0.62)
        cb.set_ticks(lev)
    else: 
        a = C.plot.pcolormesh( alpha = 0.4, cmap=cmap,linewidth=0, 
                              antialiased=True, add_colorbar=False)
        cb = plt.colorbar(a,label=unit(spc),  orientation="vertical",
                          shrink=0.62)
    
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
    
   # Vykreslenie AMS alebo miest:
    amstab.plot(ax=ax,transform=ccrs.PlateCarree(), marker='o', edgecolor='black',
            facecolor=None, markersize=14 )

    for x, y, label in zip(amstab.geometry.x, amstab.geometry.y, amstab.ShowOnMap):
        ax.text(x, y, f' {label}', fontsize=11,color='black', 
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

# Domena a data specificke pre domenu:
    
year = 2021
amsmesta = ['martin','zilina','ruzomberok','kosice','krompachy','banskabystrica']
doms = ['martin', 'ruzomberok','zilina','kysuce','orava','povazie']
doms = ['kosice', 'krompachy']
doms = ['banskabystrica','hnusta','jelsava','pohronie','brezno','juznyhont','jskotlina']
doms = ['juznyhont','kosice']
doms = ['kosice']
groups = ['heat', 'road','neis']

spcs = ['PM10','PM25','NO2','BaP']

for dom in doms:
    domshape = gpd.read_file(f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp')
    if dom in amsmesta:
        show_points = gpd.overlay(stations, domshape.to_crs(4326), how='intersection')
    else:
        show_points = gpd.overlay(mesta, domshape.to_crs(4326), how='intersection')
        show_points.columns =   ['ShowOnMap', 'cat', 'geometry']        
    # Cesta k vstupom:
    datafile = {}
    datafile['road'] = f"/data/oko/AtmostreetPostproc/{year}/Sectors/{dom}-{cpfa['road']}.nc"
    #datafile['neis'] = f"/data/users/p2993/data_cpf/netcdf/{dom}/annual-{dom}-{year}-neis-s-haldou.nc"
    datafile['neis'] = f"/data/users/p2993/data_cpf/netcdf/{dom}/annual-{dom}-{year}-neis.nc"
    datafile['heat'] = f"/data/users/p2993/data_cpf/netcdf/{dom}/annual-{dom}-{year}-heat.nc"
    datafile['rio'] = f"/data/users/p2993/data_cpf/rio/{dom}/cutout-orig.nc"
        # Cesta k vystupom:
    pics = f"/data/users/p2993/data_cpf/pics/{dom}/conc"
    if not os.path.exists(pics):
        os.makedirs(pics)
    
    
    # Nacitanie dat CALPUFF, ATMOSTREET:
    conc = {}
    for group in groups:
        conc[group] = xr.open_dataset(datafile[group])
        conc[group] = conc[group].where(conc[group] >=0)
        conc[group] = conc[group].fillna(0.0)
    
    # Interpolacia heat a neis do mriezky ATMOSTREET:
    for group in ['heat','neis']:
        conc[group] = conc[group].interp_like(conc['road'])
        conc[group]['NO2'] = conc[group]['NOx'] 
        #conc[group]['BAP'] = conc[group]['BaP']
        del conc[group]['NOx']
        #del conc[group]['BaP']
    
    # Nacitanie RIO:
    rio = xr.open_dataset(datafile['rio'])
    rioMean = rio.mean('times')
    # Najdenie polohy minima:
    minval = {}
    for par in list(rioMean.data_vars)[1:]:
        minarr = rioMean[par].where(rioMean[par]==rioMean[par].min(), drop=True).squeeze()
        minval[par] = [float(minarr),float(minarr.coords['x']), float(minarr.coords['y'])]
    
    # Vytvorenie backg datasetu s konstantnymi hodnotami:
    conc['backg'] = conc['road'].copy()
    for spc in spcs:
        conc['backg'][spc] = conc['backg'][spc]*0 + minval[spc.lower()][0]
    
    # Celkova koncentracia:
    concT = conc['backg']+conc['heat']+conc['road']+conc['neis']
    
    concT.to_netcdf(f"/data/users/p2993/data_cpf/netcdf_groups/{dom}-total.nc")
    # Percentualne podiely sektorov na totaloch:
    for group in groups:
        concp = conc[group]*100/concT
        concp.to_netcdf(f"/data/users/p2993/data_cpf/netcdf_groups/{dom}-sa-{group}.nc")
        
    # Export timeseries pre bod minval pre neskorsie pouzitie v plot_daily_SA_graphs.py:
    ams = {}
    for spc in spcs:
        spcl = spc.lower()
        ams[spc] = rio[spcl].sel(x=minval[spcl][1], y=minval[spcl][2]).to_dataframe()
        ams[spc] = ams[spc].drop(['x','y'], axis=1)
    allspc = pd.concat([ams['PM10'],ams['PM25'],ams['NO2'],ams['BaP']], axis=1)
    allspc.columns = spcs
    allspc.to_csv(f"/data/users/p2993/data_cpf/rio/{dom}/minpoint_tseries.csv")    
    
    seip = (concT.dims['x'],concT.dims['y'])
    sizex = 10
    asp = seip[1]/seip[0]
    
    cmap = 'cubehelix_r'
    #cmapp = 'CMRmap_r'
    
    # ############# rocny priemer ####
    
    for spc in spcs:
        
        for lim in (0, limit[spc], newlimit[spc]):
            cif = concT[spc].where(concT[spc] > lim) 
                
            figname = f"{pics}/{spc}-{year}-{dom}-total-{lim}.png"
            fstring = f"(c > {lim} {unit(spc)})\n"
            #fstring = ""
            figtitle = f"Priemerné ročné koncentrácie {spc} - {year} - celkové\n{fstring}"    
            
            #levs = lev[group][spc]
            levs = 0
            plotting(lcc, cif , spc, figtitle, show_points,    figname, asp,levs)
            #plotting(lcc, cif , spc, figtitle, show_st,    figname, asp, 0)

### >>>>>>>> Vykreslovanie subgroups <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    





