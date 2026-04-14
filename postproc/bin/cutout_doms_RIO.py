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

parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
args = parser.parse_args()

crs_wkt = 'PROJCS["Lambert_Conformal_Conic",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",\
    SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",\
    0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic"],\
    PARAMETER["standard_parallel_1",48.75],PARAMETER["standard_parallel_2",49],\
    PARAMETER["latitude_of_origin",47.7],PARAMETER["central_meridian",19.5],\
    PARAMETER["false_easting",200000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
                                                                           
#dom = 'zilina'
res = 250
year = 2024
dom = args.domena
domshape = f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf'
output = f'/data/users/p2993/data_cpf/rio/{year}/{dom}'
# Cesta k dennym RIO vystupom SR:
riopth = f'/data/oko/RIO_archive/{year}/{year}_v0'
riopth = "/data/oko/RIO_back_temp_2024"

if not os.path.exists(output):
     os.makedirs(output)

# zvacsena domena pre vyrezy 
reg = gpd.read_file(f'{domshape}')
regb = reg.buffer(2000,join_style=2)

idx0 = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='1D')
dslist = []

for date in idx0:
    
    print(f"Working on day: {str(date)} ... \n")
    m = date.month
    d = date.day
    
    ds = xr.Dataset()
    for spc in ['pm10','pm25','no2','bap']:
        
        inp = f'{riopth}/{spc}/{spc}_opt_da_1x1-{year}{m:02d}{d:02d}T000000.tif'
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