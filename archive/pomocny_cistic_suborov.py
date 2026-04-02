#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 15:41:29 2023

@author: p2993
"""

#doms = ['martin', 'ruzomberok','zilina','kysuce','orava','povazie','krompachy']
#doms = ['krompachy']
doms = ['banskabystrica','hnusta','jelsava','pohronie','brezno','juznyhont','jskotlina']


import os

pics = "/data/users/p2993/data_cpf/pics"
spcs = ['PM10','PM25','NO2','BaP']
year = 2021

for dom in doms:
    for spc in spcs:
        if os.path.exists(f"{pics}/{dom}/scenare/{spc}-{year}-{dom}-abovelim.png"):
            os.remove(f"{pics}/{dom}/scenare/{spc}-{year}-{dom}-abovelim.png")
        if os.path.exists(f"{pics}/{dom}/conc/total-{spc}-{year}-{dom}-0.png"):
            os.rename(f"{pics}/{dom}/conc/total-{spc}-{year}-{dom}-0.png",
                      f"{pics}/{dom}/conc/{spc}-{year}-{dom}-total-0.png")
        if os.path.exists(f"{pics}/{dom}/conc/total-{spc}-{year}-{dom}.png"):
            os.rename(f"{pics}/{dom}/conc/total-{spc}-{year}-{dom}.png",
                      f"{pics}/{dom}/conc/{spc}-{year}-{dom}-total-0.png")
            
                         