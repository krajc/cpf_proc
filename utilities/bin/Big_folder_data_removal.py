#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 16 12:42:49 2025
Removes files in very large directories
@author: p2993
"""

import os
import shutil


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

#### Mazanie volemarb dat (z /data/oko/ disku. Novsie by mali byt vo worku)
folder = "/data/oko/krajc/dbase_calpuff/source_arb"
for dom in metid.keys():
    for houses in ['fh', 'nfh']:
        if os.path.exists(f'{folder}/{dom}/{houses}'):
            print (f"Removing files in {dom}/{houses}... \n")
            
            for fil in os.listdir(f'{folder}/{dom}/{houses}'):
                os.remove(f'{folder}/{dom}/{houses}/{fil}')
                
        else:
            print (f"Folder {dom}/{houses} doesn't exist \n")
    
### Mazanie ASCII dat z PRTMET 
dom = 'banskabystrica'
folder = f'/work/users/p2993/prtmet/{dom}'
if os.path.exists(f'{folder}'):
    
    if os.path.exists(f'{folder}/asc'):
        shutil.rmtree(f'{folder}/asc')    
    
    
    
            
