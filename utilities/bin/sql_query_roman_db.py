#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 13:46:01 2025

- vypocet priemernej dennej teploty na klimatologickych staniciach, ktore pouzivame pre CALPUFF domeny
- data tahame z Romanovej databazy 
- teplota sa zaznamenava kazdu minutu v UTC time, treba spravit konverziu na CET
2026-01-20:
    Zmena vstupnej tabulky domena-metID (namiesto dictionary .xls subor)
    Zmena vstupnych dat meteo z .csv na .xls (ukazalo sa, ze surove data z databazy treba niekedy aj trochu zeditovat)
"""

import sys
sys.path.append('/users/p6065/python-scripts')
from dbConnector import obs 
import pandas as pd
import datetime



        
#vyber casoveho intervalu - v UTC!
#v zime je  CET=UTC+1:00:00
year = 2024
date_begin=f'{year}-01-01 00:00:00'
date_end=f'{year}-12-31 23:00:00'

metid1 = pd.read_excel("/data/oko/krajc/dbase_calpuff/met.data/meteo4domains_2021_2024.xlsx", sheet_name=f'meteo_2021')
metid2 = pd.read_excel("/data/oko/krajc/dbase_calpuff/met.data/meteo4domains_2021_2024.xlsx", sheet_name=f'meteo_2024')


metlist = list(set(list(metid1['metid'])+list(metid2['metid'])))


# #priemerna hodinova teplota v UTC pre konkretnu stanicu
# sqr = obs.query("select avg(ta_2m),HOUR(date),DATE(date) from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
#                                 where date between '2025-04-09 00:00:00'  and '2025-04-11 00:00:00' and ii=11810 group by HOUR(date),DATE(date) \
#                                     order by  DATE(date), HOUR(date)")

                         
                                
# #KONVERZIA NA CET - kontrola prechodu na letny a zimny cas - je to OK
# #priemerna hodinova teplota (v CET)
# obs.query("select avg(ta_2m),HOUR(CONVERT_TZ(date, 'UTC', 'CET')) as hour, DATE(CONVERT_TZ(date, 'UTC', 'CET')) as datum from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
#                                 where date between '2025-03-30 00:00:00'  and '2025-03-31 00:00:00' and ii=11810 group by hour,datum \
#                                     order by  datum, hour")



# #priemerna denna teplota (v CET)  
# obs.query(f"select avg(ta_2m), DATE(CONVERT_TZ(date, 'UTC', 'CET')) as datum from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
#                                 where date between '{str(date_begin)}'  and '{str(date_end)}' and ii=11810 group by datum \
#                                     order by  datum")     
                                    

k=1
dfhourly = pd.DataFrame(index=pd.date_range(start=date_begin, end=date_end,freq='1H'))
dfdaily = pd.DataFrame(index=pd.date_range(start=date_begin, end=date_end,freq='1D'))
for value in metlist:

    df=obs.query(f"select avg(ta_2m), DATE(CONVERT_TZ(date, 'UTC', 'CET')) as datum from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
                                    where date between '{str(date_begin)}'  and '{str(date_end)}' and ii='{value}' group by datum \
                                        order by  datum") 
    df.index = pd.to_datetime(df.datum)
    del df['datum']
    df.columns = [value] 
    if k==1:
      df_final=pd.merge(dfdaily,df,left_index=True,right_index=True, how='left')
    else:
      df_final=pd.merge(df_final,df,left_index=True,right_index=True, how='left')      
    k=k+1    

#zaokruhlenie na dve desatinne miesta a export do csv suboru
df_final.round(2).to_csv(f'/data/oko/krajc/dbase_calpuff/met.data/stations_daily_temp_{year}.dat',sep='|') 

'''


sqr = obs.query("select avg(ta_2m),HOUR(date),DATE(date) from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
                                where date between '2024-04-01 00:00:00'  and '2024-04-16 00:00:00' and ii=11819 group by HOUR(date),DATE(date) \
                                     order by  DATE(date), HOUR(date)")
                      
sqr=obs.query("select avg(ta_2m),HOUR(CONVERT_TZ(date, 'UTC', 'CET')) as hour, DATE(CONVERT_TZ(date, 'UTC', 'CET')) as datum from obs.obs_sxsq39_1m as obs join si.si on si.id = obs.si_id \
                                where date between '2024-04-01 00:00:00'  and '2024-04-16 00:00:00' and ii=11819 group by hour,datum \
                                     order by  datum, hour")

#tabulka s nameranymi hodinovymi priemermi
obs.query("desc obs.obs_nmsko_1h")

#namerane hodinove priemerne koncentracie PM10 a PM2,5 na stanici Jeseniova, konverzia z UTC na CET
df=obs.query(f"select PM10, PM2_5,ta_2m, HOUR(CONVERT_TZ(date, 'UTC', 'CET')) as datum  from obs.obs_nmsko_1h o join si.si on si.id=o.si_id where ii=11813 and \
             date between '{str(date_begin)}'  and '{str(date_end)}' ")
                                    
df=obs.query(f"select PM10, PM2_5,ta_2m, CONVERT_TZ(date, 'UTC', 'CET') as datum  from obs.obs_nmsko_1h o join si.si on si.id=o.si_id where ii=11813 and \
                          date between '{str(date_begin)}'  and '{str(date_end)}' ")
                          