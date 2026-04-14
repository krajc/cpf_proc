#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025-12-03:
    Priprava scaling table pre KINIT (rozpocitavanie emisii na dni)
    
@author: p2993
"""
import numpy as np
import pandas as pd
import calendar


#sample_inp_volemar = "/users/ext33340/templates/volemarb.dat"

crsLCC = {
  'proj': 'lcc',
 'lat_1': 48.75,
 'lat_2': 49,
 'lat_0': 47.7,
 'lon_0': 19.5,
 'x_0': 200000,
 'y_0': 0,
 'ellps': 'WGS84',
 'units': 'm',
 'no_defs': True
 }


def prepare_scaling_table(t):
    
    #vypocet koeficientov 
    t['diff'] = np.where(t[id_st] > 13, 0, 13-t[id_st])
    #t['diff'] = list(map(lambda x: np.where(x > 13, 0, 13-x),t[id_st] ))
    #priemerna rocna odchylka od 13C
    t_mean = t['diff'].mean()
    t['koef'] = (t['diff'] / (t_mean * t.shape[0])).round(5)
    #t['koef'] = list(map(lambda x: (x / (t_mean * t.shape[0])).round(5), t['diff']))
    return(t)


doms = ('banskabystrica', 'brezno', 'jelsava', 'nitra', 'prievidza', 'pohronie', 'bratislava')
year = 2021
year0 = 2021          # Meteorologicky rok pre model REM3
dom = 'bratislava'
outdir = "/data/oko/kinit/annual_coef"
if calendar.isleap(year):
    ndays = 366
else:
    ndays = 365
    

#id stanice, z ktorej chcem pouzit data
metid = {
'ruzomberok':'11872',    # Ruzomberok
'povazie':'11874',     # Liptovsky Hradok
'zilina':'11865',    # Zilina
'martin':'11893',    # Martin
'orava':'11890',     # Oravske Vesele
'kysuce':'11866',    # Cadca
'krompachy':'11949',   # Spisske Vlachy
'kosice':'11947',    # Moldava nad Bodvou
'spis':'11949',   # Spisske Vlachy
'javorniky':'11841', # Dolny Hricov
'presov':'11963',
'jskotlina':'11927',
'juznyhont':'11880',
'banskabystrica':'11898',
'brezno':'11917',
'pohronie':'11938',
'hnusta':'11941',
'jelsava':'11953',
'zarnovicanb':'11900',
'zvolen':'11900',
'prievidza':'11867',
'trencin':'11803',
'myjava':'11806',
'nitra':'11855',
'trnava':'11819',
'bratislava':'11816',
'poprad':'11924'
}


#subor s dennymi profilmi teplot zo vsetkych stanic
#tfile = "/data/oko/krajc_hpc3/stations_daily_temp.dat"
tfile = f"/data/oko/krajc/dbase_calpuff/met.data/stations_daily_temp_{year}.dat"
tdata = pd.read_csv(tfile,sep='|')
# volemarb vyzaduje julian day
tdata.index = list(range(1,ndays+1))
#del tdata['Unnamed: 0']
for dom in doms:
    id_st = metid[dom]
    # data mozu obsahovat chybajuce dni, treba to osetrit:
    t = tdata[[id_st]]
    nancount = t[id_st].isnull().sum()
    if nancount > 0:
        print (f'Check missing days: {nancount} in total \n')
        exit()
    etab = prepare_scaling_table(t)
    etab.columns = ['Tmean', 'diff', 'coef']
        
    etab.to_csv(f"{outdir}/{dom}-heating_coef_{year}.csv")

'''
import xarray as xr

heat = xr.open_dataset('/data/users/p2993/data_cpf/netcdf_groups/banskabystrica-sa-heat-man.nc')
       
heat = xr.open_dataset('/data/users/p2993/data_cpf/netcdf/banskabystrica/daily-banskabystrica-2021-heat-all.nc')



