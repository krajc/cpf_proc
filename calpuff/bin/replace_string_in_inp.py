#!/usr/bin/env /users/oko105/PythonTest/PythonTest/bin/python

'''
Skript v existujucich inp suboroch vymeni zadany string za iny


'''
import os
import datetime
import pandas as pd
import sys

dom = "bratislava"
domena = "{}250".format(dom)
#pth = "/data/oko/krajc/calpuff/{}".format(domena)
pth = "."
group = "small2"
ggroup = 'bratislava_fh'

filenomin, filenomax = sys.argv[1], sys.argv[2]

nomelist = list(range(filenomin, filenomax+1))
str_old = "CONDAT = /data/users/nwp108"
str_new = "CONDAT = /data/oko/krajc"


for i in nomelist:
    with open("{}/calpuff-{}-{}.inp".format(pth,ggroup,i)) as f_obj:
        temp = f_obj.read()
    temp = temp.replace(str_old, str_new)    
    with open("{}/calpuff-{}-{}.inp".format(pth,ggroup,i),"w") as f:
        f.write(temp)
        
