#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 11:43:49 2022

@author: p2993
"""

__lstfile__
__concfile__
__nmetdat__
__nvoldat__
__metdatstring__
__voldat__
__metrunswitch__
__startyear__
__startmonth__
__startday__
__starthour__
__endyear__
__endmonth__
__endday__
__endhour__
__nspec__
__nse__
__mwet__
__specieslist__
__speciestable__
__mnx__
__mny__
__mnz__
__reskm__
__mxorig__
__myorig__
__llx__
__lly__
__urx__
__ury__
__meshdens__
__ivet__
__outoptstring__
__nvl1__
__nsvl1__ ...  pocet source/species comb. pre scaling factors
__nsvl2__ ... pocet volemarb.dat
__nsvl2string__ ... nazvy volemarb.dat
__nrec__
__ngrp__ ... pocet recepor groups
__grpstring__
__recstring__

def make_groupstring(grplist):
    groupstring = ""
    for name in range(len(grplist)):
        groupstring = groupstring + f'! RGRPNAM =  {name}     !   !END!\n'
    return groupstring        
        
