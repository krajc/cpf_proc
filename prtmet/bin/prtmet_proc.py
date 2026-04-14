#!/users/p6065/anaconda3/envs/supergeo/bin/python

'''
Skript vyraba prtmet.inp subory na vyrobu hodinovych poli .asc za cely rok 
a spusta na tento subor PRTMET.


'''
import os
import subprocess
import re
import calendar
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('domena', type=str)
parser.add_argument('yr', type=int)
args = parser.parse_args()

dom = args.domena
year = args.yr

domena = dom
workdir = f"/work/users/p2993/prtmet/{dom}/asc"
prtmetdir = "/users/p2993/cpf_proc/prtmet"
outdir = f"/data/oko/krajc/data_cpf/prtmet/{year}/{dom}"
prtmet_inp = f"{prtmetdir}/{dom}/prtmet.inp"
listfile = f"{prtmetdir}/{dom}/prtmet.lst"
inpdir = f"/data/oko/krajc/data_cpf/calmet/{year}/{dom}"

#Template pre prtmet.inp:
prtmet_templ = f"{prtmetdir}/templates/prtmet.templ"
exe = "/users/p2993/bin/prtmet"

# vytvorime potrebne adresare:
if not os.path.exists(workdir):
    os.makedirs(workdir)
if not os.path.exists(f"{prtmetdir}/{dom}"):
    os.makedirs(f"{prtmetdir}/{dom}")
if not os.path.exists(outdir):
    os.makedirs(outdir)    

################## Funkcie ###################        
# Vytvaranie .inp suborov:
def create_inp (month, day):

    metfile = f"{inpdir}/{year}-{month:02d}-{day:02d}.dat"
    '''
    if (month == 12) & (day == 31):
        endhour = 22
    else:
        endhour = 23
    '''
    endhour = 23
    with open(prtmet_templ) as f_obj:
        template = f_obj.read()

    template = template.replace("__METFILE__",metfile)
    template = template.replace("__LISTFILE__",listfile)
    template = template.replace("__IBYR__",str(year))
    template = template.replace("__IBMO__",str(month))
    template = template.replace("__IBDY__",str(day))
    template = template.replace("__IEYR__",str(year))
    template = template.replace("__IEMO__",str(month))
    template = template.replace("__IEDY__",str(day))
    template = template.replace("__IEHR__",str(endhour))
    
    with open(prtmet_inp, 'w') as f:
        f.write(template)
    return metfile
########################################################

#************** program **************
# Zmena workdir na tu, kam chceme aby sa zapisovali vystupy:
os.chdir(workdir)
# Argumenty pre subprocess.run:
args = [exe, prtmet_inp]

for m in range(1,13):
    
    # zistenie posledneho dna v mesiaci:
    endday = calendar.monthrange(year,m)
    
    
    for d in range (1,endday[1]+1):
        
        metfile = create_inp (m, d)
                
        print(f"running month:{m}, day:{d}\n")
        
        try:
            output = subprocess.run(args, capture_output=True, text=True)
            print (output.stderr)
            print (output.stdout)
        
        except Exception:
            print(f'Execution of prtmet has failed for {metfile}! \n')
