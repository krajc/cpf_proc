#!/users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Vytvori rerun subor obsahujuci obdobia epizody
(v pripade, ze nechceme spustat cely rok)
"""

year = 2023
dom = 'bratislava'
#disk =  '/data/users/p2993'
rerunfile = f'/users/p2993/cpf_proc/calmet/rerun{year}_{dom}.inp'

episodes = {
    2: [6,25],
    9: [6, 14]
}

rerun = []


for month in episodes.keys():
     
    for day in range(episodes[month][0],episodes[month][1]+1):
        rerun.append(f'{year}-{month:02d}-{day:02d}\n')
       
with open(rerunfile, 'w') as f:
    for line in rerun:
        f.write(line)
