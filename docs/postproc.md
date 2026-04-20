# Postprocessing

## 1. Preparation of background concentrations

Ako pozadie je možné použiť modely RIO, CAMS alebo CMAQ. Aktuálne (apríl 2026) ešte nie je vyhodnotené, ktoré pozadie je 
najvhodnejšie. Pre mapy koncentracii uvazujeme konstantne pozadie. Metody vyberu bodu/bodov pozadia sa lisia medzi RIO
a CTM modelmi CMAQ a CAMS. RIO je interpolacny model, preto sa bod pozadia vybera bud automaticky (vid bod 3) alebo 
manualne, pricom ide o priemerne denne hodnoty. CTM modely uvazuju s meteorologiou, teda existuje v kazdom case naveterna
cast domeny. Body pozadia sa menia kazdu hodinu v zavislosti od smeru vetra na naveternej strane domeny. 
Tu sú skripty, ktoré pripravia pozadie z jednotlivých modelov: 

**RIO**

Vzhľadom na vysoké rozlíšenie modelu je potrebné najprv z veľkých .tiff súborov pre celú SR vystrihnúť doménu:

`/users/p2993/cpf_proc/postproc/bin/run_cutout_doms_RIO.py`

Bod pozadia a casovy rad z tohto bodu sa vybera az v kroku 3. 

**CMAQ**

`/users/p2993/cpf_proc/postproc/bin/background_points_CMAQ.py`

**CAMS**
 
`/users/p2993/cpf_proc/postproc/bin/background_points_CAMS.py`

## 2. Processing of road traffic concentrations from ATMOSTREET

ATMOSTREET vypocitava PM zvlast pre priame emisie a zvlast pre resuspenziu. Pred dalsim spracovanim je potrebne 
tieto dva prispevky spocitat. Skript pri prvom spusteni pre dany rok vypocita sucet pre celu domenu a z .csv pre receptory stanic 
(vsetky su v jednom subore). Nasledne uz sa spustaju iba jednotlive domeny (vytvorenie vyrezov). 
`/users/p2993/cpf_proc/postproc/bin/atmostreet_postproc_road.py `

## 3. Producing total concentration maps (! includes RIO background timeseries production)



## 4. Producing source apportionment graphs for monitoring stations and validation statistics



## 5. Producing source apportionment maps

