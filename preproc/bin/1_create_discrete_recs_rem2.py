#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 30 10:02:32 2022

Update 24-01-2023: Osetrenie domen ktore lezia v dvoch krajoch (Spis, JuznyHont, 
                                                                    Javorniky)
@author: p2993
"""
import geopandas as gpd
import pandas as pd
import rioxarray
import xarray as xr
import os

dom = 'orava'
regs = ['za']
prjname = 'LCCcpf'
res0 = 1000
res1 = 250
gdom = gpd.read_file(f"/data/oko/krajc/cpf_domeny/{dom}_{prjname}/Creg.shp")
lcc = gdom.crs

bb = gdom.bounds

print(f"Running DISCRETE RECEPTORS for domain: {dom} ...\n")

def make_gridpoints (bbox, res):
    sizex = bbox['maxx'][0] - bbox['minx'][0]
    sizey = bbox['maxy'][0] - bbox['miny'][0]
    nx0 = int(sizex/res) if sizex % res == 0 else int(sizex/res) + 1
    ny0 = int(sizey/res) if sizey % res == 0 else int(sizey/res) + 1
    r = pd.DataFrame(columns=['X','Y'])
    #x0, y0 = bbox['minx'][0] + res/2, bbox['miny'][0] + res/2
    x0, y0 = bbox['minx'][0] , bbox['miny'][0] 
    for i in range(nx0 +1):
        x = x0 + res * i 
        if i == nx0:
            if x > int(bb.maxx):
                x = int(bb.maxx)
        for j in range (ny0 + 1):
            y = y0 + res * j
            if j == ny0:
                if y > int(bb.maxy):
                    y = int(bb.maxy)
            r = r.append({'X':x, 'Y':y}, ignore_index=True)
    # df to gdf:
    rdf = gpd.GeoDataFrame(r, geometry=gpd.points_from_xy(r.X, r.Y))
    rdf.crs = lcc
    return rdf

outdir = f"/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom}"
if not os.path.exists (outdir):
    os.makedirs(outdir)
    
# Riedky grid:
r0 = make_gridpoints(bb, res0)
# Husty grid:
r1 = make_gridpoints(bb, res1)

# Vyber z husteho gridu pre obufrovane oblasti s kureniskami

# Vyrobim z polygonov budov 1 objekt ktory obufrujem 500 metrami:
    
if len(regs) > 1:
    r = []
    for houses in ['fh','nfh']:
        for reg in regs:
            r.append(gpd.read_file(f"/data/oko/krajc/cpf_domeny/budovy_byty/2021/{reg}-budovy-{houses}.gpkg"))
    bud = r[0].append(r[1])
    bud = bud.append(r[2])
    bud = bud.append(r[3])
    
else:
    reg = regs[0]
    budovyfh = f"/data/oko/krajc/cpf_domeny/budovy_byty/2021/{reg}-budovy-fh.gpkg"
    budovynfh = f"/data/oko/krajc/cpf_domeny/budovy_byty/2021/{reg}-budovy-nfh.gpkg"
    budfh = gpd.read_file(budovyfh)
    budnfh = gpd.read_file(budovynfh)
    bud = budfh.append(budnfh)
    if dom == 'kosice':
        buduss = gpd.read_file(f"/data/oko/krajc/cpf_domeny/budovy_byty/2021/{reg}-budovy-USS.gpkg")
    
    bud = bud.append(buduss)

bud = bud.to_crs(lcc)
b = gpd.sjoin(bud, gdom, how='inner', predicate='within')
b['dummy'] = 'dummy'
bdis = b.dissolve(by='dummy')
bbuf = bdis.buffer(500)
bbuf = gpd.GeoDataFrame(geometry=bbuf)

# Vyberiem pomocou neho subset z r1
rr = gpd.sjoin(r1, bbuf, how='inner', predicate='within')

# Spojim riedky a husty grid do jednej gdf:
allr = rr.append(r0)
allr.index = list(range(allr.shape[0]))
# Vytvorim ASCII subor s receptormi pre CALPUFF
# Modelovy terern:
terfile = "/data/oko/krajc/dbase_calpuff/geodat/elevationSK_250.tif"
ter = rioxarray.open_rasterio(terfile)
# nasamplujem este elevation:
allr['elev'] = list(map(lambda px,py:float(ter.interp(x=px, y=py, method='nearest')),
                           allr.X, allr.Y))
allr.to_file(f"{outdir}/drec-{dom}.gpkg", driver='GPKG')
outfile = f"{outdir}/drec_file.dat"

outl = []
for i in range(allr.shape[0]):
    xo, yo = round(allr['X'][i]/1000,3), round(allr['Y'][i]/1000,3)
    el = round(allr['elev'][i], 1)
    outl.append(f"{i} ! grp0 = {xo},  {yo}, {el}, 2.0    !   !END!\n")
    
with open (outfile, 'w') as fout:        
    fout.writelines(outl)






    