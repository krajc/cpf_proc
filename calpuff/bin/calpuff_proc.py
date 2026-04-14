#!/usr/bin/env /users/oko105/PythonTest/PythonTest/bin/python

'''
Skript vyraba calpuff.inp subory 
Toto je stary skript ani si nan  nepamatam, je pre cesty s casovymi profilmi


'''
import os
import datetime
import pandas as pd

# Switch ci je treba vytvarat calpost.inp subor. Ak ano - 1. 
year = 2017
dom = "jelsava"
domena = "{}250".format(dom)
group = "road"
ggroup = 'xx'
species = ('SO2','NOx','PM10','PM25','BaP')

roadfile = "/home/KOL/p2828/roads_for_calpuff/roads_points_emissions_jelsava.txt"
recfile = "/home/KOL/p2828/roads_for_calpuff/receptors12353/receptors_50_jelsava_200_alt_new_corr"

# Number of defined emission scale factor tables:
nsftab = 1
sctablename = "road_daily"
sctable = "0.74,0.74,0.62,0.50,0.67,0.96,1.27,1.34,1.22,1.08,0.96,0.94,0.89,0.89,0.91,0.98,1.03,1.10,1.20,1.27,1.25,1.18,1.13,1.01,0.84"

calpuff_templ = "/data/oko/krajc/calpuff/templates/calpuff7-{}.inp.templ".format(group)
pth = "/data/oko/krajc/calpuff/{}/{}/{}".format(domena,group, ggroup)
datdir = "/data/users/nwp108/data_cpf/{}".format(domena)
concfile = "{}/conc-{}.dat".format(datdir, domena, ggroup)
calpuff_inp = "{}/{}-{}.inp".format(pth, group, ggroup)
calpuff_lst = "{}/{}-{}.lst".format(pth, group, ggroup)
'''
Temporary (currently uncertain) road parameters (effective height, sigma Y and Z:
plumeH je cca vyska stredu vlecky, povedme cca 1m, sirka cesty je 2x (alebo 4x pri dialnici)sirka 
jazdnehopruhu, ktory je podla noriem cca 3 - 3.5m
'''
plumeH, roadW = 1, 6
eH, sigY, sigZ = plumeH, plumeH/2.15, roadW/2.15

if not os.path.exists(pth):
    os.makedirs(pth)

# Read in receptor data file:
rc = pd.read_csv(recfile, sep='|')
nrec = len(rc.index)
# Non-gridded receptor definition string:
recstring = ""
for i in range(nrec):
    recstring = recstring + "{} ! X = {}, {}, {}, {} !  !END!\n".format(i+1, 
                             rc.loc[i,'x']/1000, rc.loc[i,'y']/1000, rc.loc[i,'z'], 2)
    
# Read in road data file:
rd = pd.read_csv(roadfile, sep='|', index_col='cat')
r = rd.groupby('cisloSU')['so2','nox','pm10','pm25','bap'].max()
r = r.astype(str)
roads = list(r.index)

rid = roads[0]
seg = rd[rd['cisloSU']==rid]

# road source string
emissions = ", ".join(list(r.loc[rid,:]))
roademistring = "! SRCNAM = R{} !\n1 ! X =  {},  {},  {}, {} ! !END!\n".format(
        rid, eH, sigZ, sigY, emissions)
# road scale string
roadscalestring = ""
j = 0
for i in species:
    j = j+1
    roadscalestring = roadscalestring + "{} ! SCALEFACTOR = 1,   {},  {} ! !END!\n".format(
            j, i, sctablename)
# road segments definition:
npoints = len(seg.index)
roadsegstring = "! SRCNAM = R{} !\n! NPTROAD = {} !\n ! END !\n".format(rid, npoints)
for i in range(1,npoints+1):
    roadsegstring = roadsegstring + "{} ! XYZ = {}, {}, 2.0 ! !END!\n".format(i, 
                                     seg.loc[i,'x']/1000, seg.loc[i,'y']/1000)
# Scale factor table definition:
scaletabstring = "1 !FACTORNAME = {} !\n1 !FACTORTYPE = HOUR24 !\n1 !FACTORTABLE = {} !\n1 !END!\n".format(
        sctablename, sctable)

# Number of met. files
nmetdat = 365
# Creating metdatstring:
metdatstring = ""
for i in range (1,nmetdat+1):
    d = datetime.datetime.strptime('17{}'.format(i),'%y%j').date()
    metdatstring = metdatstring + '!  METDAT= {0}/meteo/calmet{1:02d}-{2:02d}.met !   !END!\n'.format(datdir,
                                              d.month, d.day)
# Use whole period specified in meteo data (if 1):
metrunswitch = 1
# Number of species:
nspec = 5
# Species list:
specieslist = ""
for i in species:
    specieslist = specieslist + "! CSPEC = {} ! !END!\n".format(i)
# Species table:
speciestable = ""
for i in species:
    speciestable = speciestable + "! {} = 1,    1,    0,    0 !\n".format(i)
# Met. grid definition (dimensions in cells, resolution and SW corner in km)
mnx, mny, mnz = 36, 32, 10
reskm, mxorig, myorig = 0.25, 246.75, 102.25
vertlayerstring = "! ZFACE = 0,20,40,100,200,400,700,1100,1600,2000,3000      !"
# Comp. grid and sampling grid extent and sampling grid density(in cells of met. grid)
llx, lly, urx, ury, meshdens = 2, 2, 35, 31, 1
# Output options:
outoptstring = ""
for i in species:
    outoptstring = outoptstring + "! {} = 0,    1,    0,    0,    0,    0,    0 !\n".format(i)
# Number of road links, and no of road links with scaling factors in .inp file:
nrd1, nsfrds = 1, 1



# Static parameters:
parsstat = {
         "__nmetdat__": nmetdat,
        "__metdatstring__": metdatstring,
        "__metrunswitch__": metrunswitch,
        "__nspec__": nspec,
        "__specieslist__": specieslist,
        "__speciestable__": speciestable,
        "__mnx__": mnx,
        "__mny__": mny,
        "__mnz__": mnz,
        "__reskm__": reskm,
        "__vertlayerstring__": vertlayerstring,
        "__mxorig__": mxorig,
        "__myorig__": myorig,
        "__llx__": llx,
        "__lly__": lly,
        "__urx__": urx,
        "__ury__": ury,
        "__meshdens__": meshdens,
        "__outoptstring__": outoptstring,
        "__nrd1__": nrd1,
        "__nsfrds__": nsfrds,
        "__nsftab__": nsftab,
        "__scaletabstring__": scaletabstring,
        "__nrec__": nrec,
        "__recstring__": recstring
        }

pars = {
        "__lstfile__": calpuff_lst,
        "__concfile__": concfile,
        "__roademistring__": roademistring,
        "__roadscalestring__":roadscalestring,
        "__roadsegstring__": roadsegstring,
        }

def create_inp (template, output, paramsstat, params):
        
        with open(template, encoding='cp1252') as f_obj:
            templ = f_obj.read()
        
        for i in paramsstat.keys():
            templ = templ.replace(i, str(paramsstat[i]))
        for i in params.keys():
            templ = templ.replace(i, str(params[i]))
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(templ)
    
create_inp (calpuff_templ, calpuff_inp, parsstat, pars)

#subprocess.call(['ls','-aop'])
#subprocess.call("{} {}".format(exe,calpost_inp), shell=True)
