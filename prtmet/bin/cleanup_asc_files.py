#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Po spusteni import_calpet_to_xarray.... a vytvoreni .nc suborov
je potrebne zmazat .asc subory. 

@author: p2993
"""

import os

dom = 'ruzomberok'
workdir = f'/work/users/p2993/prtmet/{dom}'

for file in os.listdir(workdir):
    if os.path.isfile(f'{workdir}/{file}'):
        os.remove(f'{workdir}/{file}')
        
##### TOTO JE STRASNE POMALE


    
 