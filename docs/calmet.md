# Spúšťanie modelu CALMET 

Na spustenie CALMET potrebujeme mať vstupné meteorologické dáta z meteorologického prognostického modelu v správnom formáte 
(ascii subory .m3d). Tieto súbory vytvára Juraj (.... tu doplniť link na jeho dokumentáciu ...) 
`~/cpf_proc/calmet/bin/run_calmet_mproc.py` submituje skript `calmet_mproc.py` na 1 node (40 cpu) pomocou knižnice `multiprocessing` (Pool)

Poznámka: 
Meteo súbory sa pôvodne konvertovali pomocou CALWRF zo štandardného formátu NETCDF z modelu WRF, preto v adresári existujú aj 
tieto verzie skriptov.

`check_file_sizes_dom.py` skontroluje existenciu a velkost vystupnych suborov a tie ktore nie su v poriadku zapise do `rerun.dat` suboru, na ktory
sa potom znova spusti `run_calmet_mproc.py` (ten uz pri spustani kontroluje pritomnost rerun suboru, ak ho najde tak spusti ten namiesto kompletneho runu)







