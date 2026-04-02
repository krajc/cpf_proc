#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 15:14:23 2026

@author: p2993
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

dom = 'bratislava'
year = 2024
suff='-man'
inpdir = '/data/users/p2993/data_cpf'
rio = f'{inpdir}/rio/{year}/{dom}/minpoint_tseries{suff}.csv'
cmaq = f'{inpdir}/cmaq/{year}/{dom}/cmaq-daily-backg-{dom}-{year}.csv'

def produce_plots(file1, file2):
    # Load the datasets
    # Assumes columns: times, PM10, PM25, NO2
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Convert 'times' to datetime objects
    df1['times'] = pd.to_datetime(df1['times'])
    df2['times'] = pd.to_datetime(df2['times'])

    # Sort by time to ensure lines are drawn correctly
    df1 = df1.sort_values('times')
    df2 = df2.sort_values('times')

    # Prepare Monthly Averages
    # We set 'times' as index to use the resample function easily
    df1_resampled = df1.set_index('times').resample('M').mean().reset_index()
    df2_resampled = df2.set_index('times').resample('M').mean().reset_index()

    pollutants = ['PM10', 'PM25', 'NO2']
    labels = ['RIO', 'CMAQ']
    
    # 1. Plot Daily Concentrations
    fig_daily, axes_d = plt.subplots(3, 1, figsize=(12, 18), sharex=True)
    for i, pol in enumerate(pollutants):
        axes_d[i].plot(df1['times'], df1[pol], label=labels[0], alpha=0.7)
        axes_d[i].plot(df2['times'], df2[pol], label=labels[1], alpha=0.7)
        axes_d[i].set_title(f'Daily Concentration: ${pol}$')
        axes_d[i].set_ylabel('$\mu g/m^3$')
        axes_d[i].legend()
        axes_d[i].grid(True, linestyle='--', alpha=0.6)

    plt.xlabel('Date')
    plt.tight_layout()
    plt.savefig(f'{inpdir}/pics/rio-cmaq-{dom}-{year}-daily.png')
    print("Daily comparison plot saved as 'daily_comparison.png'")

    # 2. Plot Monthly Concentrations
    fig_monthly, axes_m = plt.subplots(3, 1, figsize=(12, 18), sharex=True)
    for i, pol in enumerate(pollutants):
        axes_m[i].plot(df1_resampled['times'], df1_resampled[pol], marker='o', label=labels[0])
        axes_m[i].plot(df2_resampled['times'], df2_resampled[pol], marker='s', label=labels[1])
        axes_m[i].set_title(f'Monthly Average Concentration: ${pol}$')
        axes_m[i].set_ylabel('$\mu g/m^3$')
        axes_m[i].legend()
        axes_m[i].grid(True, linestyle='--', alpha=0.6)
        # Formatting the X-axis for months
        # Locator ensures we get a tick for every month
        axes_m[i].xaxis.set_major_locator(mdates.MonthLocator())
        # Formatter turns the date into "JAN", "FEB", etc.
        axes_m[i].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(f'{inpdir}/pics/rio-cmaq-{dom}-{year}-monthly.png')
    print("Monthly comparison plot saved as 'monthly_comparison.png'")
    
produce_plots(rio, cmaq)
