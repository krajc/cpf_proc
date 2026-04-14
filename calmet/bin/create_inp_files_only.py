#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Dce 1, 2022:
Skript  pripravi  potrebne calwrf a calmet.inp subory. 
Samotny run calmeta a calwrf je v skripte run_calwrf_calmet.py.

@author: p2993
"""

import os
import yaml
import xarray as xr
import numpy as np
import geopandas as gpd
import pandas as pd
import time

start_time = time.perf_counter()

calmettempl = "/users/p2993/cpf_proc/calmet/bin/templates/calmetWRF.templ"
calwrftempl = "/users/p2993/cpf_proc/calwrf/bin/templates/calwrf_dom.templ"

'''
parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
parser.add_argument('month', type=int)
parser.add_argument('day', type=int)
args = parser.parse_args()
'''

# read calwrf.inp template:
with open(calwrftempl) as f_obj:
    cwtempl = f_obj.readlines()
cwtempl = "".join(cwtempl)
# read calmet.inp template:
with open(calmettempl) as f_obj:
    cmtempl = f_obj.readlines()
cmtempl = "".join(cmtempl)

# Data aladin 2021 po konverzii pre CMAQ
datadir = "/data/users/oko001/alacon/outputs_old"
year = 2021
dom = 'ruzomberok'

scratchdir = "/scratch"
wrkdir = f'{scratchdir}/p2993'
#wrkdir = f'/work/users/p2993/calwrf/{dom}'
calwrfdir = '/users/p2993/cpf_proc/calwrf'
calmetdir = '/users/p2993/cpf_proc/calmet'
cwrkdir = '/work/users/p2993/calmet'

outdir = '/data/users/p2993/data_cpf/calmet'

     
def getclosest_ij(lats,lons,latpt,lonpt):
    # find squared distance of every point on grid
    dist_sq = (lats-latpt)**2 + (lons-lonpt)**2
    # 1D index of minimum dist_sq element
    minindex_flattened = dist_sq.argmin()
    # Get 2D index for latvals and lonvals arrays from 1D index
    return np.unravel_index(minindex_flattened, lats.shape)

def get_bbox(dom):
    
    ala = xr.open_dataset(f'{datadir}/2021-01-01_24h.nc')
    lat = ala.coords['XLAT']
    lon = ala.coords['XLONG']
    
    d = gpd.read_file(f"{domdir}/{dom}_LCCcpf")
    dwgs = d.to_crs(4326)      
    bbx = dwgs.bounds
    llx = float(bbx.minx )- 0.1
    lly = float(bbx.miny )- 0.05
    urx = float(bbx.maxx ) + 0.1
    ury = float(bbx.maxy ) + 0.05
    
    llpoint = getclosest_ij(lat,lon,lly,llx)
    urpoint = getclosest_ij(lat,lon,ury,urx)
    bboxstr = f"{llpoint[2]},{urpoint[2]},{llpoint[1]},{urpoint[1]}"
    return str(bboxstr)

def set_calwrf(dom, date, bboxstring):
        
        inpfile  = f'{datadir}/{date}_24h.nc'
        outfile  = f'{wrkdir}/{dom}-{date}_24h.m3d'
        lstfile = f'{wrkdir}/{dom}-{date}.lst'
        cconfile = f'{inpdir}/{date}.inp'
        
        text = cwtempl
        text = text.replace('__LSTFILE__', lstfile)
        text = text.replace('__OUTFILE__', outfile)
        text = text.replace('__INPFILE__', inpfile)
        text = text.replace('__BBOX__', bboxstring)
        
        with open(cconfile, 'w') as f:
            f.write(text)
           
def set_calmet(dom, date):
      
    m3ddat = f'{wrkdir}/{dom}-{date}_24h.m3d'
    lstdat =f'{cwrkdir}/{dom}/lst/{date}.lst'
    cconfile = f'{cinpdir}/{date}.inp'
    outfile = f'{outdir}/{dom}/{date}.dat'
    geodatfile = f'{geodat}/geo.dat'
    
    day = int(date[-2:])
    month = int(date[5:7])
    ibyr, ieyr = year, year
    ibmo, iemo = month, month
    ibdy, iedy = day, day
    ibhr, iehr = 0, 23
    ibsec, iesec = 0, 3600
    nx, ny = cfg['nx'], cfg['ny']
    dgridkm = cfg['dgridkm']
    xorigkm, yorigkm = cfg['xorigkm'], cfg['yorigkm']
    
    text = cmtempl
    text = text.replace('__LSTDAT__', lstdat)
    text = text.replace('__OUTFILE__', outfile)
    text = text.replace('__GEODAT__', geodatfile)
    text = text.replace('__M3DDAT__', m3ddat)
    text = text.replace('__IBYR__', str(ibyr))
    text = text.replace('__IEYR__', str(ieyr))
    text = text.replace('__IBMO__', str(ibmo))            
    text = text.replace('__IEMO__', str(iemo))
    text = text.replace('__IBDY__', str(ibdy))            
    text = text.replace('__IEDY__', str(iedy))
    text = text.replace('__IBHR__', str(ibhr))             
    text = text.replace('__IEHR__', str(iehr))
    text = text.replace('__IBSEC__', str(ibsec))
    text = text.replace('__IESEC__', str(iesec))
    text = text.replace('__NX__', str(nx))    
    text = text.replace('__NY__', str(ny))                
    text = text.replace('__DGRIDKM__', str(dgridkm))                    
    text = text.replace('__XORIGKM__', str(xorigkm))
    text = text.replace('__YORIGKM__', str(yorigkm))
    
    with open(cconfile, 'w') as f:
        f.write(text)
                            
  
##########################################################################################

domdir = "/users/p2993/cpf_domeny"

inpdir = f'{calwrfdir}/{dom}'
cinpdir = f"{calmetdir}/{dom}"
m3ddir = f'{wrkdir}' 
geodat = f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}'
confile = f'{geodat}/Domain_conf.yml' 
# Load Domain_conf config file
with open(confile) as file:
    cfg = yaml.full_load(file)
 
if not os.path.exists(cinpdir):
     os.makedirs(cinpdir)
if not os.path.exists(inpdir):
    os.makedirs(inpdir)

bboxpar = get_bbox(dom)

idx = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31',freq='1D')
dates = list(map(lambda x:str(x)[:10], idx ))

for date in dates:
  
# Prepare calwrf .inp files and run  calwrf
    set_calwrf(dom, date, bboxpar)
    set_calmet(dom, date)
    
finish_time = time.perf_counter()
cputime = finish_time-start_time
print(f"Program finished in {cputime: .0f} seconds\n")
