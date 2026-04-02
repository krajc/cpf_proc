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

# Mriezku CMAQ najdem v tomto subore. (datove subory nie su georeferencovane)
grid = xr.open_dataset("/data/users/oko001/cmaq_oper_data/static_and_default_files/GRIDCRO2D_2021-01-01.nc") 
lat = grid['LAT']
lon = grid['LON']

def getclosest_ij(lats,lons,latpt,lonpt):
    # find squared distance of every point on grid
    dist_sq = (lats-latpt)**2 + (lons-lonpt)**2
    # 1D index of minimum dist_sq element
    minindex_flattened = dist_sq.argmin()
    # Get 2D index for latvals and lonvals arrays from 1D index
    return np.unravel_index(minindex_flattened, lats.shape)   

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
def background_conc (cmaq, spc, datum, btab):
    conclist = []
    for h in range(24):
        datehour = datum + pd.to_timedelta(h, unit='h')
        row = btab.loc[datehour,'row']
        col = btab.loc[datehour,'col']
        c = float(cmaq[spc].isel(TSTEP=h, ROW=row, COL=col, LAY=0))
        conclist.append(c)  
        cmean = sum(conclist)/len(conclist)
    return cmean     

doms = ['bb2','ke1']
                                             
res = 250
year = 2024
Z = 6 # 900 m (level pre vietor z CALMET)

for dom in doms:
    domshape = f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf'
    output = f'/data/users/p2993/data_cpf/cmaq/{year}/{dom}'
    clminp = f'/data/oko/krajc/data_cpf/prtmet/{year}/{dom}'
    # Cesta k CAMS vystupom SR:
    pth = f'/data/oko/products/combine/{year}'
    if not os.path.exists(output):
         os.makedirs(output)
         
    # Nacitanie meteo dat z CALMET:
    clm = xr.open_dataset(f"{clminp}/4D-{dom}-{year}.nc")
    
    # Create table with background cells coords and respective nearest CMAQ col/rows:
    btab = background_cells(Z)
    btab['col'] = 0
    btab['row'] = 0
    for i in btab.index:
        (dum1, dum2,btab.loc[i,'row'],btab.loc[i,'col']) = getclosest_ij(lat, lon, btab['windward_lat'][i], btab['windward_lon'][i])
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
            inp = f'{pth}/{mm:02d}/{datstr}_00/COMBINE_ACONC_v533_intel_com_00_0_24_{datstr.replace("-","")}.nc'
            cd = xr.open_dataset(inp)
            pm10 = background_conc (cd, 'PM10', dat, btab)
            pm25 = background_conc (cd, 'PM25_TOT',dat, btab)
            no2 = background_conc (cd, 'NO2_ug', dat, btab)
            bctable.loc[dat] = [pm10, pm25, no2]
    
    bctable.index.name = 'times'  
    bctable.columns =   ['PM10','PM25','NO2']    
    bctable.to_csv(f"{output}/cmaq-daily-backg-{dom}-{year}.csv")        
   
   
end_time = time.perf_counter()
cputime = (end_time-start_time)/60
print(f"Program finished in {cputime: .2f} minutes\n")