#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 14:40:08 2025

Tento skript vyprodukuje mapy CMAQ (priemerne rocne) pre identifikaciu
pozadovych bodov

@author: p2993
"""

import xarray as xr
import rioxarray

pth = "/data/oko/dusan/modelovanie_2023/pollutant_netcdf_2023"

pm10 = xr.open_dataset(f"{pth}/PM10_cmaq_2023_reanBC_SR.nc")
pm25 = xr.open_dataset(f"{pth}/PM25_cmaq_2023_reanBC_SR.nc")
no2 = xr.open_dataset(f"{pth}/NO2_ug_cmaq_2023_reanBC_SR.nc")

pm10mean = pm10['PM10'].mean('time')
pm25mean = pm25['PM25'].mean('time')
no2mean = no2['NO2_ug'].mean('time')

pm10mean = pm10mean.rio.set_spatial_dims(x_dim="COL", y_dim="ROW")
pm25mean = pm25mean.rio.set_spatial_dims(x_dim="COL", y_dim="ROW")
no2mean = no2mean.rio.set_spatial_dims(x_dim="COL", y_dim="ROW")

pm10mean.rio.to_raster("/data/oko/krajc/GIS/cmaq/pm10mean_2023.tif")
pm25mean.rio.to_raster("/data/oko/krajc/GIS/cmaq/pm25mean_2023.tif")
no2mean.rio.to_raster("/data/oko/krajc/GIS/cmaq/no2mean_2023.tif")
