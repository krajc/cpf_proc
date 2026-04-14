#!/users/p6065/anaconda3/envs/supergeo/bin/python

# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 15:16:23 2019

Pre 2D polia - v nultej hladine:
Skript nacita .asc subory a vytvori jeden velky xarray dataset, exportuje ho 
do jedneho .nc suboru

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

year = 2024
dom = "bratislava"
res = float(250)       # resolution of GR (!!!! Treba zadat, neda sa zistit zo suboru)

spcs = ['mix','pgt']
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

ascpth = f"/work/users/p2993/prtmet/{dom}/asc"
pthout = f"/data/oko/krajc/data_cpf/prtmet/{year}/{dom}"
if not os.path.exists(pthout):
    os.makedirs(pthout)

# Vytvorenie suradnic pre buduci xarray:
coordfile = f"{ascpth}/{year}_M01_D01_0000(UTC+0100)_L00_1HR_mix.asc" 


with open (coordfile) as f_obj:
    name, ncols = re.split(" ",f_obj.readline().rstrip())
    name, nrows = re.split(" ",f_obj.readline().rstrip())
    name, xll = re.split(" ",f_obj.readline().rstrip())
    name, yll = re.split(" ",f_obj.readline().rstrip())
    
    
ncols = int(ncols)
nrows = int(nrows)
xll = float(xll) * 1000
yll = float(yll) * 1000

#### Vytvorenie dims (x,y, times) #################

x = list(range(int(xll), int(xll + ncols*res), int(res)))
y = list(range(int(yll), int(yll + nrows*res), int(res)))
x = [float (i) for i in x]
y = [float (i) for i in y]
### datumovy index pre cele obdobie firstm az lastm:
firstm, lastm = 1, 12
days = calendar.monthrange(year,lastm)
start0 = f'{year}-01-01 00:00:00'
end = f'{year}-{lastm:02d}-{days[1]:02d} 23:00:00'
idx0 = pd.date_range(start=start0, end=end, freq='1H')


# Citanie .asc suborov, konverzia do ndarray:
xds = xr.Dataset()
spc = 'mix'

for spc in spcs:
    print(f"Working on {spc}")
    dtarr = {}
    i = -1
    for mm in range(firstm, lastm+1):
        print (f"Month:{mm}")
        days = calendar.monthrange(year, mm)
        
        for dd in range(1,days[1]+1):
        
            for hh in range(24):
                i = i+1
                
                ascfile = f"{ascpth}/{year}_M{mm:02d}_D{dd:02d}_{hh:02d}00(UTC+0100)_L00_1HR_{spc}.asc"
                
                raster = gdal.Open(ascfile)
                narray = raster.ReadAsArray()
                k = f"{idx0[i]}"
                dtarr[k] = np.flipud(narray)
                     
    a3d = np.stack(dtarr.values())
    xds[names[spc]] = (('times','y','x'), a3d)
    
xds.coords['times'] = idx0
xds.coords['y'] = y
xds.coords['x'] = x
xds.attrs['domain'] = dom

xds.rio.write_crs(crs_wkt, inplace=True)

xds.to_netcdf(f"{pthout}/2D-{dom}-{year}.nc")

'''
# Selekcia a kreslenie
xds.mht.isel(times=6).plot.imshow(xticks=[], yticks=[], add_labels=None, size=10, aspect=1)
xds.mht.sel(times="2017-08-01 04:00:00").plot.imshow(xticks=[], yticks=[], add_labels=None,
               size=10, aspect=1)

# vytvorenie xarray dataarray:
    xa = xr.DataArray(a3d, coords = [idx1, y, x], dims = ['times','y','x'])
    xa.name = names[spc]
    xa.attrs['units'] = "ug/m3 (BaP ng/m3)"
    xa.attrs['sourcegroup'] = group
    xa.attrs['subgroup'] = ggroup
    xa.attrs['domain'] = domena
    xa.attrs['projinfo'] = projstring
    xa = xa.to_dataset
    xdict[spc] = xa

# Denne priemery:
xad = xa.groupby('times.dayofyear').mean('times')

xa.to_netcdf("/data/oko/krajc/calpost/jelsava250/small2/{0}-{1}.nc".format(year,spc))        

# Plotting - 1 bod casovy rad:
xad1 = xad.sel(y=109375,x=254875)
xad1.plot()
'''

