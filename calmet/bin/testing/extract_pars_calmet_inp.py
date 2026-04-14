#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 08:00:14 2024

@author: p2993
"""
import pandas as pd
import re

inpfile = "/users/p2993/cpf_proc/calmet/poprad/2021-12-31.inp"
outfile = "/users/p2993/barborka/parameters.xlsx"

writer = pd.ExcelWriter(outfile)

with open (inpfile) as f:
    lines = f.readlines()
    
ftext = "".join(lines)

pars = re.findall(r'!.+!',ftext)