#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 15:16:23 2019
Modifikacia pre 3D - polia v hladinach 1 az n - rychlost vetra:
Skript nacita .asc subory a vytvori jeden velky xarray dataset, exportuje ho 
do jedneho .nc suboru
POZOR: najprv treba spustit CALPOST na hpcdev01 (/data/oko/krajc/calpost/calpost_proc.py)
POZNAMKA: vyuziva na rozdiel of import_calpuff_to_xarray.py, kniznicu gdal na na-
citanie asc suborov. Predch. skript nacitaval ascii subory ako csv, takze neportre
boval gdal, ale po zahusteni GR asc subory ukazovali dvojnasobny pocet riadkov ako 
mali, comu som nerozumela

@author: p2993
"""
import numpy as np
import pandas as pd
import calendar
import xarray as xr
import rioxarray
import re
import os
from osgeo import gdal
import matplotlib.pyplot as plt

# Format nazvu suborov: 2018_M02_D01_0000(UTC+0100)_L00_1HR_mix.asc

year = 2023
dom = "bratislava"
res =float(250)        # resolution of GR (!!!! Treba zadat, neda sa zistit zo suboru)

   # resolution of GR (!!!! Treba zadat, neda sa zistit zo suboru)

spcs = ['usp','vsp']
projstring = "lcc +lat_1=48.75 +lat_2=49 +lat_0=47.7 +lon_0=19.5 +x_0=200000 +y_0=0 +ellps=WGS84 \
+towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
crs_wkt = 'PROJCS["Lambert_Conformal_Conic",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",\
    SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",\
    0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic"],\
    PARAMETER["standard_parallel_1",48.75],PARAMETER["standard_parallel_2",49],\
    PARAMETER["latitude_of_origin",47.7],PARAMETER["central_meridian",19.5],\
    PARAMETER["false_easting",200000],PARAMETER["false_northing",0],UNIT["Meter",1]]'

# Dictionaries kvoli atributom xarray:
names = {'usp':'u', 'vsp':'v', 'mix':'mht', 'pgt':'stab'}

 
ascpth = f"/work/users/p2993/prtmet/{dom}"
pthout = f"/data/oko/krajc/data_cpf/prtmet/{dom}"
if not os.path.exists(pthout):
    os.makedirs(pthout)
rerunfile = f"/users/p2993/cpf_proc/calmet/rerun{year}_{dom}.inp"
if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        dates = f_obj.readlines()
        
# Vytvorenie suradnic pre buduci xarray:
date = dates[0]
mm = date[5:7]
dd = date[8:10]
coordfile = f"{ascpth}/{year}_M{mm}_D{dd}_0000(UTC+0100)_L00_1HR_mix.asc" 

with open (coordfile) as f_obj:
    name, ncols = re.split(" ",f_obj.readline().rstrip())
    name, nrows = re.split(" ",f_obj.readline().rstrip())
    name, xll = re.split(" ",f_obj.readline().rstrip())
    name, yll = re.split(" ",f_obj.readline().rstrip())
    
ncols = int(ncols)
nrows = int(nrows)
xll = float(xll) * 1000
yll = float(yll) * 1000

#### Vytvorenie dims (x,y,z, times) #################
x = list(range(int(xll), int(xll + ncols*res), int(res)))
y = list(range(int(yll), int(yll + nrows*res), int(res)))
x = [float (i) for i in x]
y = [float (i) for i in y]
layers = [0,20,40,100,200,400,700,1100,1600,2000,3000]
z = list()
for i in range(len(layers)-1):
    z.append(np.mean(layers[i:i+2]))
### datumovy index pre obdobie epizod:
idx0 = []
for date in dates:
    mm = date[5:7]
    dd = date[8:10]
    for hh in range(24):
        idx0.append(f'{year}-{mm}-{dd} {hh:02d}:00:00')
    
# Citanie .asc suborov, konverzia do ndarray:
xds = xr.Dataset()
spc = 'usp'

for spc in spcs:
    print(f"Working on {spc}")
    a = {}
    for lev in range(1, len(layers)):
        print (f"Working on Level:{lev}")
        dtarr = {}
        i = -1
        for date in dates:
            
            mm = date[5:7]
            dd = date[8:10]
            
            for hh in range(24):
                i = i+1
                
                ascfile = f"{ascpth}/{year}_M{mm}_D{dd}_{hh:02d}00(UTC+0100)_L{lev:02d}_1HR_{spc}.asc" 
                
                raster = gdal.Open(ascfile)
                narray = raster.ReadAsArray()
                k = f"{idx0[i]}"
                dtarr[k] = np.flipud(narray)
                     
        a[lev] = np.stack(dtarr.values())       # np array pre jednu hladinu
    
    a4d = np.stack(a.values())    
    xds[names[spc]] = (('z','times','y','x'), a4d)
    
xds.coords['times'] = idx0
xds.coords['y'] = y
xds.coords['x'] = x
xds.coords['z'] = z
xds.attrs['domain'] = dom

xds.rio.write_crs(crs_wkt, inplace=True)
xds.attrs['projinfo'] = projstring

xds.to_netcdf(f"{pthout}/4D-{dom}-{year}.nc")

'''
# Selekcia a kreslenie
xds.mht.isel(times=6).plot.imshow(xticks=[], yticks=[], add_labels=None, size=10, aspect=1)
xds.mht.sel(times="2018-01-01 01:00:00").plot.imshow(xticks=[], yticks=[], add_labels=None,
               size=10, aspect=1)

    

# Denne priemery:
xad = xa.groupby('times.dayofyear').mean('times')

xa.to_netcdf("/data/oko/krajc/calpost/jelsava250/small2/{0}-{1}.nc".format(year,spc))        

# Plotting - 1 bod casovy rad:
xad1 = xad.sel(y=109375,x=254875)
xad1.plot()
'''

