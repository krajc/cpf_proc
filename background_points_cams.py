#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 5, 2025
Tento skript je zalozeny na cutouts_doms_RIO.py.
Vytahuje pozadie pre domeny z CMAQ na zaklade smeru vetra. Vysledkom su casove rady 
pozadovych hodnot

 
@author: p2993
"""
import numpy as np
import geopandas as gpd
import pandas as pd
from pyproj import Transformer
import xarray as xr
import os
import time
import calendar
import argparse

start_time = time.perf_counter()
'''
parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
args = parser.parse_args()
dom = args.domena
'''


# Dataframe s hodinovymi hodnotami pozadovych buniek:
def background_cells (Z):

    # Determine grid resolution (assuming regular grid)
    dx = float(clm.x[1] - clm.x[0])
    dy = float(clm.y[1] - clm.y[0])
    
    # Define the centers of the "outer belt" cells
    x_min_outer, x_max_outer = clm.x.min().item() - dx, clm.x.max().item() + dx
    y_min_outer, y_max_outer = clm.y.min().item() - dy, clm.y.max().item() + dy
    
    # 2. Select the center of the domain
    mid_x_idx, mid_y_idx = len(clm.x) // 2, len(clm.y) // 2
    x_c, y_c = clm.x.values[mid_x_idx], clm.y.values[mid_y_idx]
    
    # Extract time-series wind data at the center (using first vertical level z=Z)
    
    u_vec = clm.u.isel(z=Z, x=mid_x_idx, y=mid_y_idx).values
    v_vec = clm.v.isel(z=Z, x=mid_x_idx, y=mid_y_idx).values
    times = clm.times.values
    
    # 3. Setup Coordinate Transformer
    # Using the projinfo from your file: LCC with specific parallels and origin
    proj_params = (
        "+proj=lcc +lat_1=48.75 +lat_2=49.0 +lat_0=47.7 +lon_0=19.5 "
        "+x_0=200000 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    )
    # Transformer from Projected (LCC) to Geographic (Lat/Lon)
    transformer = Transformer.from_crs(proj_params, "EPSG:4326", always_xy=True)
    
    results = []
    
    for i in range(len(times)):
        u, v = u_vec[i], v_vec[i]
        speed = np.sqrt(u**2 + v**2)
        # Wind direction (Meteorological: where it comes FROM)
        # atan2(u,v) is direction TO; we add 180 to get FROM
        wdir = (np.degrees(np.arctan2(u, v)) + 180) % 360
        
        if speed < 0.1: # Handle calm conditions
            results.append([times[i],u, v,  speed, wdir, ww_x0, ww_y0, lon0, lat0])
            print(f"{times[i]} wind speed < 0.1 ... taking previous step coords\n")
            continue
    
        # 4. Find the intersection with the outer belt
        # We trace back from (x_c, y_c) along vector (-u, -v)
        # Equation: x = x_c - u*t, y = y_c - v*t
        t_cands = []
        if u > 0: t_cands.append((x_c - x_min_outer) / u)  # Hits left
        elif u < 0: t_cands.append((x_c - x_max_outer) / u) # Hits right
        if v > 0: t_cands.append((y_c - y_min_outer) / v)  # Hits bottom
        elif v < 0: t_cands.append((y_c - y_max_outer) / v) # Hits top
        
        t_hit = min([t for t in t_cands if t > 0])
        
        # Calculate exact intersection
        raw_x, raw_y = x_c - u * t_hit, y_c - v * t_hit
        
        # 5. Snap to the nearest cell center in the outer belt
        # This ensures the coordinate represents a "cell center"
        all_x_centers = np.append(np.insert(clm.x.values, 0, x_min_outer), x_max_outer)
        all_y_centers = np.append(np.insert(clm.y.values, 0, y_min_outer), y_max_outer)
        
        ww_x = all_x_centers[np.abs(all_x_centers - raw_x).argmin()]
        ww_y = all_y_centers[np.abs(all_y_centers - raw_y).argmin()]
    
        # 6. Convert to Lat/Lon
        lon, lat = transformer.transform(ww_x, ww_y)
        
        results.append([times[i], u, v, speed, wdir, ww_x, ww_y, lon, lat])
        # save for next timestep in case it contains calm:
        ww_x0, ww_y0, lon0, lat0 = ww_x, ww_y, lon, lat
    
    # Final DataFrame
    df = pd.DataFrame(results, columns=[
        'datetime','u','v', 'wind_speed', 'wind_direction', 
        'windward_X', 'windward_Y','windward_lon', 'windward_lat' 
    ])
    return df

# Extract 24 hourly concentrations from  CMAQ file and make daily mean:
def background_conc_CAMS (ds, spc, btab):
    """
    Automatically aligns ds and btab by time using metadata, 
    extracts point-wise values, and returns the daily mean.
    """
    # 1. Parse the starting date from attributes (e.g., '20240201')
    # ds.attrs['FORECAST'] example: "Europe, 20240201+[0H_24H]"
    forecast_str = ds.attrs['FORECAST'].split(',')[1].strip().split('+')[0]
    base_time = pd.to_datetime(forecast_str, format='%Y%m%d')
    
    # 2. Convert ds timedeltas to absolute DatetimeIndex
    ds_abs = ds.copy()
    ds_abs['time'] = base_time + ds.time
    
    # 3. Filter btab for the exact range of the dataset
    # This avoids 'nearest' logic and ensures we only use existing timestamps
    time_min, time_max = ds_abs.time.min().values, ds_abs.time.max().values
    btab_subset = btab.loc[time_min:time_max]
    
    # 4. Check for alignment
    if len(btab_subset) != len(ds_abs.time):
        # Optional: Print a warning or handle missing rows
        # For now, we align the dataset to only the times present in btab
        ds_abs = ds_abs.sel(time=btab_subset.index)
    
    # 5. Create coordinate DataArrays for vectorized indexing
    # This ensures each time step in ds picks its specific lat/lon from btab
    lats = xr.DataArray(btab_subset['windward_lat'].values, dims="time", coords={"time": ds_abs.time})
    lons = xr.DataArray(btab_subset['windward_lon'].values, dims="time", coords={"time": ds_abs.time})
    
    # 6. Extract Level 0 values at the moving coordinates
    # Using .sel() with the DataArrays extracts a 1D 'time' series
    extracted_series = ds_abs[spc].sel(
        level=0.0,
        latitude=lats,
        longitude=lons,
        method='nearest'
    )
    
    # 6. Return the mean (handles the 25 points if present)
    return float(extracted_series.mean().values) 
                                               
dom = 'banskabystrica'
res = 250
year = 2024
Z = 6 # 900 m (level pre vietor z CALMET)

domshape = f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf'
output = f'/data/users/p2993/data_cpf/cams/{year}/{dom}'
clminp = f'/data/oko/krajc/data_cpf/prtmet/{year}/{dom}'
# Cesta k CAMS vystupom SR:
pth = f'/data/oko/products/cams_files/{year}'
if not os.path.exists(output):
     os.makedirs(output)
     
# Nacitanie meteo dat z CALMET:
clm = xr.open_dataset(f"{clminp}/4D-{dom}-{year}.nc")

# Create table with background cells coords and respective nearest CMAQ col/rows:
btab = background_cells(Z)

btab.set_index('datetime', inplace = True) 
# Save the table for checkup
btab.to_csv(f"{output}/background_cells_{dom}-{year}.csv")
  
# Final dataframe with background concentrations:
bctable = pd.DataFrame(columns = ['pm10','pm25','no2'])

for mm in range(1,13):
    eday = calendar.monthrange(year, mm)[1]
    idx = pd.date_range(start=f'{year}-{mm:02d}-01', end=f'{year}-{mm:02d}-{eday}', freq='1D')
    sidx = idx.astype(str)
    print(f"Working on month: {str(mm)} ... \n")
    for dat in idx:
        print(f"Day {dat} ...\n")
        datstr = str(dat)[:10]
        inp1 = f'{pth}/{mm:02d}/{datstr}/download_{datstr}_CAMS_EUROPE_00+24_full.nc'
        cd = xr.open_dataset(inp1)
        pm10 = background_conc_CAMS (cd, 'pm10_conc', btab)
        pm25 = background_conc_CAMS (cd, 'pm2p5_conc',btab)
        inp2 = f'{pth}/{mm:02d}/{datstr}/download_{datstr}_CAMS_EUROPE_00+24_selected.nc'
        cd = xr.open_dataset(inp2)
        no2 = background_conc_CAMS (cd, 'no2_conc', btab)
        bctable.loc[dat] = [pm10, pm25, no2]

bctable.index.name = 'times' 
bctable.columns =   ['PM10','PM25','NO2']
bctable.to_csv(f"{output}/cams-daily-backg-{dom}-{year}.csv")        
   
   
end_time = time.perf_counter()
cputime = (end_time-start_time)/60
print(f"Program finished in {cputime: .2f} minutes\n")