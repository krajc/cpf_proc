#!/users/p6065/anaconda3/envs/supergeo/bin/python


# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 15:16:23 2019

Skript vykresluje meteorologicke polia z CALMETu, ktore su nacitavane z .nc suboru, predtym
vyprodukovaneho v import_calmet_to_xarray.py

@author: p2993
"""
import sys
sys.path.append('/users/p2993/python/libs')
import plot_conc_v3

import os
import subprocess

import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.io.img_tiles import OSM
import pandas as pd

crsLCC = plot_conc_v3.crsLCC

domname = plot_conc_v3.domname
lcc = ccrs.LambertConformal(central_longitude=crsLCC['lon_0'], central_latitude=crsLCC['lat_0'],
                            standard_parallels=(crsLCC['lat_1'], crsLCC['lat_2']), 
                            false_easting=crsLCC['x_0'])

year = 2024
domena = "banskabystrica"
dom = "banskabystrica"
spcs = ['mht','stab', 'wspeed']

units = {'mht':'Mixing height (m)', 'stab':'Static stability','wspeed':'Wind speed (m/s)'}
names = {'mht':'Mixing height', 'stab':'Static stability', 'wspeed': 'Horizontal wind'}


pth = f"/data/oko/krajc/data_cpf/prtmet/{year}/{dom}"
plotdir = f"{pth}/pics"
if not os.path.exists(plotdir):
    os.makedirs(plotdir)
xds = xr.open_dataset(f"{pth}/2D-{domena}-{year}.nc")
xd4 = xr.open_dataset(f"{pth}/4D-{domena}-{year}.nc")
xd4['vspeed'] = np.sqrt(np.square(xd4['u'])+np.square(xd4['v']))
levels = xd4.coords['z'].values
# Wind level to be plotted:
level = levels[0]

# Epizoda:
start, end = f"{year}-11-24 00:00:00", f"{year}-11-26 00:00:00"
xdss = xds.sel(times=slice(start, end))
xd4s = xd4.sel(times=slice(start, end))

# Staticke parametre kreslenia:
extent = plot_conc_v3.get_lalo_extent_from_xarray(xds)
mapsource = OSM()

plt.rcParams['figure.figsize'] = 10, 10* xds.mht.shape[1]/xds.mht.shape[2]
plt.rcParams.update({'font.size': 16})
plt.rcParams.update({'xtick.labelsize': 16})
plt.rcParams.update({'ytick.labelsize': 16}) 

# Chcem, aby bola konstantna skala rychlosti vetra:
norm = colors.Normalize(vmin=0,vmax=8)

#norm = colors.LogNorm(vmin=0.1,vmax=14)
ticks = list(range(8))
ticks.append(14)
density = 4             # Vector density (1 = each gridbox plotted)

def plot_wind(u, v, wsp, label, figname, figtitle, norm, ticks, density):
    
    # Interpolacia zloziek rychlosti do drsnejsieho gridu: 
    nx = np.linspace(u.x[0], u.x[-1],int(u.shape[1]/density))
    ny = np.linspace(u.y[0], u.y[-1],int(u.shape[0]/density))
    ui = u.interp(x=nx, y=ny)
    vi = v.interp(x=nx, y=ny)
    wspi = wsp.interp(x=nx, y=ny)
    # Chcem aby boli dlzky sipok rovnake, rychlost vetra bude iba farbou:
    ui = ui/wspi
    vi = vi/wspi

    ax = plt.axes(projection=lcc)
    ax.set_extent(extent)
    ax.add_image(mapsource, 13, interpolation='bilinear')
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
    #a = C.plot.pcolormesh( alpha = 0.5, cmap=cmap,linewidth=0, antialiased=True,add_colorbar=False)
    #a = wsp.plot(ax=ax, alpha=0.5, xticks=[], yticks=[], add_labels=None, add_colorbar=False)
    
    a = ax.quiver(nx, ny, ui, vi, wspi, scale=4, scale_units='inches', cmap='gist_rainbow', 
                  norm=norm, headlength=6, headwidth=5)
    plt.colorbar(a,label=label, orientation="vertical", ticks=ticks, format='%.0f',shrink=0.75)
    #ax.barbs(nx, ny, ui, vi, length=5)
    plt.tight_layout()
    
    plt.savefig(figname, dpi=100, bbox_inches='tight')
    plt.show()

def plot_windb(u, v, wsp, label, figname, figtitle, norm, ticks, density):
    
    # Interpolacia zloziek rychlosti do drsnejsieho gridu: 
    nx = np.linspace(u.x[0], u.x[-1],int(u.shape[1]/density))
    ny = np.linspace(u.y[0], u.y[-1],int(u.shape[0]/density))
    ui = u.interp(x=nx, y=ny)
    vi = v.interp(x=nx, y=ny)
    wspi = wsp.interp(x=nx, y=ny)
    
    ax = plt.axes(projection=lcc)
    ax.set_extent(extent)
    ax.add_image(mapsource, 13, interpolation='bilinear')
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
    
    ax.barbs(nx, ny, ui, vi, length=5)
    plt.tight_layout()
    
    plt.savefig(figname, dpi=100, bbox_inches='tight')
    plt.show()    

def plot_scalar(par, label, figname, figtitle):
    ax = plt.axes(projection=lcc)
    ax.set_extent(extent)
    ax.add_image(mapsource, 13, interpolation='bilinear')
    ax.set_title(figtitle, fontdict={'fontsize': '20', 'fontweight' : '4'})
    a = par.plot(ax=ax, alpha=0.5, xticks=[], yticks=[],  add_labels=None, 
                 add_colorbar=False, cmap='rainbow_r', linewidth=0, antialiased=True)
    plt.colorbar(a,label=label, orientation="vertical", shrink=0.75)
    plt.tight_layout()
    
    plt.savefig(figname, dpi=100, bbox_inches='tight')
    plt.show()

def plot_wind_profile (u, v, wsp, label, figname, figtitle):
    
    #### DOROBIT (pozn: toto je uz urobene v inom skripte) ###
    
    plt.tight_layout()
    
    plt.savefig(figname, dpi=100, bbox_inches='tight')
    plt.show()    

def animate(spc, rng, gifname, level):
    imstring = ""
    for i in rng:
        imstring = imstring + f" \'{spc}-level{level}-{str(i)}.png\'"
    os.chdir(f'{pth}/pics')
    subprocess.call("convert -delay 150 {} {}".format(imstring, gifname), shell=True)  
    
spc = 'wspeed'

# Terminy ktore chceme zobrazit (hodiny dna)
tt = ['00', '06', '14', '21']

tt = list(map(lambda x: str(f'{x:02d}'), range(24)))

# Kreslenie skalarov aj vektorov:
for time in xdss.coords['times'].values[:24]:
    
    if str(time)[11:13] in tt:
        
        if spc != 'wspeed':
            figtitle = f"Time: {time}"
            figname = f"{pth}/pics/{spc}-{time}.png"
            plot_scalar(xdss[spc].sel(times=time), units[spc], figname,figtitle)
        else:
            figtitle = f"Time: {str(time)[11:13]}, Level: {level}"
            figname = f"{pth}/pics/{spc}-lev{level}-T{str(time)[11:13]}.png"
            # Selekcia terminu
            xu = xd4s.u.sel(times=time, z=level)
            xv = xd4s.v.sel(times=time, z=level)
            vsp = xd4s.vspeed.sel(times=time, z=level)
            
            plot_wind (xu, xv, vsp, units[spc], figname, figtitle, norm, ticks, density)
            

'''  
animate funkciu treba upravit, nema zmysel robit movie na dynamickej skale. Musela by sa 
zjednotit. Potom by ale zasa vyzerali zle jednotive obrazky
      
day = str(rng[0])
if spc != 'wspeed':
    lev = 0
else:
    lev = level
gifname = "{}/movie-{}-level{}-{}.gif".format(pth, spc, lev, day[:10])
animate(spc, rng, gifname, lev )





#xds.coords['times'] 
#xds.coords['y'] 
#xds.coords['x']
#xds.attrs['domain'] 
#xds.attrs['projinfo'] 


Kedze neviem ako dosiahnut aby sa zakazdym nestahovala mapa z cartopy, myslienka bola uchovat 
mapku ako png a potom ju natiahnut ako obrazok pomocou imshow. (Tu som nasla ako by sa to asi
dalo urobit https://stackoverflow.com/questions/58247868/
how-can-i-plot-a-png-image-on-a-cartopy-basemap-in-a-special-projection).
Mam vsak problem ze neviem uchovat image bez bieleho pasika a cierneho ramika. aj podla google
sa zda ze to nie je az take trivialne. TREBA DORIESIT

figpath = "/data/oko/krajc/prtmet/bratislava250/mapka.png"
ax = plt.axes(projection=lcc)
ax.set_extent(extent)
ax.add_image(mapsource, 13, interpolation='bilinear')

ax.axis('off')
plt.savefig(figpath, dpi=300)




# Denne priemery:
xad = xa.groupby('times.dayofyear').mean('times')

# Plotting - 1 bod casovy rad:
xad1 = xad.sel(y=109375,x=254875)
xad1.plot()
'''

