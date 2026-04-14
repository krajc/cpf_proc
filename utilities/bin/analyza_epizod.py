#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 14:52:51 2025

@author: p2993
"""

import pandas as pd
import matplotlib.pyplot as plt


amsdata = "/data/oko/krajc/dbase_calpuff/ams.data/ruzomberok-PM10-2024.csv"

dat = pd.read_csv(amsdata)
dat.index = pd.to_datetime(dat['Unnamed: 0'])
del dat['Unnamed: 0']
dat.columns = ['Riadok', 'SCP']

daily = dat.resample('D').mean()
daily[daily.index.month==11].plot()


