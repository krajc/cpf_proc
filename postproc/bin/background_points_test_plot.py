#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 5, 2025
Tento skript je zalozeny na cutouts_doms_RIO.py.
Vytahuje pozadie pre domeny z CMAQ na zaklade smeru vetra. Vysledkom su casove rady 
pozadovych hodnot

 
@author: p2993
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
import cartopy.crs as ccrs

plt.rcParams['figure.dpi'] = 200

def plot_windward_cell(target_date):
    ts = pd.to_datetime(target_date)
    mm, dd, hh = target_date[5:7], target_date[8:10], target_date[11:13]
    # 3. Load Concentration Data
    daily_file = f"{cmaqdir}/{mm}/{target_date[:10]}_00/COMBINE_ACONC_v533_intel_com_00_0_24_{year}{mm}{dd}.nc"
    try:
        ds_conc = xr.open_dataset(daily_file)
        pm10_vals = ds_conc['PM10'].isel(TSTEP=ts.hour, LAY=0).values
    except Exception as e:
        print(f"Skipping {target_date}: {e}")
        return
    
    # Setup Plot with Cartopy
    
    ax = plt.axes(projection = ccrs_clm)
    ax.set_extent(ext, crs=ccrs_clm)
        
    # 5. Plot PM10 Background (using raw Lon/Lat as coordinates)
    # transform=ccrs.PlateCarree() tells cartopy these coords are degrees
    im = ax.pcolormesh(lon_coords, lat_coords, pm10_vals, 
                       transform=ccrs.PlateCarree(),
                       cmap='YlOrRd', shading='auto',
                       vmin=0, vmax=40, alpha=0.7)
    
    # 6. Plot the Domain Boundary (the 'ds' file extent)
    # Assuming ds.x and ds.y are already in the map_proj coordinates
    ax.plot([clm.x.min(), clm.x.max(), clm.x.max(), clm.x.min(), clm.x.min()],
            [clm.y.min(), clm.y.min(), clm.y.max(), clm.y.max(), clm.y.min()],
            color='navy', lw=1)

    # 7. Plot Windward Cell & Wind Vector
    row = df.loc[ts]
    # Note: windward_X/Y must be in the same units/projection as projection
    ax.scatter(row['windward_X'], row['windward_Y'], 
               facecolors= 'none', marker='s', s=100, edgecolors='red', 
                zorder=5)

    mid_x, mid_y = clm.x.values[len(clm.x)//2], clm.y.values[len(clm.y)//2]
    ax.quiver(mid_x, mid_y, row['u'], row['v'], 
              color='black', scale=0.007, scale_units='xy', 
              zorder=6)
    ax.text(mid_x, mid_y - 2000,  # Offset by 2km (adjust depending on your map scale)
            f"{row['wind_speed']:.1f} m/s", ha='center', va='top', 
            fontsize=10, fontweight='bold', color='black',   zorder=30)
    # 8. Final Touches
    plt.colorbar(im, ax=ax, label='PM10 [$\mu g/m^3$]', fraction=0.046, pad=0.04)
    ax.set_title(f"PM10 Background Analysis: {target_date[:-3]}", fontsize=10)
    
    plt.show()
    


dom = 'bratislava'
year = 2024
domshape = f'/data/oko/krajc/cpf_domeny/{dom}_LCCcpf'
output = f'/data/users/p2993/data_cpf/cmaq/{year}/{dom}'

clminp = f'/data/oko/krajc/data_cpf/prtmet/{year}/{dom}'
cmaqdir = f'/data/oko/products/combine/{year}'
# Load CMAQ Grid Metadata
grid = xr.open_dataset("/data/users/oko001/cmaq_oper_data/static_and_default_files/GRIDCRO2D_2021-01-01.nc")
lat_coords = grid['LAT'].isel(TSTEP=0, LAY=0).values
lon_coords = grid['LON'].isel(TSTEP=0, LAY=0).values
# Load CALMET file
clm = xr.open_dataset(f"{clminp}/4D-{dom}-{year}.nc")                                                
# Get projections:
    #  CALMET projection:
vals = clm.spatial_ref.attrs
# Create the standard Cartopy Lambert Conformal projection
# This class has the .boundary method implemented, solving your error.
ccrs_clm = ccrs.LambertConformal(
    central_longitude=vals['longitude_of_central_meridian'],
    central_latitude=vals['latitude_of_projection_origin'],
    standard_parallels=(
        vals['standard_parallel'][0], 
        vals['standard_parallel'][1]
    ),
    false_easting=vals['false_easting'],
    false_northing=vals['false_northing'],
    # Explicitly use WGS84 globe to match your metadata
    globe=ccrs.Globe(ellipse='WGS84')
)

    # CMAQ projection:
# Define the Projection from File Attributes
    # Standard CMAQ LCC parameters
ccrs_cmaq = ccrs.LambertConformal(
        central_longitude=grid.attrs['P_ALP'], 
        central_latitude=grid.attrs['P_GAM'],
        standard_parallels=(grid.attrs['P_BET'], grid.attrs['P_GAM'])
)

# Define map extent:
buf = 4000.     # zvacsenie CALMET domeny
ext = [float(clm.x.min())-buf,float(clm.x.max())+buf,
       float(clm.y.min())-buf, float(clm.y.max())+buf]

# Read file with background cells:
df = pd.read_csv(f"{output}/background_cells_{dom}-{year}.csv")
df.index = pd.to_datetime(df.datetime)

m = [1, 1]
dd = 23

for mm in range (m[0], m[1] + 1):
    for hh in range(24):
        dtime = f"{year}-{mm:02d}-{dd:02d} {hh:02d}:00:00"
        plot_windward_cell(dtime)