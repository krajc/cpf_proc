#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 15:51:13 2025
    Making .nc file from ATMOSTREET tiffs, summing PM10 and PM2.5 with resuspension part
        *summing is done once for whole SR grid and saved as new .nc file
        *summing is done once for all SR station receptors timeseries and saved
        *
@author: p2993
"""
import rioxarray
import xarray as xr
import rasterio
import numpy as np
from pyproj import CRS
import pandas as pd
import geopandas as gpd

crs_wkt = 'PROJCS["Lambert_Conformal_Conic",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",\
    SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",\
    0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic"],\
    PARAMETER["standard_parallel_1",48.75],PARAMETER["standard_parallel_2",49],\
    PARAMETER["latitude_of_origin",47.7],PARAMETER["central_meridian",19.5],\
    PARAMETER["false_easting",200000],PARAMETER["false_northing",0],UNIT["Meter",1]]'


    
year = 2024                                                                                                                                        
inpdir = f"/data/users/p6065/ATMOSTREET/Results/{year}/SR_2024/Traffic"
outdir = "/data/users/p2993/data_cpf/netcdf_road"

'''
This part is only  run once or when ATMOSTREET output changes:
ds = xr.Dataset()
for spc in ['pm10','pm25','no2','bap', 'ben']:
    print (f"Domain: {dom}\tPollutant: {spc}\n")
    atm = rioxarray.open_rasterio(f"{inpdir}/{spc.upper()}_Mean_ATMO-Street.tif")
    atm = atm.where(atm != -9999.0, np.nan)
    ds[spc.upper()] = atm
    
print ("Add resuspension for PM...\n")
r10 = rioxarray.open_rasterio(f"{inpdir}/R10_Mean_ATMO-Street.tif")
r10 = r10.where(r10 != -9999.0, np.nan)
r25 = rioxarray.open_rasterio(f"{inpdir}/R25_Mean_ATMO-Street.tif")
r25 = r25.where(r25 != -9999.0, np.nan)
    
ds['PM10'] = ds['PM10'] + r10
ds['PM25'] = ds['PM25'] + r25
    
ds = ds.rio.reproject(CRS.from_wkt(crs_wkt))PM25-total-tt3-2024.csv
ds = ds.where(ds != -9999.0, np.nan)
ds = ds.where(ds < 1000, np.nan)
ds = ds.squeeze('band')
del ds.coords['band']
# Save:
ds.to_netcdf(f'{outdir}/SR_LCC_{year}.nc')

#### Procesing timeseries at receptor points #######
atmodir = f"/data/users/p6065/ATMOSTREET/Results/{year}/SR_2024/Traffic"
outdir = "/data/users/p2993/data_cpf/timeseries_road"

# Vzhladom na moznost chybajuceho stlpca date vo vystupoch Atmostreet vytvrorim daterange
indx = pd.date_range(f"{year}-01-01 00:00:00",f"{year}-12-31 23:00:00", freq='1H' )

def table (spc):
    if spc == 'NO2':
        t = pd.read_csv(f"{atmodir}/{spc}_HourlyTimeseries_ATMO-Street_Indicators.csv")
    else:
        t = pd.read_csv(f"{atmodir}/{spc}_HourlyTimeseries_ATMO-Street_Indicators.csv")
    t.index = indx
    tdaily = t.resample('D').mean()
    return tdaily

pm10 = table('PM10') + table('R10')
pm25 = table('PM25') + table('R25')
pm10.to_csv(f"{outdir}/PM10-total-SR-{year}.csv")
pm25.to_csv(f"{outdir}/PM25-total-SR-{year}.csv")
'''
# Cut out domains from already summed SR dataset:

ds = xr.open_dataset(f'{outdir}/SR_LCC_{year}.nc')
# clipping to domains:
olddoms = [ 'banskabystrica','ruzomberok']
domtable = gpd.read_file(f"/data/oko/krajc/cpf_domeny/new_doms_{year}_LCCcpf_processed/new_doms_{year}_LCCcpf_processed.shp")
doms = olddoms + list(domtable['domname'])
for dom in doms:
    dom = dom.lower()
    domshape = gpd.read_file(f"/data/oko/krajc/cpf_domeny/{dom}_LCCcpf/Creg.shp")
    clipped = ds.rio.clip(domshape.geometry)
    clipped.to_netcdf(f"{outdir}/annual-{dom}-{year}-road.nc")





