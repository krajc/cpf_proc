#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 11:47:11 2021

projekcia -predpokladame  LCC projekciu, pri inej projekcii je potrebne upravit vzorovy subor

@author: ext33340
"""
# citanie z *.cre file
import numpy as np
import os
import re
from pyproj import Proj, transform
import csv
import pandas as pd
import rasterio
from pyproj import Transformer
import yaml

#typ zdroja
source_type='point'
group="seasonal"

domena="jelsava"

# emi_path - cesta k datam pre bodove zdroje z NEIS
'''
data z NEIS by mali mat dohodnuty format
jednotky: tony/rok - v dalsom su prepocitane na jednotky zadefinovane parametreom IPTU =2  [kg/hr]
oddelovac je | 
stlpce,ktore musi subor urcite obsahovat: 'N','x_LCC', 'y_LCC','vyska', 'alt','priemer_mv','rychlost','teplota_mv','so2', 'nox','pm10','pm2.5','bap'
N - poradove cislo zdroja       
'''

emi_path=f"/data/users/ext33340/calpuff/sources/{domena}/jelsava_2021_opr3.txt"
# adresar, kde sa budu ukladat vygenerovane input subory
inp_path=f"/users/p2993/calpuff/{domena}/{source_type}/{group}"
#vzorovy input subor calpuff_point_disc_rec.inp
#sample_inp_calpuff=f"/users/ext33340/templates/calpuff_sample_seasonal.inp"
sample_inp_calpuff=f"/users/p2993/calpuff/templates/calpuff7-point-seasonal-disc.templ"
#textovy subor s doskretnymi receptormi
#format: x_LCC[m], y_LCC[m], elevation[m] - AMS stanica
disc_file1=f"/data/users/ext33340/calpuff/sources/{domena}/jelsava_ams_alt.txt"
#diskretne receptory
disc_file=f"/data/oko/krajc_atmosys/calpuff/jelsava/drec_file.dat"
#adresar, kde sa budu ukladat output subory -  *.LST 
out_path=f"/work/users/p2993/calpuff/{domena}/{source_type}/{group}/lst"
# adresar pre conc vysledne subory
concdir = f"/data/users/p2993/data_cpf/calpuff/{domena}/{source_type}/{group}"
#adresar s konfiguraciou domeny
geodatdir="/users/p2993/dbase_calpuff/geodat/LCCcpf"

#lokalita meteo suborov, v tomto adresari by mali byt len *.met subory
meteo_dir=f"/users/p2993/data/data_cpf/calmet/{domena}/"

# zoznam meteo suborov *.met nacitame do zoznamu
meteo_list=[f for f in os.listdir(f'{meteo_dir}') if f.endswith('.dat')]
#sortovanie nazvov meteo suborov v vzostupnom poradi, sortujem najskor podla mesiaca a potom podla dna
sorted_meteo_list=sorted(meteo_list, key = lambda x:(int(x.split('-')[1]),int(x.split('-')[2].split('.')[0])))
  

# nacitanie zdrojoveho suboru s emisiami do dataframe
fdata = pd.read_csv(emi_path,sep='|')

#kontrola na existenciu roznych typov bodovych zdrojov
fdata['typ'].unique()
fdata.loc[fdata['typ'] == 'seasonal']

'''
subor s konfiguraciou domeny, subor sa vygeneruje v 0_step_teren.py

suradnice x_min, y_min su suradnice laveho dolneho rohu domeny,
suradnice x_max, y_max su suradnice praveho horneho rohu domeny

format suboru:
x_min[m] ymin[m]
x_max[m] y_max[m]
resolution[m]
'''
dom_config=f'/users/ext33340/calmet/geodat/{domena}/{domena}_conf'



# definicie textovych premennych
sourcename='! SRCNAM = P'
meteo='!  METDAT'


#definicia parametrov

#Input Group 1 -  General run control parameters
#definicia starting date pre modelovanie
IBYR=2021
IBMO=1      
IBDY=1      
IBHR=0     
IBMIN=0  
IBSEC=3600      

#definicia ending date pre modelovanie (rovnaky ako ending date pre calmet subory)
IEYR=2021
IEMO=12 
IEDY=31 
IEHR=23  
IEMIN=0 
IESEC=0 

# length of modelling time
NSECDT=3600

# number of modelled chemical species
NSPEC=5
# list of modelled chemical species
spec_list=['SO2','NOx','PM10','PM25','BaP']
# number of emitted chemical species
NSE=5
#

#Input Group 4
# pocet vertikalnych hladin
NZ=10
#definicia jednotlivych vertikalnych hladin
ZFACE='0,20,40,100,200,400,700,1100,1600,2000,3000'


# INPUT GROUPS: 13a, 13b, 13c, 13d -- Point source parameters
#pocet bodovych zdrojov
NPT1=0
#Units used for point source emission [g/s]
IPTU=1
# pocet znecistujucich latok pre zdroj s variabilnym emisnym faktorom
NSPT1=0
# pocet bodovych zdrojov s variabilnym emisnym faktorom v externom subore
NPT2=1
#pocet suborov s externymi bodovymi zdrojmi
NPTDAT=1


# INPUT GROUPS: 21a & 21b -- Non-gridded (discrete) receptor information
#nacitanie suboru s discrete receptors do dataframe
#skontrolovat, ci je v subore s diskretnymi receptormi pridana aj NMSKO, resp. ine lokality.

# ak su diskretne receptory v textovom subore s hotovym formatom pre calpuff.inp
df_disc= open(disc_file, "r")
zoznam_bodov=df_disc.readlines()
df_disc.close()


'''
# ak su diskretne receptory v textovom subore s nasledovnym formatom
# x_LCC[m], y_LCC[m], elevation[m] 
#konverzia x,y na km a zaokruhlenie
df_disc=pd.read_csv(disc_file,index_col=None,sep='|')
df_disc['x']=round(df_disc['x_lcc']/1000,3)
df_disc['y']=round(df_disc['y_lcc']/1000,3)
df_disc['elev']=round(df_disc['alt'],2)
'''


#number of non-gridded receptors
#NREC=len(df_disc.index)


#vseobecna cast, spolocna pre vsetky subory

#pocet meteo suborov NMETDAT
pocet_meteo=len(meteo_list)

#nacitanie konfiguracie domeny a urcenie potrebnych parametrov

with open(f'{geodatdir}/{domena}/Domain_conf.yml') as file:
    srec = yaml.full_load(file)

#definicia mriezky
xorigkm=srec['xorigkm']
yorigkm=srec['yorigkm']

nx=srec['nx']
ny=srec['ny']

res=srec['dgridkm']

           
#pridame do dataframe stlpec s nulami pre downwash (ak ho nechceme modelovat)- parameter building downwash
fdata['downwash']=0

#pripravime si dataframe s emisiami prekonvertovanymi na spravne jednotky a pre kazdy riadok vygenerujeme jeden calpuff input file
#vysledne jednotky pre emisie - g/s - parameter IPTU
df=fdata[['N','lat','lon','x_LCC', 'y_LCC','vyska', 'alt','priemer_mv','rychlost','teplota_mv','downwash','so2', 'nox','pm10','pm2.5','bap','typ']]
# prepocet z ton/rok na g/s
df['so2']=round(df['so2']*1000*1000/365/24/3600,6)
df['nox']=round(df['nox']*1000*1000/365/24/3600,6)
df['pm10']=round(df['pm10']*1000*1000/365/24/3600,6)
df['pm2.5']=round(df['pm2.5']*1000*1000/365/24/3600,6)
# prepocet z kg/rok na g/s
df['bap']=round(df['bap']*1000*1000/365/24/3600,10)

#transformacia lat,lon suradnic na LCC a vypocet elevation z DEM rastera
df['x_lcc']=0
df['y_lcc']=0
df['elev']=0

'''
geodatdir="/users/p2993/calmet/geodat"
#suradnice pre stanice NMSKO
with open(f'{geodatdir}/{domena}250/station_rec.yml') as file:
    srec = yaml.full_load(file)

#dataframe so suradnicami pre vsetky NMSKO v domene
nmsko=pd.DataFrame()
nmsko['id']=''
nmsko['x']=0.0
nmsko['y']=0.0
nmsko['elev']=0.0
'''


with rasterio.open("/data/users/ext33340/calpuff/sources/dem_sk_250.tif") as rds:
    # convert coordinate to raster projection
    transformer = Transformer.from_crs("EPSG:4326", rds.crs, always_xy=True)
    
    for index,row in df.iterrows():
     xx, yy = transformer.transform(df['lon'].iloc[index], df['lat'].iloc[index])
     df['x_lcc'].iloc[index]=xx
     df['y_lcc'].iloc[index]=yy

    # get value from DEM grid

     value = list(rds.sample([(xx, yy)]))[0]
     df['elev'].iloc[index]=value


#suradnice prekonvertovane na km - skontrolovat jednotky
df['x_lcc']=round(df['x_lcc']/1000,3)
df['y_lcc']=round(df['y_lcc']/1000,3)
df['elev']=round(df['elev'],0)

#nastavenie pocitadla pre poradove cislo suboru
n=1

#loop cez dataframe, vyberame len typ "annual"
for l in range(0, len(df)):
  
 
 if (df['typ'].loc[l] == group):  
 

# otvorime na citanie vzorovy input file a na zapis input file pre konkretny zdroj    
     
  fin=open(sample_inp_calpuff, "rt")

  fout = open(f"{inp_path}/calpuff_{n}.inp","wt")

  #for each line in the input file
  
  for line in fin:

 
  
    
  #Input Group 0 
  #CALPUFF.LST subor  
   cpf_lst=f'{out_path}'+ '/' +f"calpuff_{n}.lst"
   line=line.replace("__PUFLST__",cpf_lst)

  #CONC.DAT subor   
  # nazov musi mat aj s cestou <= 70 znakov - viac znakovy nazov sa nespracuje v calsume  
   conc_dat=f'{concdir}/conc_{n}.dat'
   line=line.replace("__CONDAT__",conc_dat)
       
  # pocet meteo suborov - NMETDAT 
   line=line.replace("__NMETDAT__",str(pocet_meteo))
   
  # pocet extrenych suborov s bodovymi zdrojmi - NPTDAT 
   line=line.replace("__NPTDAT__",str(NPTDAT)) 
 
  
  #meteo subory
   if "__METDAT__" in line:
     for j in range (0,pocet_meteo):
         meteo_file=sorted_meteo_list[j]
         line=meteo+' ='+f'{meteo_dir}'+sorted_meteo_list[j]+' !   !END!'+'\n'
         if j<pocet_meteo-1:
           fout.write(line)
             
  # PTERMAB.DAT subory
   line=line.replace("__PTEMARB__",f"/users/p2993/dbase_calpuff/source_arb/{domena}/{group}/ptemarb_{n}.dat")          
      
  #Input Group 1
  # definition of starting/ending date
    
   line=line.replace("__IBYR__",f'{IBYR}')
   line=line.replace("__IBMO__",f'{IBMO}')
   line=line.replace("__IBDY__",f'{IBDY}')
   line=line.replace("__IBHR__",f'{IBHR}')
   line=line.replace("__IBMIN__",f'{IBMIN}')
   line=line.replace("__IBSEC__",f'{IBSEC}')
   line=line.replace("__IEYR__",f'{IEYR}')
   line=line.replace("__IEMO__",f'{IEMO}')
   line=line.replace("__IEDY__",f'{IEDY}')
   line=line.replace("__IEHR__",f'{IEHR}')
   line=line.replace("__IEMIN__",f'{IEMIN}')
   line=line.replace("__IESEC__",f'{IESEC}')
   line=line.replace("__NSECDT__",f'{NSECDT}')
     
       
    
       
  # chemical species 
   line=line.replace("__NSPEC__",f'{NSPEC}') 
   line=line.replace("__NSE__",f'{NSE}')
   
  
  # Input Group 3
  # Species list
  # na spravne vygenerovanie obsahu Input Group3 pouzivame paramater input_group3
  
  #vo vzorovom input subore je len 1 vseobecny riadok pre ZL
    
  
   if   '__CSPEC__ ' in line:
     for i in range (len(spec_list)):
       line1=line  
       line1=line1.replace('__CSPEC__',spec_list[i])
       if i< len(spec_list)-1:
           fout.write(line1)
       else:
           line=line1
           
   if '__SPEC_GROUP3__' in line:
     for i in range (len(spec_list)): 
      line1=line
      line1=line1.replace('__SPEC_GROUP3__',spec_list[i])
      if i< len(spec_list)-1:
           fout.write(line1)
      else:
           line=line1     
          
   
            
  # Input Group 4
  # parametre pre definiciu domeny nacitame z konfiguracneho suboru pre domenu
  
   line=line.replace("__NX__",str(nx)) 
   line=line.replace("__NY__",str(ny))
   line=line.replace("__NZ__",str(NZ))
   line=line.replace("__DGRIDKM__",str(res))
   line=line.replace("__ZFACE__",ZFACE)
   line=line.replace("__XORIGKM__",str(xorigkm))
   line=line.replace("__YORIGKM__",str(yorigkm))
   line=line.replace("__IECOMP__",str(nx))
   line=line.replace("__JECOMP__",str(ny))
   line=line.replace("__IESAMP__",str(nx))
   line=line.replace("__JESAMP__",str(ny))
   

    
  #Input Group 5 
   
       
   if '__SPEC_GROUP5__' in line:
      for i in range (len(spec_list)):
       line1=line   
       line1=line1.replace('__SPEC_GROUP5__',spec_list[i])
       if i< len(spec_list)-1:
           fout.write(line1)
       else:
           line=line1
          



# Input group 13a
   line=line.replace("__NPT1__",str(NPT1))
   line=line.replace("__IPTU__",str(IPTU))
   line=line.replace("__NSPT1__",str(NSPT1))
   line=line.replace("__NPT2__",str(NPT2))

# definicia parametrov zdroja - InputGroup 13b
#nazov zdroja
   line=line.replace("__POINT__",'P'+str(n))
# parametre zdroja 
   str_source_def=(str(df.loc[l,'x_lcc'])+','+str(df.loc[l,'y_lcc'])+','+str(df.loc[l,'vyska'])+','+str(df.loc[l, 'elev'])+','
                 +str(df.loc[l,'priemer_mv'])+','+str(df.loc[l,'rychlost'])+','
                 +str(df.loc[l,'teplota_mv'])+','+str(df.loc[l,'downwash'])+','+str(df.loc[l,'so2'])+','+str(df.loc[l, 'nox'])+','
                 +str(df.loc[l,'pm10'])+','+str(df.loc[l,'pm2.5'])+','+str(df.loc[l,'bap']))

   line=line.replace("__POINT_SOURCE__",str_source_def) 



 
   ''' 
# Input group 17   
   
   line=line.replace("__NREC__",str(NREC))   
   

# discrete receptors

   if "__XDISC__" in line:
     line1=line   
     counter=1
     for index, row in df_disc.iterrows(): 
       suradnice= str(row['x'])+",   "+str(row['y'])+",   "+str(row['elev'])+",   "+str(2)
       line=str(counter)+'  '+line1.replace('__XDISC__',suradnice)
       counter=counter+1
       if counter < NREC+1:
        fout.write(line)
   '''
   
   
#Input Group 21 - DOROBIT
   if "__NRGRP__" in line:
      line=line.replace("__NRGRP__",str(2)) 

   if "__GRPNAME_" in line: 
      line="! RGRPNAM =  grp0         !   !END! \n"

      fout.write(line)
      line="! RGRPNAM =  grp1         !   !END! \n"      
 
      fout.write(line)
      line=""
 
      

   NREC=len(zoznam_bodov)
   #pripocitame 1 receptor za AMS - treba to este dorobit 
   line=line.replace("__NREC__",str(NREC+1))   

   if  "__XDISC__" in line:

    for i in zoznam_bodov:
       fout.write(i)
    # manualne pridame pre Jelsavu monitorovaciu stanicu   
    line='674 ! grp1 = 254.582,  103.817, 273, 2.0    !   !END!'   
   
   
   
    

   fout.write(line)


#close input and output files
  fin.close()
  fout.close()
  n=n+1

