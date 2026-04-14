#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 16 14:21:45 2025
Skript nacita vysky budov z REM2 a urobi priemery (ucel: REM3 vystup)
@author: p2993
"""

import pandas as pd

inpdir = "/data/oko/krajc/New_method/noutputs2021/tmp"

kraje = {'bb':6, 'ba':1, 'tt':2, 'tn':3, 'nr':4, 'za':5, 'pe':7, 'ke':8}
cols = ['fh_mean', 'fh_med', 'fh_max', 'fh_min','nfh_mean', 'nfh_med', 'nfh_max', 'nfh_min' ]
tab = pd.DataFrame(columns = cols, index = list(kraje.keys()))

kraj = 'bb'

for kraj in kraje.keys():
    fh = pd.read_csv(f'{inpdir}/{kraj}-PM10-fh.xyz')
    nfh = pd.read_csv(f'{inpdir}/{kraj}-PM10-nfh.xyz')
    
    tab['fh_mean'][kraj] = fh.HGT.mean().round(1)
    tab['fh_med'][kraj] = fh.HGT.median().round(1)
    tab['fh_max'][kraj]= fh.HGT.max().round(1)
    tab['fh_min'][kraj]= fh.HGT.min().round(1)
    tab['nfh_mean'][kraj] = nfh.HGT.mean().round(1)
    tab['nfh_med'][kraj]= nfh.HGT.median().round(1)
    tab['nfh_max'][kraj]= nfh.HGT.max().round(1)
    tab['nfh_min'][kraj]= nfh.HGT.min().round(1)

summary = tab[['fh_med', 'nfh_med']].mean()

'''
OUTPUTS:

tab
   fh_mean fh_med fh_max fh_min nfh_mean nfh_med nfh_max nfh_min
bb     7.4    7.2   19.6    2.0     16.1    14.0    49.0     2.4
ba     7.2    7.1   22.1    0.4     20.4    17.5    96.2     2.0
tt     7.0    7.0   21.6    2.0     14.5    12.6    50.2     2.0
tn     7.5    7.5   30.0    2.0     16.6    14.4    49.0     4.7
nr     7.1    7.0   21.5    2.0     15.6    13.0    48.0     4.0
za     7.4    7.5  100.0    2.0     16.7    14.5    78.0     3.0
pe     7.8    7.8   67.4    2.0     16.4    14.1    47.0     2.5
ke     7.2    7.1   36.0    2.0     18.0    14.9    45.0     3.0

summary
fh_med      7.275
nfh_med    14.375