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

year = 2023
epis = ['BA_2023_CAMS_FEB', 'BA_2023_CAMS_SEP']
#inpdir = "/data/oko/krajc/atmostreet"
#inpdir = "/data/users/p6065/atmostreet/Results/DOM_2021_zilinsky_kraj/SectorContribution"
#inpdir = '/data/users/p6065/atmostreet/Results/SR_2021_traffic/pureSectors'
#inpdir = '/data/users/p6065/atmostreet/Results/BanskaBystrica_2021_Traffic/SectorContribution'
#inpdir = '/data/users/p6065/atmostreet/Results/Zilina_2021_Traffic/SectorContribution'
#inpdir = '/data/users/p6065/atmostreet/Results/Ruzomberok_2021_Traffic/SectorContribution'
#inpdir = '/data/users/p6065/atmostreet/Results/Bratislava_2021_Traffic/SectorContribution'
#inpdir = '/data/users/p6065/atmostreet/Results/SR_2021_traffic_fixed/SectorContribution'

for epi in epis:
    inpdir = f"/data/users/p6065/ATMOSTREET/Results/{epi}/Traffic"
    
    outdir = f"/data/oko/AtmostreetPostproc/{year}/{epi}/Sectors"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    domdir = "/data/oko/krajc/cpf_domeny"
    
    sa = {
          'Background': 'Regionálne pozadie' ,
          'Industry': 'Priemysel a energetika',
          'Residential': 'Vykurovanie domácností',
          'Traffic': 'Cestná doprava'
        }
    sectors = ['Traffic']
    #doms = ['martin','ruzomberok','zilina','kysuce','orava','povazie']
    #doms = ['hnusta','jelsava','pohronie','brezno','jskotlina',
     #       'zarnovicanb', 'zvolen', 'juznyhont', 'kosice','krompachy']
    #doms = ['trencin','prievidza','myjava','javorniky']
    #doms = ['spis','presov','kosice','krompachy']
    doms = ['bratislava']
    
    
    spcs = ["PM10"]
    
    for sector in sectors:
        print(f'Working on sector {sector}:\n')
        astrlcc = {}
        for spc in spcs:
            print(f'processing {spc} ... \n') 
            astr = rioxarray.open_rasterio(f"{inpdir}/PM10_Mean_ATMO-Street.tif")
            # Konverzia  do LCC
            astrlcc[spc] = astr.rio.reproject(lcc)
            astrlcc[spc] = astrlcc[spc].where(astrlcc[spc] >= 0)
            astrlcc[spc] = astrlcc[spc].squeeze('band')
            del  astrlcc[spc].coords['band']
           
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
    




