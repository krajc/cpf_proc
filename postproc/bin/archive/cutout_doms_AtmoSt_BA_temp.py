#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript na pozeranie a porovnanie Hansovych vystupov -  produkuje vyrezy 
domen z velkeho tiffu a zapisuje ich. Pre dalsie spracovanie

@author: krajc
"""
import os
import geopandas as gpd
import rioxarray
import xarray as xr
from pyproj import CRS

crs_wkt = 'PROJCS["Lambert_Conformal_Conic",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",\
    SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",\
    0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic"],\
    PARAMETER["standard_parallel_1",48.75],PARAMETER["standard_parallel_2",49],\
    PARAMETER["latitude_of_origin",47.7],PARAMETER["central_meridian",19.5],\
    PARAMETER["false_easting",200000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
lcc = CRS.from_wkt(crs_wkt)                                                                           

year = 2022
#inpdir = "/data/oko/krajc/atmostreet"
#inpdir = "/data/users/p6065/atmostreet/Results/DOM_2021_zilinsky_kraj/SectorContribution"
inpdir = '/data/users/p6065/atmostreet/Results/SR_2021_traffic/pureSectors'
#inpdir = '/data/users/p6065/atmostreet/Results/BanskaBystrica_2021_Traffic/SectorContribution'
#inpdir = '/data/users/p6065/atmostreet/Results/Zilina_2021_Traffic/SectorContribution'
#inpdir = '/data/users/p6065/atmostreet/Results/Ruzomberok_2021_Traffic/SectorContribution'
inpdir = '/data/users/p6065/atmostreet/Results/Bratislava_2021_Traffic/SectorContribution'
inpdir = '/data/users/p6065/atmostreet/Results/SR_2022_NPM/SectorContribution'

outdir = f"/data/oko/AtmostreetPostproc/{year}/Sectors"
if not os.path.exists(outdir):
    os.makedirs(outdir)
domdir = "/data/oko/krajc/cpf_domeny"

sa = {
      'Background': 'Regionálne pozadie' ,
      'Industry': 'Priemysel a energetika',
      'Residential': 'Vykurovanie domácností',
      'Traffic': 'Cestná doprava'
    }
sectors = ['Traffic','Industry','Residential','Background']
#doms = ['martin','ruzomberok','zilina','kysuce','orava','povazie']
#doms = ['banskabystrica','hnusta','jelsava','pohronie','brezno','jskotlina']
#doms = ['trencin','prievidza','myjava','javorniky']
#doms = ['spis','presov','kosice','krompachy']
#doms = ['nitra','juznyhont','bratislava']
doms = ['zarnovicanb', 'zvolen']
doms = ['bratislava']

spcs = ["PM10","PM25",'NO2']

for sector in sectors:
    print(f'Working on sector {sector}:\n')
    astrlcc = {}
    for spc in spcs:
        print(f'processing {spc} ... \n')
        astr = rioxarray.open_rasterio(f"{inpdir}/{spc.upper()}_{sector}.tif")
        # Konverzia  do LCC
        astrlcc[spc] = astr.rio.reproject(lcc)
        astrlcc[spc] = astrlcc[spc].where(astrlcc[spc] >= 0)
        astrlcc[spc] = astrlcc[spc].squeeze('band')
        del  astrlcc[spc].coords['band']
        # Traffic ma emisie z BaP v kg, takze vystupy treba delit 1000
        if sector != 'Residential' and spc == 'BaP':
            astrlcc[spc] = astrlcc[spc]/1000
    print('Creating dataset ...\n')
    ds = xr.Dataset()
    ds.coords['x'] = astrlcc[spc].x
    ds.coords['y'] = astrlcc[spc].y
    for spc in spcs:
        ds[spc] = (('y','x'), astrlcc[spc].data)

    for dom in doms:
        print(f'Clipping domain: {dom}...\n')
        domshape = gpd.read_file(f"{domdir}/{dom}_LCCcpf/Creg.shp")
        clipped = ds.rio.clip(domshape.geometry)
        print(f'Writing to NetCDF file {dom}-{sector}.nc ... \n')
        clipped.to_netcdf(f"{outdir}/{dom}-{sector}.nc")
    




