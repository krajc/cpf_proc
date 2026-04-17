# Spúšťanie CALPUFF pre lokálne kúreniská - `heat`

Skupina `heat` je rozdelena na podskupiny: 

*rd* - rodinne domy
*bd* - bytove domy
*no* - nekonvencne obydlia
*os* - ostatne

**`~/cpf_proc/calpuff/bin/`**

`run_calpuff_mproc.py` spusta `calpuff_mproc_heat.py` na zaklade casovo premenlivych `volemarb.dat` suborov v `~/dbase_calpuff/source_arb/<dom>/.` Mnozstvo zdrojov rozdeluje na batche (default 200 na 1 node, ale da sa zmenit) a zdroje rozhodi na prislusne potrebne mnozstvo nodov. 
`analyze_calpuff_runs_dom.py` analyzuje .lst fily z jednotlivych calpuff runov, robi statistiku trvania (CPU time) a zapisuje chybajuce zdroje do rerun filu, ktory ak je nenulovy, treba nan znovu spustit `run_calpuff_mproc.py`. Ten si kontroluje ci existuje rerun subor a ak ano tak ho spusti `calpuff_mproc_heat_rerun.py` namiesto kompletneho runu. 

