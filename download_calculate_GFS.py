#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Brad W Vick
# Created Date: 11/8/2018
# =============================================================================
"""
    The Module is designed to be the driver for downloading GFS GRB files from
    the web.  It will then aggregate the GRB files into daily netCDF files.

    It will do this in a loop for each day in a given date range
    (startDate, endDate).

    The module uses wget to download the files.

    The website that holds these GRB files does have indexing so he module will
    build a txt file containing all the file names to download for each day
    and wget will use that txt file to download all the files.

    The module also shells out to the os to perform the daily aggregation

    The files are located at https://nomads.ncdc.noaa.gov/data/gfs4/YYYYMM/
    The naming convention for the files is gfs4_YYYYMMDD_HHHH_HHH.grb2
    Where
        YYYYY = year
        MM = Month
        DD = Day
        HHHH = 6 hour average interval (0000, 0600, 1200, 1800)
        HHH = 3 hour forcaste interval (000, 003, 003, ....384)

 """
from datetime import date, timedelta
import os
import gc
import common

startDate = date(2018, 1, 1)
endDate = date(2018, 1, 1)
myDate = startDate

#loop over dates from startDate to endDate
while myDate <= endDate:
    #split out the parts of the year
    year = ("{date.year:04}".format(date=myDate))
    month = ("{date.month:02}".format(date=myDate))
    day = ("{date.day:02}".format(date=myDate))

    #get current path
    fullPath = os.path.dirname(os.path.abspath(__file__)) + common.GFSpath

    #call wget to download files for given year/day
    #create a filelist.txt file to contain the files that we need to download
    if os.path.exists("filelist.txt"):
        os.remove("filelist.txt")
    url_list = open("filelist.txt", "w")

    #populate filelist
    #outer loop is for the 6 hour intervals (0000, 0600, 1200, 1800)
    for i in range(4):
        #inner loop for the 3 hour forecast intervals (000, 003, 006, ....384)
        for j in range(129):
            filename = 'gfs_4_' + year + month + day + '_' + str(i*6).zfill(2) + '00_' + str(j*3).zfill(3) + '.grb2'
            url_list.write('https://nomads.ncdc.noaa.gov/data/gfs4/' + year + month + '/' + year + month + day  + '/' + filename + '\n')

    url_list.close()

    #call wget to get all files in filelist.xt
    #os.system('wget -x -i filelist.txt')

    #create daily averages and output netCDF file
    #loop over all forecast intervals for the given day (000, 003, 006, ....384)
    for j in range(129):
        os.system('python -c "import hourly_to_daily_GFS; hourly_to_daily_GFS.hourly_to_daily_one_day(\'' + fullPath + '\',\'' + year + '\',\'' + month + '\',\'' + day + '\',\'' + str(j*3).zfill(3) + '\')"')
        gc.collect()
    myDate += timedelta(days=1)