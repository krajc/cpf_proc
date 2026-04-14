#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 11:59:03 2025
Povodna verzia skriptu 0_domains_for_CALPUFF.py neobsahovala v Domain_conf.yml
parameter ztop. Skript prida tento parameter do uz existujucich Domain_conf suborov
@author: p2993
"""
import os
import yaml

geodir = "/data/oko/krajc/dbase_calpuff/geodat/LCCcpf"
ztop = 3000
#zface = '0,20,40,100,200,400,700,1100,1600,2000,3000'

for file in os.listdir(geodir):
    if file != 'old':
        with open(f'{geodir}/{file}/Domain_conf.yml') as f:
            cfg = yaml.full_load(f)
        cfg['ztop'] = ztop
        with open(f'{geodir}/{file}/Domain_conf.yml', 'w') as f:
            yaml.dump(cfg, f)
