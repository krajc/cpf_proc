#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 28 13:45:31 2025

@author: p2993
"""


# In[1]:


import rpy2
print(rpy2.__version__)
from rpy2.robjects.packages import importr
import numpy as np
import pandas as pd
import xarray as xr
from rpy2.robjects import pandas2ri

openair = importr('openair')

import rpy2.robjects as robjects


# In[24]:

aer = xr.open_dataset('/users/p2993/barborka/model_vs_aero_poprad_cubic.nc')
aer10 = aer.sel(z=10.0).to_dataframe()
df = aer10[['wspeed', 'wdir', 'wspeeda', 'wdira']]


# In[25]:


pandas2ri.activate()
r_df = pandas2ri.py2rpy_pandasdataframe(df)
openair.summaryPlot(r_df)


# In[33]:


def displayOpenairPlot(func, figsize=(10,10), res=150, *args, **kwargs):

    """
    Displays openair plots in a notebook inline.
    + func. openair callback.
    + figsize. tuple. figure size
    + res. int. resolution of figure
    + **kwargs. to be passed to func.
    """

    import IPython
    from rpy2.robjects.lib import grdevices

    pixel_per_inch = 0.0104166667
    width, height =figsize[0]/pixel_per_inch, figsize[1]/pixel_per_inch
    with grdevices.render_to_bytesio(grdevices.png, width=width, height=height, res=res) as img:
        plot = func(*args, **kwargs)
    IPython.display.display(IPython.display.Image(data=img.getvalue(), format='png', embed=True))

    return None

# In[35]:


displayOpenairPlot(openair.windRose, mydata=r_df)
displayOpenairPlot(openair.windRose, mydata=r_df)

# In[38]:


displayOpenairPlot(openair.polarPlot, mydata=r_df, pollutant="oz")


# In[39]:


displayOpenairPlot(openair.pollutionRose, mydata=r_df, pollutant="oz")


# In[40]:


#openair.percentileRose(mydata=r_df, pollutant ='oz')
displayOpenairPlot(openair.percentileRose, mydata=r_df, pollutant="oz")


# In[41]:


#openair.calendarPlot(mydata=r_df, pollutant ='oz')
displayOpenairPlot(openair.calendarPlot, mydata=r_df, pollutant="oz")


# In[43]:


#openair.polarAnnulus(mydata=r_df, pollutant ='oz', period='hour')
displayOpenairPlot(openair.polarAnnulus, mydata=r_df, pollutant="oz", period='hour')


# In[45]:


#openair.polarAnnulus(mydata=r_df, pollutant ='oz', period='hour')
displayOpenairPlot(openair.polarAnnulus, mydata=r_df, pollutant="oz", type='season')

