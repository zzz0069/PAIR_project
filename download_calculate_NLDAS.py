#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Brad W Vick
# Created Date: 11/7/2018
# =============================================================================
"""
    The Module is designed to be the driver for downloading NLDAS GRB files from
    the web.  It will then aggregate the GRB files into daily netCDF files.

    It will do this in a loop for each day in a given date range
    (startDate, endDate).

    The module uses wget to download the files.

    The website that holds these GRB files has indexing so we can download
    all files in a single directory at once

    The files are located at https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/YYYY/DDD
    The naming convention for the files is NLDAS_FORA0125_H.AYYYYMMDD.HHHH.002.grb
    Where
        YYYYY = year
        MM = Month
        DDD = Julian day of year
        HHHH = 1 hour average interval (0000, 0100, 0200, ....2300)

 """

#files required for wget
#.netrc - need to update with username/password to NLDAS data website
#.usr_cookies

import hourly_to_daily_NLDAS
from datetime import date, timedelta
import os
import common

startDate = date(2018, 1, 1)
endDate = date(2018, 1, 3)
myDate = startDate

#loop over dates from startDate to endDate
while myDate <= endDate:
    #split out the parts of the year
    year = ("{date.year:04}".format(date=myDate))
    tt = myDate.timetuple()
    julianday = format(tt.tm_yday, '03')

    # get current path
    fullPath = os.path.dirname(os.path.abspath(__file__)) + common.NLDASpath
    #call wget to download files for given year/day
    os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies -np -r --content-disposition https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/' + year + '/' + julianday + '/ -A grb')

    #create daily averages and output netCDF file
    hourly_to_daily_NLDAS.hourly_to_daily_one_day(fullPath, year, julianday)
    myDate += timedelta(days=1)
