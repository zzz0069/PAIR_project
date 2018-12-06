#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Brad W Vick
# Created Date: 11/26/2018
# =============================================================================
"""
    The Module contains a set of functions for querying data from the daily
    GFS netCDF files

    GFS data is future forecasting data

    Each function has a docstring describing the query it performs

    variables included in the NLDAS netCDF file:
        Name                        Description                             Units
        APCP_P8_L1_GLL0_acc6h       Total Precipitation                     kg/m^2
        RH_P0_L200_GLL0             Avg Relative Humidity                   %
        AVG_MAX_MIN_TMP_P0_L1_GLL0  Avg of Min/Max Temp                     k
        MAX_RH_P0_L200_GLL0         Maximum relative humidity               %
        MIN_RH_P0_L200_GLL0         Minimum specific humidity               %
        MAX_TMP_P0_L1_GLL0          Maximum temperature                     k
        MIN_TMP_P0_L1_GLL0          Minimum temperature                     k
        UGRD_P0_L104_GLL0           Avg u-component of wind                 m/s
        VGRD_P0_L104_GLL0           Avg v-component of wind                 m/s
        WIND_SPEED                  Avg Wind Speed                          m/s
        DPT_P0_L103_GLL0            Dew Point Temperature                   k
        DSWRF_P8_L1_GLL0_avg6h      Downward shortwave radiation            W.m-2
        lat_0                       Lattitude                               radians
        lon_0                       Longitude                               radians

 """

from datetime import date, timedelta
import os
import numpy as np
from netCDF4 import Dataset
from pyeto import convert
import common

def getfilename(querydate, forecastinterval):
    """
    Get a GFS netCDF filename

    Will return the name of an GFS netCDF file based on the supplied date and forecast interval (hours)

    Parameters
    ----------
    querydate : date
        date for the GFS file
    forecastinterval : int
        number of hours in the future to forecast

    Returns
    -------
    str
        GFS netCDF filename

    """
    fullPath = os.path.dirname(os.path.abspath(__file__)) + common.netCDFpath

    #split out the parts of the year
    year = ("{date.year:04}".format(date=querydate))
    month = ("{date.month:02}".format(date=querydate))
    day = ("{date.day:02}".format(date=querydate))
    hour = str(forecastinterval).zfill(3)

    fileName = fullPath + "GFS_" + year + month + day + "_" + hour + ".nc"

    return fileName


def getfilenames(querydate, days):
    """
    Get an array of GFS netCDF filename

    Will return a list of GFS netCDF file names based on the supplied start date and number of days forecast

    Parameters
    ----------
    querystartdate : date
        start date date for the NLDAS files
    days : int
        number of days to forecast

    Returns
    -------
    str()
        an array of GFS netCDF filenames

    """
    file_name_list = []
    fullPath = os.path.dirname(os.path.abspath(__file__)) + common.netCDFpath

    #split out the parts of the year
    year = ("{date.year:04}".format(date=querydate))
    month = ("{date.month:02}".format(date=querydate))
    day = ("{date.day:02}".format(date=querydate))

    for i in range(1, days):
        hour = str(i * 24).zfill(3)
        fileName = fullPath + "GFS_" + year + month + day + "_" + hour + ".nc"
        file_name_list.append(fileName)

    return file_name_list


def queryFileSingleDateRectangle(querydate, forecastinterval, variable, lat_bounds, lon_bounds):
    """
    Query for a GFS variable, single date/forecast interval, rectanglar area

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date to query
    forecastinterval : int
        number of hours in the future to forecast
    variable : str
        variable to query from the netCDF file
    lat_bounds : int[]
        an array with to variables to represent the lower and upper bounds
        for lat in radians
    lon_bounds : int[]
        an array with to variables to represent the lower and upper bounds
        for lon in radians

    Returns
    -------
    tuple[]
        0 index is a tuple of lats included in the query
        1 index is a tuple of lons included in the query
        2 index is a tuple of numeric results

    """
    ds = Dataset(getfilename(querydate, forecastinterval))
    returnTuple = []

    #grab the lat and lon variable arrays
    lats = ds.variables['lat_0'][:]
    lons = ds.variables['lon_0'][:]
    lons = np.mod(lons - 180.0, 360.0) - 180.0


    #calculate the lower and upper indicies of the lat array
    latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
    latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))
    if latupperindex<latlowerindex:
        latlowerindex, latupperindex = latupperindex, latlowerindex

    #calculate the lower and upper indices of the lon array
    lonlowerindex = np.argmin(np.abs(lons - lon_bounds[0]))
    lonupperindex = np.argmin(np.abs(lons - lon_bounds[1]))

    #populate the tuple of lats included in the query
    returnLatTuple = []
    for i in range(latlowerindex, latupperindex):
        returnLatTuple.append(lats[i])

    #populate the tuple of lons included in the query
    returnLonTuple = []
    for i in range(lonlowerindex, lonupperindex):
        returnLonTuple.append(lons[i])

    #grab the dataset for the given variable name and rectangle
    dataSubset = ds.variables[variable][latlowerindex:latupperindex, lonlowerindex:lonupperindex]

    returnTuple.append(returnLatTuple)
    returnTuple.append(returnLonTuple)
    returnTuple.append(dataSubset)


    return returnTuple

def queryFileSingleDateSingleCoordinate(querydate, forecastinterval, variable, lat, lon):
    """
    Query for a GFS variable, single date/forecast, single coordinate

    will return a single values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date to query
    forecastinterval : int
        number of hours in the future to forecast
    variable : str
        variable to query from the netCDF file
    lat : int
        lat in radians
    lon : int
        lon in radians

    Returns
    -------
    float
        result for the query

    """
    ds = Dataset(getfilename(querydate, forecastinterval))

    #grab the lat and lon variable arrays
    lats = ds.variables['lat_0'][:]
    lons = ds.variables['lon_0'][:]
    lons = np.mod(lons - 180.0, 360.0) - 180.0

    #calculate the lower and upper indicies of the lat array
    latindex = np.nonzero(lats == lat)[0][0]

    #calculate the lower and upper indices of the lon array
    lonindex = np.nonzero(lons == lon)[0][0]

    #grab the dataset for the given variable name and rectangle
    dataSubset = ds.variables[variable][latindex, lonindex]

    return dataSubset

def queryFileAggregateDateRangeRectangle(querydate, days, variable, aggregatefunction, lat_bounds, lon_bounds):
    """
    Query for a GFS variable, date, number of forecast days, rectanglar area

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date for query
    days : int
        number of days to forecast
    variable : str
        variable to query from the netCDF file
    aggregatefunction : str
        function for aggregating th data possible values: min, max, avg
    lat_bounds : int[]
        an array with to variables to represent the lower and upper bounds
        for lat in radians
    lon_bounds : int[]
        an array with to variables to represent the lower and upper bounds
        for lon in radians

    Returns
    -------
    tuple[]
        0 index is a tuple of lats included in the query
        1 index is a tuple of lons included in the query
        2 index is a tuple of numeric results

    """

    file_name_list = getfilenames(querydate, days)

    aggregate = []
    returnTuple = []

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_0'][:]
        lons = ds.variables['lon_0'][:]
        lons = np.mod(lons - 180.0, 360.0) - 180.0

        #calculate the lower and upper indicies of the lat array
        latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
        latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))
        if latupperindex<latlowerindex:
            latlowerindex, latupperindex = latupperindex, latlowerindex

        #calculate the lower and upper indices of the lon array
        lonlowerindex = np.argmin(np.abs(lons - lon_bounds[0]))
        lonupperindex = np.argmin(np.abs(lons - lon_bounds[1]))

        #populate the tuple of lats included in the query
        returnLatTuple = []
        for i in range(latlowerindex, latupperindex):
            returnLatTuple.append(lats[i])

        #populate the tuple of lons included in the query
        returnLonTuple = []
        for i in range(lonlowerindex, lonupperindex):
            returnLonTuple.append(lons[i])

        #grab the dataset for the given variable name and rectangle
        dataSubset = ds.variables[variable][latlowerindex:latupperindex, lonlowerindex:lonupperindex]

        if aggregate == []:
            aggregate = dataSubset
        else:
            if aggregatefunction  == "max":
                aggregate = np.maximum(dataSubset, aggregate)
            elif aggregatefunction == "min":
                aggregate = np.minimum(dataSubset, aggregate)
            elif aggregatefunction == "avg":
                aggregate += dataSubset

    if aggregatefunction == "avg":
        aggregate = aggregate / filecount

    returnTuple.append(returnLatTuple)
    returnTuple.append(returnLonTuple)
    returnTuple.append(aggregate)

    return returnTuple


def queryFileAggregateDateRangeSingleCoordinate(querydate, days, variable, aggregatefunction, lat, lon):
    """
    Query for a GFS variable, date, number of forecast days, single coordinate

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date for query
    days : int
        number of days to forecast
    variable : str
        variable to query from the netCDF file
    aggregatefunction : str
        function for aggregating th data possible values: min, max, avg
    lat : int
        lat in radians
    lon : int
        lon in radians

    Returns
    -------
    float
        result for the query

    """

    file_name_list = getfilenames(querydate, days)

    aggregate = 0

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_0'][:]
        lons = ds.variables['lon_0'][:]
        lons = np.mod(lons - 180.0, 360.0) - 180.0

        # calculate the lower and upper indicies of the lat array
        latindex = np.nonzero(lats == lat)[0][0]

        # calculate the lower and upper indices of the lon array
        lonindex = np.nonzero(lons == lon)[0][0]

        # grab the dataset for the given variable name and rectangle
        dataSubset = ds.variables[variable][latindex, lonindex]

        if aggregate == 0:
            aggregate = dataSubset
        else:
            if aggregatefunction  == "max":
                aggregate = np.maximum(dataSubset, aggregate)
            elif aggregatefunction == "min":
                aggregate = np.minimum(dataSubset, aggregate)
            elif aggregatefunction == "avg":
                aggregate += dataSubset

    if aggregatefunction == "avg":
        aggregate = aggregate / filecount

    return aggregate


def queryFileConsecutiveDaysDateRangeRectangle(querydate, days, variable, aggregatefunction, lat_bounds, lon_bounds):
    """
    Query for number of consecutive days for a given GFS variable, date, number of forecast days, cunction, rectanglar area

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date for query
    days : int
        number of days to forecast
    variable : str
        variable to query from the netCDF file
    aggregatefunction : str
        function for calculating concecutive days, possible values: cold, hot, wet, dry
    lat_bounds : int[]
        an array with to variables to represent the lower and upper bounds
        for lat in radians
    lon_bounds : int[]
        an array with to variables to represent the lower and upper bounds
        for lon in radians

    Returns
    -------
    tuple[]
        0 index is a tuple of lats included in the query
        1 index is a tuple of lons included in the query
        2 index is a tuple of numeric results

    """

    file_name_list = getfilenames(querydate, days)

    aggregate = []
    returnTuple = []
    firstLoop = 0

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_0'][:]
        lons = ds.variables['lon_0'][:]
        lons = np.mod(lons - 180.0, 360.0) - 180.0

        #calculate the lower and upper indicies of the lat array
        latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
        latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))
        if latupperindex<latlowerindex:
            latlowerindex, latupperindex = latupperindex, latlowerindex

        #calculate the lower and upper indices of the lon array
        lonlowerindex = np.argmin(np.abs(lons - lon_bounds[0]))
        lonupperindex = np.argmin(np.abs(lons - lon_bounds[1]))

        #populate the tuple of lats included in the query
        returnLatTuple = []
        for i in range(latlowerindex, latupperindex):
            returnLatTuple.append(lats[i])

        #populate the tuple of lons included in the query
        returnLonTuple = []
        for i in range(lonlowerindex, lonupperindex):
            returnLonTuple.append(lons[i])

        #grab the dataset for the given variable name and rectangle
        dataSubset = ds.variables[variable][latlowerindex:latupperindex, lonlowerindex:lonupperindex]

        #initialize return aggregate
        if firstLoop == 0:
            firstLoop = 1
            rows = dataSubset.shape[0]  # calculate number of rows in array
            cols = dataSubset.shape[1]  # calculate number of columns in array
            aggregate = np.zeros((rows,cols))

        rows = aggregate.shape[0]  # calculate number of rows in array
        cols = aggregate.shape[1]  # calculate number of columns in array
        for i in range(0, rows):
            for j in range(0, cols):

                if aggregatefunction == "hot":
                    dataSubset[i, j] = convert.kelvin2celsius(dataSubset[i, j])
                    if dataSubset[i, j] > common.hotTemp:
                        aggregate[i, j] += 1
                    else:
                        aggregate[i, j] = 0

                elif aggregatefunction == "cold":
                    dataSubset[i, j] = convert.kelvin2celsius(dataSubset[i, j])
                    if dataSubset[i, j] < common.coldTemp:
                        aggregate[i, j] += 1
                    else:
                        aggregate[i, j] = 0
                elif aggregatefunction == "wet":
                    if dataSubset[i, j] > common.wetPrecip:
                        aggregate[i, j] += 1
                    else:
                        aggregate[i, j] = 0

                elif aggregatefunction == "dry":
                    if dataSubset[i, j] < common.dryPrecip:
                        aggregate[i, j] += 1
                    else:
                        aggregate[i, j] = 0

    returnTuple.append(returnLatTuple)
    returnTuple.append(returnLonTuple)
    returnTuple.append(aggregate)

    return returnTuple


def queryFileConsecutivedDateRangeSingleCoordinate(querydate, days, variable, aggregatefunction, lat, lon):
    """
    Query for number of consecutive days for a given GFS variable, date, number of forecast days, cunction, single coordinate

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date for query
    days : int
        number of days to forecast
    variable : str
        variable to query from the netCDF file
    aggregatefunction : str
        function for calculating concecutive days, possible values: cold, hot, wet, dry
    lat : int
        lat in radians
    lon : int
        lon in radians

    Returns
    -------
    float
        result for the query

    """

    file_name_list = getfilenames(querydate, days)

    aggregate = 0

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_0'][:]
        lons = ds.variables['lon_0'][:]
        lons = np.mod(lons - 180.0, 360.0) - 180.0

        # calculate the lower and upper indicies of the lat array
        latindex = np.nonzero(lats == lat)[0][0]

        # calculate the lower and upper indices of the lon array
        lonindex = np.nonzero(lons == lon)[0][0]

        # grab the dataset for the given variable name and rectangle
        dataSubset = ds.variables[variable][latindex, lonindex]

        if aggregatefunction == "hot":
            dataSubset = convert.kelvin2celsius(dataSubset)
            if dataSubset>common.hotTemp:
                aggregate += 1
            else:
                aggregate = 0

        elif aggregatefunction == "cold":
            dataSubset = convert.kelvin2celsius(dataSubset)
            if dataSubset<common.coldTemp:
                aggregate += 1
            else:
                aggregate = 0

        elif aggregatefunction == "wet":
            if dataSubset>common.wetPrecip:
                aggregate += 1
            else:
                aggregate = 0

        elif aggregatefunction == "dry":
            if dataSubset<common.dryPrecip:
                aggregate += 1
            else:
                aggregate = 0


    return aggregate



lat_bnds = [20.0, 26.0]
lon_bnds = [-110, -102]

#print(queryFileSingleDateRectangle(date(2018, 1, 1), 24, 'MAX_TMP_P0_L1_GLL0', lat_bnds, lon_bnds))
#print(queryFileSingleDateSingleCoordinate(date(2018, 1, 1), 24, 'MAX_TMP_P0_L1_GLL0', 25, -107))

#print(queryFileAggregateDateRangeRectangle(date(2018, 1, 1), 3, 'AVG_MAX_MIN_TMP_P0_L1_GLL0', 'avg', lat_bnds, lon_bnds))

#print(queryFileAggregateDateRangeSingleCoordinate(date(2018, 1, 1), 3, 'MAX_TMP_P0_L1_GLL0', 'min', 25, -107))


#print(queryFileConsecutiveHotColdDateRangeSingleCoordinate(date(2018, 1, 1), 5, 'AVG_MAX_MIN_TMP_P0_L1_GLL0', 'cold', 25, -107))


print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), 5, 'AVG_MAX_MIN_TMP_P0_L1_GLL0', 'hot', lat_bnds, lon_bnds))
print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), 5, 'AVG_MAX_MIN_TMP_P0_L1_GLL0', 'cold', lat_bnds, lon_bnds))
print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), 5, 'APCP_P8_L1_GLL0_acc6h', 'wet', lat_bnds, lon_bnds))
print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), 5, 'APCP_P8_L1_GLL0_acc6h', 'dry', lat_bnds, lon_bnds))