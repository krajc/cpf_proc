#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 11:43:49 2022
Priprava calpuff.inp suborov pre jednotlive group/ggroup.

@author: p2993
"""

import os
import yaml
import rasterio

def get_calpuff_elev(x,y):
    with rasterio.open("/data/users/ext33340/calpuff/sources/dem_sk_250.tif") as rds:
         value = list(rds.sample([(x*1000, y*1000)]))[0]
    return(round(float(value),1))

# Switch ci je treba vytvarat calpost.inp subor. Ak ano - 1. 
year = 2021
dom = "ruzomberok"
group = "heat"
ggroups = ('fh','nfh')
ggroup = 'nfh'

species = ('SO2','NOx','PM10','PM25','BaP')

configfile = f'/users/p2993/dbase_calpuff/geodat/LCCcpf/{dom}/Domain_conf.yml'
with open(configfile) as file:
    cfg = yaml.full_load(file)
    
metdir = f'/data/users/p2993/data_cpf/calmet/{dom}'
metfiles = sorted(os.listdir(metdir))
# Create met string:
metdatstring = ""
for m in metfiles:
    metdatstring = metdatstring + f'!  METDAT= {metdir}/{m} !   !END!\n'

cpfdir = '/users/p2993/cpf_proc/calpuff'
temp = f'{cpfdir}/templates/calpuff7_{group}.inp.templ'
with open(temp) as f_obj:
    templ = f_obj.readlines()
templ = "".join(templ)

sourcedir = '/data/oko/krajc/dbase_calpuff/source_arb'
volemdir = f'{sourcedir}/{dom}/{ggroup}'
files = sorted(os.listdir(f'{volemdir}'))

scratchdir = "/scratch"
wrkdir = f'{scratchdir}/p2993'
tmpdir = f'{scratchdir}/p2993/tmp'
cpfdir = f'/users/p2993/calpuff/{dom}/{group}/{ggroup}'
outdir = f'/data/users/p2993/data_cpf/calpuff/{dom}/{group}/{ggroup}'
lstdir = f'/work/users/p2993/calpuff/{dom}/{group}/{ggroup}/lst'
# Ak nexistuju, vytvorit
for dir in (cpfdir, outdir, lstdir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# Ak existuju uz predchadzajuce .inp subory, vymazat
if os.path.exists(cpfdir):
    for fil in os.listdir(cpfdir):
        os.remove(f'{cpfdir}/{fil}')

recfile = f"/data/oko/krajc_atmosys/calpuff/{dom}/drec_file.dat"
with open (recfile) as f:
    recs = f.readlines()

recfile2 = f"/users/p2993/dbase_calpuff/geodat/LCCcpf/{dom}/station_rec.yml"
with open(recfile2) as file:
    rec2 = yaml.full_load(file)
 
for i in rec2:
    X, Y = i['x'], i['y']
    elev = get_calpuff_elev(X , Y)
    recs.append(f"{len(recs)} ! grp1 = {X}, {Y}, {elev}, 2.0    !   !END!\n ")
 
nrec = len(recs)
recstring = "".join(recs)

ngrp =  2
grpstring = ' ! RGRPNAM = grp0         !   !END!\n ! RGRPNAM = grp1         !   !END! '
    
text = templ

ibmo, iemo = 1, 12
ibdy, iedy = 1, 31
ibhr, iehr = 0, 23

nx, ny = cfg['nx'], cfg['ny']
dgridkm = cfg['dgridkm']
xorigkm, yorigkm = cfg['xorigkm'], cfg['yorigkm']

text = text.replace('__metrunswitch__', str(1)) # 1=all periods in metfile

text = text.replace('__startyear__', str(year))
text = text.replace('__endyear__', str(year))
text = text.replace('__startmonth__', str(ibmo))            
text = text.replace('__endmonth__', str(iemo))
text = text.replace('__startday__', str(ibdy))            
text = text.replace('__endday__', str(iedy))
text = text.replace('__starthour__', str(ibhr))            
text = text.replace('__endhour__', str(iehr))

text = text.replace('__mnx__', str(nx))    
text = text.replace('__mny__', str(ny))                
text = text.replace('__reskm__', str(dgridkm))                    
text = text.replace('__mxorig__', str(xorigkm))
text = text.replace('__myorig__', str(yorigkm))

text = text.replace('__nmetdat__', str(365))
text = text.replace('__metdatstring__', metdatstring)
text = text.replace('__nvoldat__', str(1))      # pocet suborov volemarb.dat
text = text.replace('__myorig__', str(yorigkm))

text = text.replace('__llx__', str(1))
text = text.replace('__lly__', str(1))
text = text.replace('__urx__', str(cfg['nx']))
text = text.replace('__ury__', str(cfg['ny']))

text = text.replace('__iwet__', str(0))         # wet deposition output = 1
text = text.replace('__mwet__', str(0))         # wet deposition = 1

text = text.replace('__nvl2__', str(1))         # pocet zdrojov vo volemarb.dat
text = text.replace('__ngrp__', str(ngrp))   # pocet recepor groups
text = text.replace('__grpstring__', grpstring)
text = text.replace('__nrec__', str(nrec))
text = text.replace('__recstring__', recstring)

for file in files:
    body = file[8:-4]
     
    textv = text
    textv = textv.replace('__lstfile__', f'{lstdir}/calpuff{body}.lst')
    textv = textv.replace('__concfile__', f'{outdir}/conc{body}.dat')
    textv = textv.replace('__voldat__', f'{volemdir}/{file}')
    textv = textv.replace('__nvl2string__', f'{ggroup.upper()}{file[13:-4]}.dat')

    with open(f"{cpfdir}/calpuff{body}.inp", 'w') as f:
        f.write(textv)

        
