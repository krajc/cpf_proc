#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 09:22:18 2022
Skript spusta pre domenu a mesiac zadane v argumente skriptu retaz CALWRF
a CALMET. Predtym si pripravi  potrebne calwrf a calmet.inp subory.
Po dokonceni si posebe vycisti "medziprodukty" - m3d, m2d a calwrf.lst

@author: p2993
"""

import os
import sys
import argparse
import pandas as pd
import subprocess
import calendar
import yaml
import xarray as xr
import numpy as np
import geopandas as gpd

calwrftempl = "/users/p2993/calwrf/bin/calwrf_dom.templ"
calmettempl = "/users/p2993/calmet/bin/calmetWRF.templ"

parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
parser.add_argument('month', type=int)
args = parser.parse_args()

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
        outfile  = f'{wrkdir}/m3d/{dom}/{dom}-{date}_24h.m3d'
        lstfile = f'{wrkdir}/lst/{dom}/{dom}-{date}.lst'
        cconfile = f'{inpdir}/{date}.inp'
        
        text = cwtempl
        text = text.replace('__LSTFILE__', lstfile)
        text = text.replace('__OUTFILE__', outfile)
        text = text.replace('__INPFILE__', inpfile)
        text = text.replace('__BBOX__', bboxstring)
        
        with open(cconfile, 'w') as f:
            f.write(text)
           
def set_calmet(dom, date, day):
      
    m3ddat = f'{wrkdir}/m3d/{dom}/{dom}-{date}_24h.m3d'
    lstdat =f'{cwrkdir}/lst/{dom}/{date}.lst'
    cconfile = f'{cinpdir}/{date}.inp'
    outfile = f'{outdir}/{dom}/{date}.dat'
    geodatfile = f'{geodat}/geo.dat'
    
    ibyr, ieyr = year, year
    ibmo, iemo = month, month
    ibdy, iedy = day.day, day.day
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
                            
def remove_trash():
    for f in os.listdir(f'{wrkdir}/m3d/{dom}'):
        os.remove(os.path.join(f'{wrkdir}/m3d/{dom}', f))
    for f in os.listdir(f'{wrkdir}/lst/{dom}'):
        os.remove(os.path.join(f'{wrkdir}/lst/{dom}', f))
    for f in os.listdir(f'{outdir}/{dom}'):
        if f[-3:] == 'aux':
            os.remove(os.path.join(f'{outdir}/{dom}', f))
    
##########################################################################################
calwrfdir = '/users/p2993/calwrf'
calmetdir = '/users/p2993/calmet'
cwrkdir = '/work/users/p2993/calmet'

wrkdir = '/work/users/p2993/calwrf'
outdir = '/data/users/p2993/data_cpf/calmet'

if not os.path.exists(f'{wrkdir}/m3d'):
     os.makedirs(f'{wrkdir}/m3d') 
if not os.path.exists(f'{wrkdir}/lst'):
     os.makedirs(f'{wrkdir}/lst')               
if not os.path.exists(outdir):
     os.makedirs(outdir)
     
domdir = "/users/p2993/cpf_domeny"
dom = args.domena
'''
Po zbehnuti vsetkych domen bude treba vykonat zaverecnu kontrolu vyprodukovanych
calmet.dat suborov. Na to je potrebne zistit velkost 1 validneho suboru z kazdej
domeny, a zapisat suboru na neskorsie pouzitie. Zatial ale toto robim dodatocne
v check_file_sizes.py, sem pridam pri dalsom spustani na bud. rok
'''
 
cinpdir = f"{calmetdir}/{dom}"
#geodat = f'/data/users/p2993/dbase_calpuff/geodat/{dom}'
geodat = f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}'
confile = f'{geodat}/Domain_conf.yml' 
# Load Domain_conf config file
with open(confile) as file:
    cfg = yaml.full_load(file)
 
if not os.path.exists(f'{cwrkdir}/lst/{dom}'):
     os.makedirs(f'{cwrkdir}/lst/{dom}')  
if not os.path.exists(f"{outdir}/{dom}"):
     os.makedirs(f"{outdir}/{dom}")    
if not os.path.exists(cinpdir):
     os.makedirs(cinpdir)
inpdir = f'{calwrfdir}/{dom}'
if not os.path.exists(inpdir):
    os.makedirs(inpdir)
m3ddir = f'{wrkdir}/m3d/{dom}'   
if not os.path.exists(m3ddir):
    os.makedirs(m3ddir)
if not os.path.exists(f'{wrkdir}/lst/{dom}'):
    os.makedirs(f'{wrkdir}/lst/{dom}')
    
bboxpar = get_bbox(dom)

month = args.month

ndays = calendar.monthrange(year, month)
ndays = ndays[1]   
start, end = f'{year}-{month:02d}-01', f'{year}-{month:02d}-{ndays:02d}' 
idx = pd.date_range(start=start, end=end,freq='1D')

print (f"processing domain: {dom.upper()}:")
for day in idx:
    dt = str(day)
    date = dt[:10]    
    # Prepare calwrf .inp files
    set_calwrf(dom, date, bboxpar)
    
    # Prepare calmet .inp files
    set_calmet(dom, date,day)
    print(f"Processing day {date}:")
    print("Running CALWRF ...")
    output = subprocess.run(['calwrf',f'{inpdir}/{date}.inp'], capture_output=True, text=True)
    if (output.returncode != 0):
        print(f"{date}: CALWRF error {output.stdout}\n ...exiting execution\n")
        sys.exit(1)
    print("Running CALMET ...")
    output = subprocess.run(['calmet_ifort',f'{cinpdir}/{date}.inp'], capture_output=True, text=True)
    if (output.returncode != 0):
        print(f"{date}: CALMET error {output.stdout}\n ...exiting execution\n")
        sys.exit(1)
    
if month == 12:    
    remove_trash()      
 
 
 
