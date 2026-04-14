#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 10:04:59 2022

@author: p2993
"""

from multiprocessing import Pool
import time
import math

N = 5000000

def cube(x):
    return math.sqrt(x)


# first way, using multiprocessing
start_time = time.perf_counter()
with Pool() as pool:
    result = pool.map(cube, range(10,N))
finish_time = time.perf_counter()
print("Program finished in {} seconds - using multiprocessing".format(finish_time-start_time))
print("---")
# second way, serial computation
start_time = time.perf_counter()
result = []
for x in range(10,N):
    result.append(cube(x))
finish_time = time.perf_counter()
print("Program finished in {} seconds".format(finish_time-start_time))
