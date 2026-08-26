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

Each of the subdirectories contains *bin* directory with a number of scripts. The order of the processing follows the order of the subdirectories above. 
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

 ### 5. Running CALSUM, CALPOST and preparing NETCDF files for `heat` and `neis` sectors
 #### 1.	CALSUM - Summing output files (such as concentration files CONC.DAT) from multiple independent CALPUFF  runs (output from 4).

 ##### a) Create the Input Control Files (CALSUM.INP) 
**script:** /users/oko001/cpf_proc/calsum/bin/generate_calsum_baliky.py  
**calsum version used:** /users/p2828/mod/CALSUM_v7.1.0_L190131/calsum.x

>[!NOTE]
>The file name of the *.dat/*.lst files must not be entered as an "absolute path" !!!
  
 #####  b) Execute CALSUM (dorobit automatizaciu)

 #####  c) Check CALSUM *.lst files 
 script: /users/oko001/cpf_proc/calsum/bin/calsum_output_check.py

 #### 2.	 CALPOST: Generating hourly time series from  binary output files produced by CALSUM for
- Regular grid receptors  
- Discrete receptors   
- AMS receptors, or points of interest  

##### a) Create the Input Control Files (CALPOST.INP)
For all types of receptors, a single script is used; however, the user must update the script settings depending on the receptor type (parameter grid).  

**script:** /users/oko001/cpf_proc/calpost/bin/create_calpost_inp.py.  
The script generates a Bash file named run_calpost_<group>, which is submitted to Slurm using sbatch run_calsum
**calpost version used:** /users/p2828/mod/calpost/CALPOST_v7.2.0_L150720/calpost.x  
**calpost input template file:** /users/oko001/cpf_proc/calpost/bin/calpost_sample.inp



 #### 3.	Generating netcdf files using python scripts
##### a)	Grid receptors: */users/ext33340/python_skripty/calpost_timeseries_to_xarray_grid.py*
##### b) Discrete receptors: */users/ext33340/python_skripty/calpost_timeseries_to_xarray.py*


## POSTPROCESSING
This part of the process brings together the `heat` AND `neis` concentrations with the `road` concentrations produced by ATMOSTREET model, and 
background concentrations from a regional model (RIO, CAMS or CMAQ).
Outputs are in the form of:
- Total annual concentration maps and annual sector maps (`/data/users/oko001/data_cpf/pics/{year}/{dom}/conc`)
- Source apportionment (SA) graphs for the locations of monitoring stations (`/data/users/oko001/data_cpf/pics/{year}/{dom}/graphs`)
- Tables with numerical values of SA for the locations of monitoring stations and validation statistics (`/data/users/oko001/data_cpf/pics/{year}/{dom}/SA`)

Postprocessing involves several steps:

1. Preparation of background concentrations

2. Processing of road traffic concentrations from ATMOSTREET

3. Producing total concentration maps (! includes RIO background timeseries production)

4. Producing source apportionment graphs for monitoring stations and validation statistics

5. Producing source apportionment maps

Details are explained in [Postprocessing (`postproc`)](docs/postproc.md).


* [Utilities (`utilities`)](docs/utilities.md)


```bash
cd preproc/bin
python main_preproc.py --domena 1
