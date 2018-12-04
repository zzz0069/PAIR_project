#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Brad W Vick
# Created Date: 11/8/2018
# =============================================================================
"""
    The Module is used to define constants used throughout the other scripts

 """


hotTemp = 20 #degrees celcius temperature for a day to be considered hot
coldTemp = 0 #degrees celcius temperature for a day to be considered cold
dryPrecip = 0 #amount of rain for a dry day
wetPrecip = 5 #amount of rain for a wet day

altitude = 200 #default altitude for et calculation
#number of lat/long coordinates in the NLDAS file
NLDASLatCount = 224
NLDASLonCount = 464
#number of lat/long coordinates in the GFS file
GFSLatCount = 361
GFSLonCount = 720
HOURS = 24  #hours in day

#path to store netCDF files in
netCDFpath = '/netCDF/'
#path where NLDAS files downloaded from web will be stored in
NLDASpath = '/hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/'
#path where GFS files downnloaded from the web will be stored
GFSpath = '/nomads.ncdc.noaa.gov/data/gfs4/'