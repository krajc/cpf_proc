# Spúšťanie CALPUFF pre lokálne kúreniská - `heat`

Skupina `heat` je rozdelena na podskupiny: 

*rd* - rodinne domy,
*bd* - bytove domy,
*no* - nekonvencne obydlia,
*os* - ostatne.

Pred spustením modelu CALPUFF je potrebné mať pre daný simulovaný rok:

- Celkové ročné koncentrácie pre jednotlivé ZL z emisného modelu REM3 (__odkaz na manual k modelu REM3__)
- ASCII subory s casovo premenlivymi emisiami pre jednotlive gridove stvorce, ktore su vystupom z `~/cpf_proc/preproc/bin/create_volemarb_dom.py`
  
**`~/cpf_proc/calpuff/bin/`**

`run_calpuff_mproc.py` spusta `calpuff_mproc_heat.py` na zaklade casovo premenlivych `volemarb.dat` suborov v `~/dbase_calpuff/source_arb/<dom>/.` Mnozstvo zdrojov rozdeluje na batche (default 200 na 1 node, ale da sa zmenit) a zdroje rozhodi na prislusne potrebne mnozstvo nodov. POZNAMKA: Informacia o pocte zdrojov v jednotlivych domenach je v `/work/users/oko001/cpf_proc/volemarb/heat_sources_<dom>_2024.info`

`analyze_calpuff_runs_dom.py` analyzuje .lst fily z jednotlivych calpuff runov, robi statistiku trvania (CPU time) a zapisuje chybajuce zdroje do rerun filu, ktory ak je nenulovy, treba nan znovu spustit `run_calpuff_mproc.py`. Ten si kontroluje ci existuje rerun subor a ak ano tak ho spusti `calpuff_mproc_heat_rerun.py` namiesto kompletneho runu. 

