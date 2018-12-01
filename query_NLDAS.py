#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Brad W Vick
# Created Date: 11/26/2018
# =============================================================================
"""
    The Module contains a set of functions for querying data from the daily
    NLDAS netCDF files

    Each function has a docstring describing the query it performs

    variables included in the NLDAS netCDF file:
        Name                        Description                             Units
        A_PCP_110_SFC_acc1h         Total Precipitation                     kg/m^2
        AVG_MAX_MIN_TMP_110_HTGL    Avg of Min/Max Temp                     k
        DLWRF_110_SFC               Avg Downward longwave radiation flux    W/m^2
        DSWRF_110_SFC               Avg Downward shortwave radiation flux   W/m^2
        ET                          Avg reference evapotranspiration        mm
        MAX_SPF_H_110_HTGL          Maximum specific humidity               kg/kg
        MIN_SPF_H_110_HTGL          Minimum specific humidity               kg/kg
        MAX_TMP_110_HTGL            Maximum temperature                     k
        MIN_TMP_110_HTGL            Minimum temperature                     k
        PRES_110_SFC                Avg Pressure                            Pa
        U_GRD_110_HTGL              Avg u-component of wind                 m/s
        V_GRD_110_HTGL              Avg v-component of wind                 m/s
        WIND_SPEED                  Avg Wind Speed                          m/s
        lat_110                     Lattitude                               radians
        lon_110                     Longitude                               radians

 """

from datetime import date, timedelta
import os
import numpy as np
from netCDF4 import Dataset
from pyeto import convert
import common


def getfilename(querydate):
    """
    Get a NLDAS netCDF filename

    Will return the name of an NLDAS netCDF file based on the supplied date

    Parameters
    ----------
    querydate : date
        date for the NLDAS file

    Returns
    -------
    str
        NLDAS netCDF filename

    """
    fullPath = os.path.dirname(os.path.abspath(__file__)) + common.netCDFpath

    #split out the parts of the year
    year = ("{date.year:04}".format(date=querydate))
    tt = querydate.timetuple()
    julianday = format(tt.tm_yday, '03')

    fileName = fullPath + "NLDAS_" + year + "_" + julianday + ".nc"

    return fileName


def getfilenames(querystartdate, queryenddate):
    """
    Get an array of NLDAS netCDF filename

    Will return a list of NLDAS netCDF file names based on the supplied date range

    Parameters
    ----------
    querystartdate : date
        start date date for the NLDAS files
    queryenddate : date
        end date date for the NLDAS files

    Returns
    -------
    str()
        an array of NLDAS netCDF filenames

    """
    file_name_list = []
    fullPath = os.path.dirname(os.path.abspath(__file__)) + common.netCDFpath

    mydate = querystartdate

    while mydate <= queryenddate:
        #split out the parts of the year
        year = ("{date.year:04}".format(date=mydate))
        tt = mydate.timetuple()
        julianday = format(tt.tm_yday, '03')

        fileName = fullPath + "NLDAS_" + year + "_" + julianday + ".nc"

        file_name_list.append(fileName)
        mydate += timedelta(days=1)

    return file_name_list


def queryFileSingleDateRectangle(querydate, variable, lat_bounds, lon_bounds):
    """
    Query for a netCDF variable, single date, rectanglar area

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date to query
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
    ds = Dataset(getfilename(querydate))
    returnTuple = []

    #grab the lat and lon variable arrays
    lats = ds.variables['lat_110'][:]
    lons = ds.variables['lon_110'][:]

    #calculate the lower and upper indicies of the lat array
    latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
    latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))

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


def queryFileSingleDateSingleCoordinate(querydate, variable, lat, lon):
    """
    Query for a netCDF variable, single date, single coordinate

    will return a single values for the supplied parameters

    Parameters
    ----------
    querydate : date
        date to query
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
    ds = Dataset(getfilename(querydate))

    #grab the lat and lon variable arrays
    lats = ds.variables['lat_110'][:]
    lons = ds.variables['lon_110'][:]

    #calculate the lower and upper indicies of the lat array
    latindex = np.nonzero(lats == lat)[0][0]

    #calculate the lower and upper indices of the lon array
    lonindex = np.nonzero(lons == lon)[0][0]

    #grab the dataset for the given variable name and rectangle
    dataSubset = ds.variables[variable][latindex, lonindex]

    return dataSubset


def queryFileAggregateDateRangeRectangle(querystartdate, queryenddate, variable, aggregatefunction, lat_bounds, lon_bounds):
    """
    Query for a netCDF variable, date range, rectanglar area

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querystartdate : date
        start date for query
    queryenddate : date
        end date for query
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

    file_name_list = getfilenames(querystartdate, queryenddate)

    aggregate = []
    returnTuple = []

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_110'][:]
        lons = ds.variables['lon_110'][:]

        #calculate the lower and upper indicies of the lat array
        latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
        latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))

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


def queryFileAggregateDateRangeSingleCoordinate(querystartdate, queryenddate, variable, aggregatefunction, lat, lon):
    """
    Query for a netCDF variable, date range, single coordinate

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querystartdate : date
        start date for query
    queryenddate : date
        end date for query
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

    file_name_list = getfilenames(querystartdate, queryenddate)

    aggregate = 0

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_110'][:]
        lons = ds.variables['lon_110'][:]

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


def queryFileConsecutiveDaysDateRangeRectangle(querystartdate, queryenddate, variable, aggregatefunction, lat_bounds, lon_bounds):
    """
    Query for number of consecutive days for a given netCDF variable, date range, cunction, rectanglar area

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querystartdate : date
        start date for query
    queryenddate : date
        end date for query
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

    file_name_list = getfilenames(querystartdate, queryenddate)

    aggregate = []
    returnTuple = []
    firstLoop = 0

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_110'][:]
        lons = ds.variables['lon_110'][:]

        #calculate the lower and upper indicies of the lat array
        latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
        latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))

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


def queryFileConsecutivedDateRangeSingleCoordinate(querystartdate, queryenddate, variable, aggregatefunction, lat, lon):
    """
    Query for number of consecutive days for a given netCDF variable, date range, cunction, single coordinate

    will return a 2d array of values for the supplied parameters

    Parameters
    ----------
    querystartdate : date
        start date for query
    queryenddate : date
        end date for query
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

    file_name_list = getfilenames(querystartdate, queryenddate)

    aggregate = 0

    filecount = 0
    for filename in file_name_list:
        filecount += 1
        ds = Dataset(filename)

        #grab the lat and lon variable arrays
        lats = ds.variables['lat_110'][:]
        lons = ds.variables['lon_110'][:]

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

lat_bnds = [25.0, 26.0]
lon_bnds = [-103, -102]

print(queryFileSingleDateRectangle(date(2018, 1, 1), 'MAX_TMP_110_HTGL', lat_bnds, lon_bnds))
#print(queryFileSingleDateSingleCoordinate(date(2018, 1, 1), 'MAX_TMP_110_HTGL', 25.063, -107.938))

#print(queryFileAggregateDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'avg', lat_bnds, lon_bnds))

#print(queryFileAggregateDateRangeSingleCoordinate(date(2018, 1, 1), date(2018, 1, 3), 'MAX_TMP_110_HTGL', 'min', 25.063, -107.938))


#print(queryFileConsecutiveHotColdDateRangeSingleCoordinate(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'cold', 25.063, -107.938))


#print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'hot', lat_bnds, lon_bnds))
#print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'cold', lat_bnds, lon_bnds))
#print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'A_PCP_110_SFC_acc1h', 'wet', lat_bnds, lon_bnds))
#print(queryFileConsecutiveDaysDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'A_PCP_110_SFC_acc1h', 'dry', lat_bnds, lon_bnds))