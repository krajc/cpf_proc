# Processing of CALMET/CALPUFF

## Structure
**Root directory:**   *cpf_proc*

**Sub dierectories:**
- *aladin*
- *preproc*
- *calwrf*
- *calmet*
- *calpuff*
- *calpost*
- *postproc*
- *prtmet*
- *utilities*

Each of the subdirectories contains *bin* directory with a number of scripts. The order of the processing pretty much follows the order of the subdirectories above. 
All but one of the scripts is run on HPC3 cluster. One script (`~/python/CPF_preproc/0_domains_for_CALPUFF.py`) is run on **srv-atmosys** because it requires GRASS GIS for processing.

## Main steps

### 0. Convert ALADIN meteo data to CALMET .m3d format
`~/cpf_proc/aladin/bin/juraj_ALADIN2CALMET.py` 
 
When processing a new domain from scratch, the following steps must be taken. Assuming we want to run CALPUFF for three main emission sectors: residential heating, NEIS and road traffic. 
### 1. Setting up the domain (or multiple domains)
`~/cpf_proc/preproc/bin/0_domains_for_CALPUFF.py` (`srv-atmosys`)
 
 Na zaklade manualne vytvorenej vrstvy .shp, vytvara .shp subory jednotlivych domen (Vystup: `/data/oko/krajc/cpf_domeny`),  `Creg` a `Mreg`  v `LCCcpf` mapsetoch, ` Domain_conf.yml` (parametre domeny), 
 `geo.dat` pre CALMET a `station_rec.yml` pre CALPUFF. (Vystupy: `/data/oko/krajc/dbase_calpuff/geodat/LCCcpf/<domena>`).

 Tento skript vytvorí všetky potrebné dáta a súbory pre spustenie CALMET (okrem meteodát). 

 **POZNÁMKA**
 (JK): Foldery s výstupmi tohto skriptu: `/data/oko/krajc/cpf_domeny/` a `/data/oko/krajc/dbase_calpuff/geodat/LCCcpf` sú zatiaľ pod mojim userom na atmosyse (nie je na ňom vytvorený user oko001)

 ### 2. Run CALMET
 Procedures for running CALMET are described in detail in [CALMET (`calmet`)](docs/calmet.md) 
 Before proceeding to the next step - running CALPUFF - it is advisable to look at the meteo data produced by CALMET and, if possible, validate them against a meteo station data, if available. 
 This is done through series of scripts described in [PRTMET (`prtmet`)](docs/prtmet.md)

 ### 3. Prepare discrete receptors file
 Before running CALPUFF, we need prepare receptor files, which is done in `~/cpf_proc/preproc/1_create_discrete_recs.py`. It is based on the locations of residential heating sources - receprors are denser near heating sources and less dense elsewhere 

 ### 4. Run CALPUFF
 CALPUFF is run for residential heating (`heat`) and NEIS (`neis`). Road traffic (`road`) is run externaly using ATMOSTREET model, and is added to the domain in postprocessing stage. 
 Before running CALPUFF, it is necessary to prepare **receptor points**  `~/cpf_proc/preproc/1_create_discrete_recs.py`. 
 Detailed guide for running CALPUFF for residential heating is described in [CALPUFF (`calpuff`)](docs/calpuff.md)
 Detailed guide for running CALPUFF for NEIS is described in [CALPUFF_neis (`calpuff_neis`)](docs/calpuff_neis.md)

 ### 5. Running CALPOST and prepraring NETCDF files for `heat` and `neis` sectors
 .... doplni katka/janka .....

## POSTPROCESSING
This part of the process brings together the `heat` AND `neis` concentrations with the `road` concentrations produced by ATMOSTREET model, and 
background concentrations from a regional model (RIO, CAMS or CMAQ).
Outputs are in form of:
- Total annual concentration maps and annual sector maps
- Source apportionment (SA) graphs for the locations of monitoring stations
- Tables with numerical values of SA for the locations of monitoring stations and validation statistics

Postprocessing involves several steps:

### 1. Preparation of background concentrations

### 2. Processing of road traffic concentrations from ATMOSTREET

### 3. Producing total concentration maps (! includes RIO background timeseries production)

### 4. Producing source apportionment graphs for monitoring stations and validation statistics

### 5. Producing source apportionment maps

## Documentation

Detailná dokumentácia k jednotlivým krokom a ich nastaveniam sa nachádza v adresári `docs/`. Kliknutím na odkazy nižšie prejdeš na príslušnú časť:


* [Postprocessing (`postproc`)](docs/postproc.md)
* [Utilities (`utilities`)](docs/utilities.md)


```bash
cd preproc/bin
python main_preproc.py --domena 1
