#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 5, 2023
Tento skript je zalozeny na povodnom ~/python/atmosys/CPF_postproc/doublecounting/
1_RIO_processing_for_daily.py, ktory povodne vyrabal gpkg subory pre dni a ZL. 
Upravila som ho aby vytvaral vyrez z RIO map pre domenu a ukladal vysledky
do datsetu so vsetkyi ZL a dnami.
 
@author: p2993
"""
import geopandas as gpd
import pandas as pd
import rasterio
import rioxarray
import xarray as xr
from pyproj import CRS
import os
import sys
import time
import argparse

start_time = time.perf_counter()
'''
parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
args = parser.parse_args()
'''
crs_wkt = 'PROJCS["Lambert_Conformal_Conic",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",\
    SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",\
    0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic"],\
    PARAMETER["standard_parallel_1",48.75],PARAMETER["standard_parallel_2",49],\
    PARAMETER["latitude_of_origin",47.7],PARAMETER["central_meridian",19.5],\
    PARAMETER["false_easting",200000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
                                                                           
dom = 'bratislava'
res = 250
year = 2023
#dom = args.domena
rerunfile = f'/users/p2993/cpf_proc/calmet/rerun{year}_{dom}.inp'
if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        dates = f_obj.readlines()
        dates = list(map(lambda x: x[:-1], dates))

domshape = f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf'
output = f'/data/users/p2993/data_cpf/rio/{year}/{dom}'
# Cesta k dennym RIO vystupom SR:
riopth = '/data/oko/RIO_archive/2021/2021_v1'
riopth = '/data/juraj/OPAQPY/data/maps/rio/output/2023_v0' 
if not os.path.exists(output):
     os.makedirs(output)

# zvacsena domena pre vyrezy 
reg = gpd.read_file(f'{domshape}')
regb = reg.buffer(2000,join_style=2)

dslist = []

for date in dates:
    
    print(f"Working on day: {date} ... \n")
    y, m, d = date.split('-')
    
    ds = xr.Dataset()
    for spc in ['pm10','pm25','no2','nox','bap']:
        
        inp = f'{riopth}/{spc}/{spc}_opt_da_1x1-{year}{m}{d}T000000.tif'
        big = rioxarray.open_rasterio(inp)
        big = big.rio.reproject(CRS.from_wkt(crs_wkt))
        clipped = big.rio.clip(regb.geometry)
        clipped = clipped.squeeze('band')
        del clipped.coords['band']
        clipped.coords['times'] = date
        ds[spc] = clipped
        
    dslist.append(ds)

bigds = xr.concat(dslist, dim='times')
    
bigds.to_netcdf(f"{output}/cutout-orig.nc")

end_time = time.perf_counter()
cputime = (end_time-start_time)/60
print(f"Program finished in {cputime: .2f} minutes\n")