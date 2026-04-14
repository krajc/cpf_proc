#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
6-2025: Pridany parameter __TERRAD__ nastavitelny pre kazdu domenu zvlast
4-2025:
Ukazalo sa, ze v ojedinelych pripadoch CALMET padne na chybajucich datach nad 3000 m
(co bola povodne zadefinovana max. vertikalna hladina). Vtedy treba znizit vysku poslednej
hladiny. Modifikacie:
    zaviedla som parameter ztop udavajuci vysku poslednej hladiny
    do .templ suboru bol pridany parameter __ZFACE__ 
    pri zmene ztop automaticky zmodifikuje vysky hladin v Domain_conf.yml (kvoli CALPUFF procesingu)
    Ukazalo sa, ze znizenie ztop problem neodstranilo, musela smo zmenit ZIMAX v .inp subore
    (max vyska mixh nad zem. povrchom) z 3000 na 2800
3-2025:
Dorobeny modul na extrakciu tar.gz suborov .m3d
2-2025:
Skript spusta CALMET po novom s m3d datami z 2km Aladinu bez potreby CALWRF. 

Po dokonceni si posebe vycisti "medziprodukty" - m3d, m2d a calwrf.lst v /scatch

Dec 7, 2022:
Pokial najde rerunfile pre danu domenu, spusti iba terminy v rerunfile. Inak spusti
vsetkych 365 dni.

@author: p2993
"""

import os
import sys
import tarfile
import subprocess
import yaml
import xarray as xr
import numpy as np
import geopandas as gpd
import pandas as pd
from multiprocessing import Pool, cpu_count
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
parser.add_argument('disk', type=str)
parser.add_argument('year', type=int)
parser.add_argument('ztop', type=int)
parser.add_argument('terrad', type=float)
parser.add_argument('ikine', type=int)
args = parser.parse_args()

year = args.year
dom = args.domena
disk = args.disk
ztop = args.ztop
terrad = args.terrad
ikine = args.ikine

if terrad == 999:
    calmettempl = "/users/p2993/cpf_proc/calmet/bin/templates/calmetWRF.templ"
elif ikine == 999:
    calmettempl = "/users/p2993/cpf_proc/calmet/bin/templates/calmet2024_terrad.templ"
else:
    calmettempl = "/users/p2993/cpf_proc/calmet/bin/templates/calmet2024_terrad_ikine.templ"


#dom = 'ruzomberok'
print(f'running domain: {dom}\n')

start_time = time.perf_counter()

# read calmet.inp template:
with open(calmettempl) as f_obj:
    cmtempl = f_obj.readlines()
cmtempl = "".join(cmtempl)

###############################################################

def getclosest_ij(lats,lons,latpt,lonpt):
    # find squared distance of every point on grid
    dist_sq = (lats-latpt)**2 + (lons-lonpt)**2
    # 1D index of minimum dist_sq element
    minindex_flattened = dist_sq.argmin()
    # Get 2D index for latvals and lonvals arrays from 1D index
    return np.unravel_index(minindex_flattened, lats.shape)


# Prepare calmet config file
def set_calmet(dom, date, ztop):
    (y, m, d) = date.split(sep="-")  
    m3ddat = f'{m3dtmp}/sr-{y}{m}{d}_24h.m3d'
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
    zface = f'0,20,40,100,200,400,700,1100,1600,2000,{ztop}'
    
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
    text = text.replace('__ZFACE__', zface)
    text = text.replace('__TERRAD__', str(terrad))
    text = text.replace('__IKINE__', str(ikine))
    
    with open(cconfile, 'w') as f:
        f.write(text)

def extract_m3d(date, y, m, d):
    print(f"Unzipping file{m3ddir}/sr-{y}{m}{d}_24h.tar.gz ...\n")
    badpth = 'data/oko/meteo/csv'
    os.chdir(f'{m3ddir}')
    tar = tarfile.open(f"{m3ddir}/sr-{y}{m}{d}_24h.tar.gz")
    tar.extractall()
    tar.close()
    if os.path.exists(f'{m3ddir}/{badpth}/{year}/sr-{y}{m}{d}_24h.m3d'):
        os.rename(f'{m3ddir}/{badpth}/{year}/sr-{y}{m}{d}_24h.m3d', f'{m3dtmp}/sr-{y}{m}{d}_24h.m3d')
    else:
        os.rename(f'{m3ddir}/sr-{y}{m}{d}_24h.m3d', f'{m3dtmp}/sr-{y}{m}{d}_24h.m3d')

# Run calmet                           
def run_calmet(date):
    (y, m, d) = date.split(sep="-") 
    extract_m3d(date, y, m, d)
    m3ddat = f'{m3ddir}/tmp/sr-{y}{m}{d}_24h.m3d'
    if os.path.exists(m3ddat):
        
        
        print(f"Running CALMET {date}...\n")        
        # Prepare calmet .inp files
        set_calmet(dom, date, ztop)
        output = subprocess.run(['calmet_ifort',f'{cinpdir}/{date}.inp'], capture_output=True, text=True)
        if (output.returncode != 0):
            print(f"{date}: CALMET error {output.stderr}\n ...exiting execution\n")
            sys.exit(1)
                    
    else:
        print(f"Error: {m3ddat} is missing!! \n")
    
    clean_scratch(dom, date)
    if os.path.exists(f'{outdir}/{dom}/{date}.dat'):
        if os.path.exists(m3ddat):
            os.remove(m3ddat)
            
def final_cleanup():
    if os.path.exists(f'{scratchdir}/p2993'):
        os.removedirs(f'{scratchdir}/p2993/tmp')
        #os.removedirs(f'{scratchdir}/p2993')

def clean_scratch(dom, date):
    
    if os.path.exists(f'{outdir}/{dom}/{date}.aux'):
        os.remove(f'{outdir}/{dom}/{date}.aux')
    
##########################################################################################

#scratchdir = "/scratch"
#$wrkdir = f'{scratchdir}/p2993'
#tmpdir = f'{scratchdir}/p2993/tmp'
tmpdir = '/work/users/p2993/tmp'
#wrkdir = f'/work/users/p2993/calwrf/{dom}'
#calwrfdir = '/users/p2993/cpf_proc/calwrf'
calmetdir = '/users/p2993/cpf_proc/calmet'
cwrkdir = '/work/users/p2993/calmet'
outdir = f'{disk}/data_cpf/calmet/{year}'
rerunfile = f'{calmetdir}/rerun{year}_{dom}.inp'
domdir = "/users/p2993/cpf_domeny"

cinpdir = f"{calmetdir}/{dom}"
# Data aladin cela SR vo formate 3D.dat (.m3d zatarovane gzip)
m3ddir =   f'/data/oko/meteo/csv/{year}'
# m3dtmp for extraction of m3d files:
m3dtmp = f'{m3ddir}/tmp'
geodat = f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}'
confile = f'{geodat}/Domain_conf.yml' 
# Load Domain_conf config file
with open(confile) as file:
    cfg = yaml.full_load(file)
# V pripade, ze treba zmenit hornu hladinu modelu, tu sa prepise, a zaroven
# sa prepise aj v existujucom subore Domain_conf.yml pre dalsie pouzitie
if ztop != 3000:
    cfg['ztop'] = ztop
    with open(confile, 'w') as f:
        yaml.dump(cfg, f)
 
if not os.path.exists(f'{cwrkdir}/{dom}/lst'):
     os.makedirs(f'{cwrkdir}/{dom}/lst')  
if not os.path.exists(f"{outdir}/{dom}"):
     os.makedirs(f"{outdir}/{dom}")    
if not os.path.exists(cinpdir):
     os.makedirs(cinpdir)

if not os.path.exists(tmpdir):
    os.makedirs(tmpdir)   
if not os.path.exists(m3dtmp):
    os.makedirs(m3dtmp)

if os.path.exists(rerunfile):
    with open(rerunfile) as f_obj:
        dates = f_obj.readlines()
        dates = list(map(lambda x: x[:-1], dates))
else:
    idx = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31',freq='1D')
    #idx = pd.date_range(start=f'{year}-01-01', end=f'{year}-01-03',freq='1D')
    dates = list(map(lambda x:str(x)[:10], idx ))
#dates = dates[:40]

# Multiprocessing:
# setup local TMPDIR:
os.environ['TMPDIR'] = tmpdir
#number_of_cores = cpu_count() 
number_of_cores = int(os.environ['SLURM_CPUS_PER_TASK'])   
#number_of_cores = int(os.environ['SLURM_NTASKS'])   
print(f'Number of cores: {number_of_cores}\n')

with Pool(number_of_cores) as pool:
    pool.map(run_calmet, dates)

finish_time = time.perf_counter()
cputime = (finish_time-start_time)/3600
print(f"Program finished in {cputime: .1f} hours\n")
# Removing scratchdir:
#final_cleanup()
