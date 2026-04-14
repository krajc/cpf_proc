#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 09:13:25 2025

@author: p2993
"""

import pandas as pd
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from metpy.calc import wind_direction, wind_speed
from metpy.units import units


year = 2024
dom = 'banskabystrica'
pth = f'/data/oko/krajc/data_cpf/prtmet/{year}/{dom}'

s1 = pd.read_csv(f"{pth}/validate-set0-11898.csv")
s2 = pd.read_csv(f"{pth}/validate-set1-11898.csv")

'''
u = units.Quantity( wind_zon, 'm/s')
v = units.Quantity( wind_mer, 'm/s')

wd = wind_direction( u, v, convention='from')
ws = wind_speed( u, v)

# output data
print('Making output data')
out = pd.DataFrame()
out['date'] = pd.date_range(f'{year}-01-01 00:00',f'{year}-12-31 23:00',freq='1h')
out['ws'] = ws.magnitude
out['wd'] = wd.magnitude
out['t2'] = tempr2
out.to_csv(final_directory+'/data.csv')
'''


speeds = (0, 0.5, 1, 2,3,4,5,6,7)
colormap = "viridis_r"
    
i = 1
for t in (s1, s2):
    
    # Priemerna rychlost vetra a bezvetrie:
    v_mean_m = (t.wspeed.mean()).round(1)
    calm_m = t.wspeed <= 0.2
    calmPerc_m = (calm_m.sum()*100/t.shape[0]).round(1)
    Nazov_m = f"Model S{i} \nPriemerná ročná rýchlosť vetra: {str(v_mean_m)} m/s, bezvetrie: {calmPerc_m}%"
    
        
    ax = WindroseAxes.from_ax()
    ax.bar(t.wdirc, t.wspeed, bins=speeds, normed=True)
    ax.set_legend(title="Rýchlosť vetra (m/s)")
    ax.set_title(Nazov_m)
    i = i+1
    
v_mean_o = (t.ff.mean()).round(1)
calm_o = t.ff <= 0.2
calmPerc_o = (calm_o.sum()*100/t.shape[0]).round(1)

Nazov_o = f"Merania \nPriemerná ročná rýchlosť vetra: {str(v_mean_o)} m/s, bezvetrie: {calmPerc_o}%"
ax = WindroseAxes.from_ax()
ax.bar(t.dd, t.ff, bins=speeds, normed=True)
ax.set_legend(title="Rýchlosť vetra (m/s)")
ax.set_title(Nazov_o)