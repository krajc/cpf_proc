#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dec 12, 2022:
    Multiproc verzia submitovania CALPUFF runov

@author: p2993
"""

import os
import sys
import yaml
import rasterio
import subprocess
from multiprocessing import Pool, cpu_count
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
parser.add_argument('group', type=str)
parser.add_argument('ggroup', type=str)
parser.add_argument('batchsize', type=int)
parser.add_argument('batchnumber', type=int)
parser.add_argument('disk', type=str)
parser.add_argument('epi1', type=str)
parser.add_argument('epi2', type=str)

args = parser.parse_args()

def get_calpuff_elev(x,y):
    with rasterio.open("/data/users/p6278/calpuff/sources/dem_sk_250.tif") as rds:
         value = list(rds.sample([(x*1000, y*1000)]))[0]
    return(round(float(value),1))

def replace_common(template):

    text = template
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
    
    text = text.replace('__nmetdat__', str(nmetfiles))
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
    return(text)

def run_calpuff(file):
    body = file[9:-4]
    textv = commontext
    textv = textv.replace('__lstfile__', f'{lstdir}/{body}.lst')
    textv = textv.replace('__concfile__', f'{outdir}/conc-{body}.dat')
    textv = textv.replace('__voldat__', f'{volemdir}/{file}')
    
    # Ak existuje uz predchadzajuci .inp subor, najprv vymazat
    if os.path.exists(f"cpfdir/{body}.inp"):
        os.remove(f'{cpfdir}/{body}.inp')
    # Zapiseme novy subor:
    with open(f"{cpfdir}/{body}.inp", 'w') as f:
        f.write(textv)
    
    print(f"Running CALPUFF {body}...\n")        
    output = subprocess.run(['calpuff',f"{cpfdir}/{body}.inp"], capture_output=True, text=True)
    if (output.returncode != 0):
        print(f"{body}: CALPUFF error {output.stderr}\n ...exiting execution\n")
        sys.exit(1)
    
    #clean_scratch(dom, date)
    
def final_cleanup():
    if os.path.exists(f'{scratchdir}/p2993'):
        os.removedirs(f'{scratchdir}/p2993/tmp')
        #os.removedirs(f'{scratchdir}/p2993')

# nasekanie files na 40 CPU useky:
def distribution_list(origlist, batchsize):
    # looping till length of origlist
    for i in range(0, len(origlist), batchsize):
        yield origlist[i:i + batchsize]
        
start_time = time.perf_counter()

year = 2023
#dom = "ruzomberok"
#disk = "/data/oko/krajc"      # alebo:
disk = args.disk
group, ggroup = 'heat', 'nfh'
dom = args.domena
group = args.group
ggroup = args.ggroup
epi1 = args.epi1
epi2 = args.epi2
#ggroups = ('fh','nfh')

species = ('SO2','NOx','PM10','PM25','BaP')

configfile = f'/users/p2993/dbase_calpuff/geodat/LCCcpf/{dom}/Domain_conf.yml'
with open(configfile) as file:
    cfg = yaml.full_load(file)
    
metdir = f'{disk}/data_cpf/calmet/{year}/{dom}'
#metdir = f'/data/users/p2993/data_cpf/calmet/{dom}'
metfiles = sorted(os.listdir(metdir))
nmetfiles = len(metfiles)
# Create met string:
metdatstring = ""
for m in metfiles:
    metdatstring = metdatstring + f'!  METDAT= {metdir}/{m} !   !END!\n'

cpfdir = '/users/p2993/cpf_proc/calpuff'
temp = f'{cpfdir}/bin/templates/calpuff7_{group}.inp.templ'
with open(temp) as f_obj:
    templ = f_obj.readlines()
templ = "".join(templ)

sourcedir = '/data/oko/krajc/dbase_calpuff/source_arb'
volemdir = f'{sourcedir}/{dom}/{year}/{ggroup}'
files = sorted(os.listdir(f'{volemdir}'))

scratchdir = "/scratch"
wrkdir = f'{scratchdir}/p2993'
tmpdir = f'{scratchdir}/p2993/tmp'
#tmpdir = '/work/users/p2993/tmp'
cpfdir = f'/users/p2993/cpf_proc/calpuff/{dom}/{group}/{ggroup}'
outdir = f'{disk}/data_cpf/calpuff/{year}/{dom}/{group}/{ggroup}'
lstdir = f'/work/users/p2993/calpuff/{dom}/lst/{group}/{ggroup}'

# Ak nexistuju, vytvorit
for dir in (cpfdir, outdir, lstdir, tmpdir):
    if not os.path.exists(dir):
        os.makedirs(dir)



recfile = f"/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}/drec_file.dat"
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

yr1, mo1, dy1 = epi1.split("-")
yr2, mo2, dy2 = epi2.split("-")
ibmo, iemo = mo1, mo2
ibdy, iedy = dy1, dy2
ibhr, iehr = 0, 23

nx, ny = cfg['nx'], cfg['ny']
dgridkm = cfg['dgridkm']
xorigkm, yorigkm = cfg['xorigkm'], cfg['yorigkm']

commontext = replace_common(templ)

# Multiprocessing:
batchlists = list(distribution_list(files, args.batchsize))
# setup local TMPDIR (kedze pool mozat iba na jednom node, staci tmpdir nasetovat tu):
os.environ['TMPDIR'] = tmpdir
#number_of_cores = cpu_count() 
number_of_cores = int(os.environ['SLURM_CPUS_PER_TASK'])   
#number_of_cores = int(os.environ['SLURM_NTASKS'])   
print(f'Number of cores: {number_of_cores}\n')
print(f'Batch number {args.batchnumber}\n')

with Pool(number_of_cores) as pool:
    pool.map(run_calpuff, batchlists[args.batchnumber])

finish_time = time.perf_counter()
cputime = (finish_time-start_time)/3600
print(f"Program finished in {cputime: .2f} hours\n")
# Removing scratchdir:
final_cleanup()
'''
# Creating link to the other  output disk, if necessary:
if disk != "/data/users/p2993" and not os.path.exists(f'/data/users/p2993/data_cpf/calpuff/{year}/{dom}'):
    os.symlink(f'{disk}/data_cpf/calpuff/{year}/{dom}', f'/data/users/p2993/data_cpf/calpuff/{year}/{dom}')
'''

         

        
