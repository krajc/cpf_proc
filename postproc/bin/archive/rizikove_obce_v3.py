#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:36:00 2023
Skript rozsiri dusanov zoznam rizikovych obci V2 o obce z modelu na verziu V3
podla najnovsej metodiky
12.11.2023: Uprava na nove subory s pozadim vybranym manualne

@author: p2993
"""
import xarray as xr
import pandas as pd
import geopandas as gpd
import rioxarray

doms = ['martin', 'ruzomberok','zilina','kysuce','orava','povazie','nitra',
        'kosice', 'krompachy','hnusta','jelsava','pohronie','brezno',
        'juznyhont','jskotlina', 'zarnovicanb','zvolen', 'banskabystrica',
        'presov','spis','prievidza','myjava','trencin','javorniky','bratislava']

# Mesta pri ktorych je bod pozadia vybrany manualne: 
manbackg = ['banskabystrica','hnusta','zarnovicanb','martin','prievidza', 'bratislava',
            'kosice', 'krompachy','nitra','juznyhont']
        
spcs = ['PM10','PM25','NO2','BaP']
filt = {
    'BaP':1,
    'NO2':40,
    'PM10':40,
    'PM25':20
    }

#inpdir = "/data/users/p2993/data_cpf/netcdf_groups"
inpdir = "/data/oko/jana/data_cpf/netcdf_groups"

#Rizikove obce:
ro = pd.read_excel("/data/oko/krajc/ORKO/rizikove_obce_2022_v2.xlsx",
                    index_col='obec_id')
ro = ro.replace("#pocet domov 2021 > 2011", 1)
ro.drop(columns = ['obyv_spolu','domy kuriace tuhym palivom',
       ' % domov kuriacich tuhym palivom  ku vs.domom', 'emis rank',
       'model1 rank', 'model2 rank'], inplace=True)
roids = list(ro.index)
# Vsetky obce shape:
obce = gpd.read_file("/data/oko/krajc/GIS/admin_hranice/obec_1.shp")
obce.index = obce['IDN4']
obce.drop(columns=['DOW', 'FACC', 'IDN3', 'IDN2', 'VYMERA',
       'NUTS1', 'NUTS1_CODE', 'NUTS2', 'NUTS2_CODE', 'NUTS3', 'NUTS3_CODE',
       'LAU1', 'LAU1_CODE', 'LAU2', 'LAU2_CODE', 'Shape_Leng', 'Shape_Area'],
          inplace=True)

# Zoznam obci

frames = {}

for dom in doms:
    if dom in manbackg:
        suff = '-man'
    else:
        suff = ''
    cd = xr.open_dataset(f"{inpdir}/{dom}-total{suff}.nc")
    c = {}
    # Spojim vsetky prekrocenia do jedneho suboru:
    for spc in spcs:
        c[spc] = cd[spc].where(cd[spc] > filt[spc])
        c[spc] = c[spc].fillna(0.0)
    cj = c[spcs[0]]
    for spc in spcs[1:]:
        cj = cj + c[spc]
    cj = cj.where(cj > 0)
    cj = cj.where(~(cj > 0), 1)
    cj.rio.to_raster(f"/data/oko/krajc/ORKO/{dom}-total.tif")
    cj.name = dom
    df = cj.squeeze().to_dataframe().reset_index()
    geometry = gpd.points_from_xy(df.x, df.y)
    gdf = gpd.GeoDataFrame(df, crs=cj.rio.crs, geometry=geometry)
    gdf = gdf.dropna(axis=0)
    gdf.to_crs(5514, inplace=True)
    
    obce_orko =  gpd.sjoin(gdf, obce, how='inner', predicate='within')
    obce_orko.drop(columns=['spatial_ref','index_right'], inplace=True)
    o = obce_orko.groupby('IDN4')['NM4','NM3', 'NM2'].first()
    frames[dom] = o
    
ooo = pd.concat(list(frames.values()), axis=0)
pd.DataFrame(ooo).to_excel("/data/oko/krajc/ORKO/rizikove_obce_HR_model2.xlsx",sheet_name='obce')

# Uz je zoznam vyrobeny takze staci nacitat:
ooo = pd.read_excel("/data/oko/krajc/ORKO/rizikove_obce_HR_model2.xlsx",sheet_name='obce', 
                    index_col='IDN4')

# Countery:
a, b, c = 0, 0, 0
for ide in ooo.index:
    if ide in roids:
        if ro['rank'][ide] != 3:
            print(f"{ro['obec'][ide]}: Changing rank {ro['rank'][ide]} to 3 \n")
            ro['rank'][ide] = 3
            a = a+1
        else:
            print(f"{ro['obec'][ide]}: 3 is already current rank \n")
            b = b+1
    else:
        print(f"Adding {ooo['NM4'][ide]} with rank 3\n")
        ro.loc[ide] = list(ooo.loc[ide]) + [3] 
        c = c+1
        
print(f"\n\nzmena ranku: {a}\nrovnaky rank: {b}\npridana obec: {c}\n")
[obce['geometry'][ide]]
ro['Hlavny zdroj'] = 'Lokálne kúreniská'

ro.to_excel("/data/oko/krajc/ORKO/rizikove_obce_2022_v3m.xlsx", sheet_name='V3m')

gro = obce.merge(ro, left_index=True, right_index=True, how='right')
gro.to_file("/data/oko/krajc/ORKO/rizikove_oblasti_2022_3stupne_v3m.gpkg",driver='GPKG')