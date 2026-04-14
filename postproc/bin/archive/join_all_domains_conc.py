#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 07:24:46 2023

Vytvorenie spojenej mapy koncentracii zo vsetkych HR domen

@author: p2993
"""
import xarray as xr
import rioxarray


doms = ['martin', 'ruzomberok','zilina','kysuce','orava','povazie',
'kosice','krompachy',
'banskabystrica','hnusta','jelsava','pohronie','brezno','juznyhont','jskotlina']

for dom in doms:
    cnc = xr.open_dataset(f"/data/users/p2993/data_cpf/netcdf_groups/{dom}-total.nc")
