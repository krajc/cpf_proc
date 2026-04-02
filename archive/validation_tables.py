#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKRIPT spracuva .xlsx subory s validacnymi parametrami pre jednotlive domeny a produkuje prehladnu tabulku
(kvoli prezentacii vysledkov)
"""
import sys
sys.path.append('/users/p2993/python/libs')
import plot_conc_BA
import utils_v1
import pandas as pd
import geopandas as gpd
import yaml


unit = plot_conc_BA.unit_string
opis = plot_conc_BA.opis
# Dictionary s civilnymi nazvami domen:
domname = plot_conc_BA.domname
codes = utils_v1.codes
rmse = utils_v1.rmse
bias = utils_v1.bias
trim = utils_v1.trimming


year = 2021
spcs = ['PM10','PM25','NO2','BaP']
domfile = '/users/p2993/cpf_domeny/all_doms_LCCcpf_processed/all_doms_LCCcpf_processed.shp'
#stationfile = '/users/p2993/dbase_calpuff/ams.data/ams2022.xlsx'
doms = gpd.read_file(domfile, encoding='utf-8')
#stations = pd.read_excel(stationfile)
noAMS = ['Myjava','Brezno','Kysuce','Orava','Javorniky', 'Pohronie', 'Povazie', 'Spis', 'JSKotlina']
#valdir = "/data/oko/krajc/SA"
valdir = "/data/oko/jana/SA"
#############################################################################    
# Zapis dennych a rocnych SA do excelu
writer = pd.ExcelWriter('/data/oko/krajc/SA/Summary_table_new.xlsx')

for spc in spcs: 

    # Vysledna tabulka pre 1 znecistujucu latku:
    tab = pd.DataFrame(columns=['City','Street','AMScode','backg','heat','road','neis',
                                'model','measured','r','bias','rmse'])
    
    for dom in list(doms['domname']): 
        
        print(f"{dom}") 
        
        if dom not in noAMS:
            
            f = pd.ExcelFile(f'{valdir}/SA_{dom.lower()}.xlsx')
            sheets = f.sheet_names
            with open(f'/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/{dom.lower()}/station_rec.yml') as file:
                recdict = yaml.full_load(file)
            
            rec = pd.DataFrame.from_dict(recdict)
                        
            for i in rec.index:
                if f'annual_{spc}_{rec["EolStationCode"][i]}' in sheets:
                    
                    val = pd.read_excel(f'{valdir}/SA_{dom.lower()}.xlsx',sheet_name=f'annual_{spc}_{rec["EolStationCode"][i]}')
                    val.columns = ['par','value']
                    # V sheete PM10 je navyse riadok s limitnou hodnotou, treba vymazat:
                    if spc == 'PM10':
                        val = val.drop([6], axis=0)
                        val.index = list(range(9))
                    tab = tab.append({'AMScode':rec["EolStationCode"][i],
                                      'City':rec['City'][i],
                                      'Street':rec['Street'][i],
                                      'backg':val['value'][0],
                                      'heat': val['value'][1],
                                      'road': val['value'][2],
                                      'neis': val['value'][3],
                                      'model': val['value'][4],
                                      'measured': val['value'][5],
                                      'r': val['value'][6],
                                      'bias': val['value'][8],
                                      'rmse': val['value'][7]}, ignore_index=True)
            
    tab.to_excel(writer, sheet_name=f'{spc}')        
               
        
writer.save()
    
    
    
    