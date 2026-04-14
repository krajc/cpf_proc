#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:55:18 2025

@author: p6065
"""
import sys
sys.path.append('/home/KOL/p6065/python-scripts/core')
sys.path.append('/users/p6065/python-scripts')
import numpy as np
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os
import time
import pygrib
import metpy.calc as mpcalc
from metpy.units import units
from metpy.calc import relative_humidity_from_specific_humidity, mixing_ratio_from_specific_humidity
import pyproj
from collections import defaultdict
import subprocess

path_ala2 = '/data/oko/dusan/ala_temp_2023/'  #'/data/nwp/ala2e/grib/sh20/'  # 
path_output = '/data/oko/meteo/'

names2d = ['prmsl','cwp','csf','lsf','lswp','sde','ssrd','sshf','2t','2sh','10u','10v','sp','orog']
names3d = ['t','u','v','q','clwc','crwc','ciwc','cswc']

tar_file = True
prepare_csv = True
prepare_nc = False

cutter = (200,-86,125,-138) # xlef,xright,ybot,ytop (200,-86,125,-138)
start_date = datetime(2024,4,28)
ndays = 96  #287
sleep_day = 0
sleep_file = 0
prepare_nc = False
prepare_csv = True
levels=40 # need to chage header
hours = 24 # min 4
max_lvl =87

rdwrf = 287
rvwrf = 461.6
giwrf = 1/9.81
pt = 0
p0 = 101325.

proj4 ='+proj=lcc +lat_1=48.80182499999999 +lat_2=48.80182499999999 +lat_0=48.80182499999999 +lon_0=18.111565 +x_0=0.0 +y_0=0.0 +a=6371229.0 +b=6371229.0 +units=m +no_defs:'
p =pyproj.Proj(proj4)
nx = 215 #501 - cutter[0] + cutter[1]
ny = 110 #373 - cutter[2] + cutter[3]
dx = 2000/1000  # km
dy = 2000/1000
xorig = (-501000.0000000002 + cutter[0]*2000)/1000  #km
yorig = (-373000.0000000017 + cutter[2]*2000)/1000
xend = xorig +(nx+1)*dx*1000
yend = yorig +(ny+1)*dy*1000
lonend, latend = p(xend,yend,inverse=True)
lonbeg, latbeg = p(xorig,yorig,inverse=True)

bf   = np.array([1.00000000e+00, 9.97621515e-01, 9.94968780e-01, 9.91835807e-01,
   9.88252355e-01, 9.84229631e-01, 9.79772520e-01, 9.74882396e-01,
   9.69558284e-01, 9.63797454e-01, 9.57595774e-01, 9.50947933e-01,
   9.43847599e-01, 9.36287534e-01, 9.28259690e-01, 9.19755280e-01,
   9.10764854e-01, 9.01278362e-01, 8.91285220e-01, 8.80774382e-01,
   8.69734411e-01, 8.58153565e-01, 8.46019886e-01, 8.33321311e-01,
   8.20045782e-01, 8.06433191e-01, 7.92696276e-01, 7.78793033e-01,
   7.64688145e-01, 7.50352544e-01, 7.35762948e-01, 7.20901384e-01,
   7.05754685e-01, 6.90313973e-01, 6.74574140e-01, 6.58533301e-01,
   6.42192250e-01, 6.25553909e-01, 6.08622778e-01, 5.91404395e-01,
   5.73904819e-01, 5.56130140e-01, 5.38086046e-01, 5.19777449e-01,
   5.01208204e-01, 4.82380932e-01, 4.63296986e-01, 4.43956570e-01,
   4.24359064e-01, 4.04503556e-01, 3.84389644e-01, 3.64018514e-01,
   3.43394336e-01, 3.22526005e-01, 3.01429226e-01, 2.80128966e-01,
   2.58662234e-01, 2.37081147e-01, 2.15456181e-01, 1.93879449e-01,
   1.72467786e-01, 1.51365292e-01, 1.31273982e-01, 1.12799372e-01,
   9.59450775e-02, 8.06985139e-02, 6.70316250e-02, 5.49018829e-02,
   4.42535121e-02, 3.50188823e-02, 2.71200160e-02, 2.04701548e-02,
   1.49753307e-02, 1.05358929e-02, 7.04794030e-03, 4.40460990e-03,
   2.49715510e-03, 1.21570320e-03, 4.49432000e-04, 8.53058000e-05,
   0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
   0.00000000e+00, 0.00000000e+00, 0.00000000e+00])[:levels+1]
af  = np.array([0.00000000e+00, 0.00000000e+00, 5.16961263e-06, 2.44936985e-05,
   6.39398075e-05, 1.29971665e-04, 2.29593782e-04, 3.70358766e-04,
   5.60365754e-04, 8.08255130e-04, 1.12320122e-03, 1.51490283e-03,
   1.99357157e-03, 2.56991754e-03, 3.25513161e-03, 4.06086365e-03,
   4.99919591e-03, 6.08261064e-03, 7.32395074e-03, 8.73637246e-03,
   1.03332887e-02, 1.21283015e-02, 1.41351220e-02, 1.63674761e-02,
   1.88389944e-02, 2.15123514e-02, 2.43456814e-02, 2.73447691e-02,
   3.05152648e-02, 3.38623320e-02, 3.73903643e-02, 4.11027608e-02,
   4.50017546e-02, 4.90882886e-02, 5.33619368e-02, 5.78208635e-02,
   6.24618204e-02, 6.72801736e-02, 7.22699555e-02, 7.74239342e-02,
   8.27336889e-02, 8.81896822e-02, 9.37813138e-02, 9.94969402e-02,
   1.05323843e-01, 1.11248129e-01, 1.17254528e-01, 1.23326090e-01,
   1.29443725e-01, 1.35585591e-01, 1.41726277e-01, 1.47835779e-01,
   1.53878231e-01, 1.59810381e-01, 1.65579805e-01, 1.71122856e-01,
   1.76362399e-01, 1.81205367e-01, 1.85540267e-01, 1.89234790e-01,
   1.92133776e-01, 1.94057851e-01, 1.94800588e-01, 1.94281376e-01,
   1.92504234e-01, 1.89489896e-01, 1.85275140e-01, 1.79911868e-01,
   1.73465957e-01, 1.66015972e-01, 1.57651776e-01, 1.48473116e-01,
   1.38588223e-01, 1.28112522e-01, 1.17167474e-01, 1.05879663e-01,
   9.43801940e-02, 8.28045860e-02, 7.12934903e-02, 5.99952340e-02,
   4.90758015e-02, 3.87817317e-02, 2.92667659e-02, 2.06241244e-02,
   1.29919687e-02, 6.60935488e-03, 2.14618846e-03])[:levels+1]

sigmap_half = (af[:-1]+af[1:])/2 + (bf[:-1]+bf[1:])/2
##########################################

def get_files( start_date,hours):
    ''' Find files in order, fail if one is missing'''
    out = list()
    yesterday = (start_date -timedelta( days =1)).strftime('%Y-%m-%d')
    today= start_date.strftime('%Y-%m-%d')
    out = [None]*(hours+1)
    for h in range(hours+1):
        if h==0 :
            #add hour fordecumulation
            # out[0] = path_ala2 + yesterday+'_12/'+'ALA2ESH20+0011.grb.CMAQ'
            out[0] = path_ala2 + yesterday+'_00/'+'ALA2ESH20+0023.grb.CMAQ'
        elif h==1:
            #add hour fordecumulation
            # out[1] = path_ala2 + yesterday+'_12/'+'ALA2ESH20+0012.grb.CMAQ'
            out[1] = path_ala2 + yesterday+'_00/'+'ALA2ESH20+0024.grb.CMAQ'
        else:
            out[h] = path_ala2 +today+'_00/'+'ALA2ESH20+{}.grb.CMAQ'.format( str(h-1).zfill(4)) # start with 0001 h make 0 from 12th 

    for h in out:
        if os.path.isfile(h):
            continue
        else:
            print('{} not found'.format(h))
            sys.exit()

    return( out)


def get_data(files, cutter, names2d, names3d, levels,max_lvl):
    ''' Read grib files'''
    starttime = datetime.now()
    out ={}
    for index,file in enumerate(files):
        # print(file)
        data = pygrib.open(file)
        for g in data:
            if  (index == 0) and (g.shortName not in ['cwp','csf','lsf','lswp','ssrd','sshf']): continue
            # print(g)
            if g.shortName in names2d:
                temp = None
                temp = g.values[cutter[2]:cutter[3], cutter[0]:cutter[1]]
                temp = np.expand_dims(temp, axis=0)
                if g.shortName not in out.keys(): out[g.shortName] = temp
                else: out[g.shortName] = np.concatenate( [ out[g.shortName], temp], axis=0)
        
            if g.shortName in names3d:
                if g.level <max_lvl-levels+1:      continue
                temp = None
                temp = g.values[cutter[2]:cutter[3], cutter[0]:cutter[1]]
                temp = np.expand_dims(temp, axis=0)
                if '{}_{}'.format( g.shortName, max_lvl -g.level) not in out.keys():  out['{}_{}'.format( g.shortName, max_lvl -g.level)] = temp
                else: out['{}_{}'.format(g.shortName, max_lvl -g.level)] = np.concatenate( [ out['{}_{}'.format(g.shortName, max_lvl -g.level)], temp], axis=0)  
    # deacumulate data accumulated
    for item in ['cwp','csf','lsf','lswp','ssrd','sshf']:
        t0 = np.expand_dims( out[item][1,:,:] - out[item][0,:,:],axis=0)
        t1 = np.expand_dims(out[item][2,:,:], axis=0)
        trest = out[item][3:,:,:] - out[item][2:-1,:,:]
        tstack = np.concatenate([t0,t1,trest],axis=0)
        out[item] = tstack
   
    param_groups = defaultdict(list)

    # make 3d data Group arrays by base parameter and collect levels
    for key, array in out.items():
        if '_' in key:
            param, level = key.rsplit('_', 1)  # Split by last underscore
            param_groups[param].append((int(level), array))  # Store (level, array)
        
    # Stack arrays efficiently
    d3d = {
        param: np.stack([arr for _, arr in sorted(arrays, key=lambda x: x[0])], axis=-1)
        for param, arrays in param_groups.items()
        }
    out = out | d3d  
    # remove 2d key layers from 
    keys_to_remove = [k for k in out.keys() if '_' in k]
    for k in keys_to_remove:
        del out[k]
    print('DATA reading time {} s '.format(  ( datetime.now() -starttime).seconds ))
    time.sleep(sleep_file)  # sleep after each file
    return( out)


def make_nc( ):
    # only 3 parameters
    out_name =  date_to_proc.strftime('%Y-%m-%d')
    t,y,x = data_in['2t'].shape

    path_out = path_output +'/nc'+ '/{}.nc'.format(out_name)
    ncfile = Dataset( path_out ,mode='w',format='NETCDF4_CLASSIC') 
    # create dim
    y_dim = ncfile.createDimension('y', y)     # latitude axis
    x_dim = ncfile.createDimension('x', x)    # longitude axis
    time_dim = ncfile.createDimension('time', t) # unlimited axis (can be appended to).
    #create vars
    temp = ncfile.createVariable('2t',np.float32,('time','y','x'))
    temp = ncfile.createVariable('10u',np.float32,('time','y','x'))
    temp = ncfile.createVariable('10v',np.float32,('time','y','x'))
    # create attributes
    ncfile.date = '{}'.format(out_name)
    ncfile.source='ALADIN_SHMU_2km'
    ncfile.xorig = '{}'.format(xorig)
    ncfile.yorig = '{}'.format(yorig)
    ncfile.proj4 = proj4
    ncfile.dx = dx*1000
    ncfile.dy = dy*1000
    ncfile.nx = '{}'.format(x)
    ncfile.ny = '{}'.format(y)
    # add var values
    ncfile.variables['2t'][:] = data_in['2t']
    ncfile.variables['10u'][:] = data_in['10u']
    ncfile.variables['10v'][:] = data_in['10v']
    ncfile.close()
    print('NC DONE - {}'.format(out_name))    

def make_csv(date_to_proc):
    starttime =  datetime.now()
    date =date_to_proc.strftime("%Y%m%d")
    ##### THIS PART WRITES HEADER
    h1 = '3D.DAT          2.1             WRF_ARW         V3.4.1           Created at 2024-11-22'
    h2 = '   1'
    h3 = 'Produced by CALWRF v2.0.3        Level: 190426'
    h4 = '  0  1  1  1  1  1'
    h5 = f'LCC   48.8018   18.1116  48.80  48.80  {xorig:>8.3f}{yorig:>10.3f}{dx:>8.3f}{nx:>4.0f}{ny:>4.0f}{levels:>3.0f}'
    h6 = '  1 19 15 17 14 17  0  0  0  0  0  0  0  0  0  0  0  0  0  0 25'
    h7 = f'{date}{"00"}{"   24"}{nx:>4.0f}{ny:>4.0f}{levels:>4.0f}' # pocet subdomain grid x y a pocet vrstiev
    h8 = f'{0:>4.0f}{0:>4.0f}{nx:>4.0f}{ny:>4.0f}{1:>4.0f}{levels:>4.0f}{lonbeg:>10.4f}{lonend:>10.4f}{latbeg:>9.4f}{latend:>9.4f}'
    
    sigmas ='\n'.join( [f'{sig:>6.3f}'for sig in sigmap_half])
           
    header = '\n'.join([h1,h2,h3,h4,h5,h6,h7,h8,sigmas])
    
    ##### THIS PART WRITES GRID META
    # print('Writing grid meta')
    with open("/data/oko/meteo/configs/grid/header_grid.txt") as f:
        grid_desc = f.readlines()
        
    indices = np.array(list(np.ndindex(data_in['2t'].shape)))
    
    starttime =  datetime.now()
    date =date_to_proc.strftime("%Y%m%d")
    # hour2d = [ f'{hour}'.zfill(2) for hour in range(hours)]
    hour2d = [f'{hour}'.zfill(2) for hour in indices[:,0]]
    nxx = indices[:,2]
    nyy = indices[:,1]
    pres = data_in['prmsl']/100   #hPa
    t2 = data_in['2t']
    q2 = data_in['2sh']*1000
    ws10 = mpcalc.wind_speed( data_in['10u'] * units('m/s'), data_in['10v'] * units('m/s')).magnitude
    wd10 = mpcalc.wind_direction( data_in['10u']* units('m/s'), data_in['10v']* units('m/s')).magnitude
    sst =np.array( [0.0]*(nx*ny*hours))
    
    sc = np.where(data_in['sde'] >= 1, 1, 0)
      
    rain = data_in['cwp'] + data_in['csf'] +data_in['lsf'] +data_in['lswp']
    radsw = data_in['ssrd'] /3600   # J/m2 to Watt
    radlw = data_in['sshf']/3600
    
    # FORMAT 2d
    formatted_nxx = np.char.mod('%3.0f', nxx)
    formatted_nyy = np.char.mod('%3.0f', nyy)
    formatted_pres = np.char.mod('%7.1f', pres.flatten())
    formatted_rain = np.char.mod('%5.2f', rain.flatten())
    formatted_sc = np.char.mod('%2.0f', sc.flatten())
    formatted_radsw = np.char.mod('%8.1f', radsw.flatten())
    formatted_radlw = np.char.mod('%8.1f', radlw.flatten())
    formatted_t2 = np.char.mod('%8.1f', t2.flatten())
    formatted_q2 = np.char.mod('%8.2f', q2.flatten())
    formatted_wd10 = np.char.mod('%8.1f', wd10.flatten())
    formatted_ws10 = np.char.mod('%8.1f', ws10.flatten())
    formatted_sst = np.char.mod('%8.1f', sst)
    
    # Step 2: Combine all parts row-wise
    formatted_rows2d = np.char.add(
        np.char.add(
            np.char.add(
                np.char.add(date, hour2d),
                np.char.add(formatted_nxx, formatted_nyy)
            ),
            np.char.add(
                np.char.add(
                    np.char.add(formatted_pres, formatted_rain),
                    formatted_sc
                ),
                np.char.add(
                    np.char.add(formatted_radsw, formatted_radlw),
                    np.char.add(
                        np.char.add(formatted_t2, formatted_q2),
                        np.char.add(
                            np.char.add(formatted_wd10, formatted_ws10),
                            formatted_sst
                        )
                    )
                )
            )
        ),
        "\n"
    )
    
    # FORMAT 3D
    
    pres3 = ((af[:-1] +af[1:])/2*p0 + np.einsum('i,jkl->jkli', (bf[:-1]+ bf[1:])/2, data_in['sp']))/100 #np.einsum(bf[:-1]+ bf[1:])/2*data_in['sp'])/100
    temp3 = data_in['t']
    ws3 = mpcalc.wind_speed( data_in['u'] * units('m/s'), data_in['v'] * units('m/s')).magnitude
    wd3 = mpcalc.wind_direction( data_in['u'] * units('m/s'), data_in['v'] * units('m/s')).magnitude
    ww3 = 0.0
    rh3  = relative_humidity_from_specific_humidity( pres3 * units.hPa, temp3 * units.degK, data_in['q'] *units('kg/kg')).to('percent').magnitude # q in kg/kg to g/kg
    vapmr = mixing_ratio_from_specific_humidity( data_in['q'] *units('kg/kg')).to('g/kg').magnitude    # specific to mixing atio
    cldmr = mixing_ratio_from_specific_humidity( data_in['clwc'] *units('kg/kg')).to('g/kg').magnitude   #'clwc : Specific cloud liquid water content, kg kg**-1,'
    rainmr= mixing_ratio_from_specific_humidity( data_in['crwc'] *units('kg/kg')).to('g/kg').magnitude   #'crwc : Specific rain water content, kg kg**-1,'
    icemr = mixing_ratio_from_specific_humidity( data_in['ciwc'] *units('kg/kg')).to('g/kg').magnitude  #'ciwc : Specific cloud ice water content, kg kg**-1,'
    snowmr= mixing_ratio_from_specific_humidity( data_in['cswc'] *units('kg/kg')).to('g/kg').magnitude   #'cswc : Specific snow water content, kg kg**-1,'
    grpmr = 0.0
    
    # elev layer calc
    presf = (af)*(p0)+  np.einsum('i,jkl->jkli', bf, data_in['sp'])
    dens = pres3*100/( rdwrf*temp3 * (1+rvwrf*vapmr/1000/rdwrf))  # ok
    zf =  giwrf *(presf[:,:,:,:-1] - presf[:,:,:,1:])/dens
    zf = np.cumsum( zf, axis=3 ) + np.concatenate([np.expand_dims(data_in['orog'],3)]*levels,axis=3)
    zf = np.insert(zf,0, data_in['orog'],axis=3)
    elev3 = (zf[:,:,:,:-1]+zf[:,:,:,1:])/2
    
    formatted_pres3 = np.char.mod('%4.0f', pres3.flatten())
    formatted_elev3 = np.char.mod('%6.0f', elev3.flatten())
    formatted_temp3 = np.char.mod('%6.1f', temp3.flatten())
    formatted_wd3 = np.char.mod('%4.0f', wd3.flatten())
    formatted_ws3 = np.char.mod('%5.1f', ws3.flatten())
    formatted_ww3 = np.char.mod('%6.2f', [ww3]*(nx*ny*hours*levels))
    formatted_rh3 = np.char.mod('%3.0f', rh3.flatten())
    formatted_vapmr = np.char.mod('%5.2f', vapmr.flatten())
    formatted_cldmr = np.char.mod('%6.3f', cldmr.flatten())
    formatted_rainmr = np.char.mod('%6.3f', rainmr.flatten())
    formatted_icemr = np.char.mod('%6.3f', icemr.flatten())
    formatted_snowmr = np.char.mod('%6.3f', snowmr.flatten())
    formatted_grpmr = np.char.mod('%6.3f', [grpmr]*(nx*ny*hours*levels))
    
    # Combine all formatted strings using np.char.add
    formatted_rows3d = np.char.add(
        np.char.add(
            np.char.add(
                np.char.add(
                    np.char.add(
                        np.char.add(
                            np.char.add(
                                np.char.add(
                                    np.char.add(
                                        np.char.add(
                                            np.char.add(
                                                np.char.add(
                                                    np.char.add(
                                                        formatted_pres3,
                                                        formatted_elev3
                                                    ),
                                                    formatted_temp3
                                                ),
                                                formatted_wd3
                                            ),
                                            formatted_ws3
                                        ),
                                        formatted_ww3
                                    ),
                                    formatted_rh3
                                ),
                                formatted_vapmr
                            ),
                            formatted_cldmr
                        ),
                        formatted_rainmr
                    ),
                    formatted_icemr
                ),
                formatted_snowmr
            ),
            formatted_grpmr
        ),
        "\n"
    )
       
    rows3d_reshaped = formatted_rows3d.reshape(len(formatted_rows2d), levels)
    combined = np.column_stack((formatted_rows2d[:, None], rows3d_reshaped)).flatten()
    
    headers_txt ='\n'.join([header,''.join(grid_desc)])
    bulk_data_txt =''.join( combined)
    out_txt = '\n'.join([headers_txt,bulk_data_txt])
    print('DATA preparing time {} s '.format(  ( datetime.now() -starttime).seconds ))
    starttime =  datetime.now()
    with open(f"{path_output}/csv/{date_to_proc.year}/sr-{date_to_proc.strftime('%Y%m%d')}_24h.m3d", "w") as text_file:
        text_file.write(out_txt)
    print('Writing time {} s '.format(  ( datetime.now() -starttime).seconds ))

########### RUN PART
totalstarttime =  datetime.now()
for n in list(range(ndays)):
    date_to_proc = start_date + timedelta( days =n)
    print(date_to_proc)

    files = get_files( date_to_proc, hours)
    data_in = get_data( files,cutter, names2d, names3d,levels,max_lvl)

    if prepare_csv == True: make_csv(date_to_proc)
    
    if prepare_nc == True:  make_nc(date_to_proc)
    
    if tar_file==True:
        print('Taring file')
        subprocess.call(['tar', '--remove-files', '-czvf', f'{path_output}/csv/{date_to_proc.year}/sr-{date_to_proc.strftime("%Y%m%d")}_24h.tar.gz', f'{path_output}/csv/{date_to_proc.year}/sr-{date_to_proc.strftime("%Y%m%d")}_24h.m3d'])
        subprocess.call(['chmod','770',f'{path_output}/csv/{date_to_proc.year}/sr-{date_to_proc.strftime("%Y%m%d")}_24h.tar.gz']) 
    print('Total time {} s '.format(  ( datetime.now() -totalstarttime).seconds ))
    time.sleep(sleep_day)

