
from datetime import date, timedelta
import os
import Nio
import os
import numpy as np
import glob
import math
from netCDF4 import Dataset
from pyeto import convert

hotTemp = 20 #degrees celcius
coldTemp = 0 #degrees celcius

path = '/netCDF/'


#This function will return the netCDF file name for a given date
def getfilename(querydate):

    fullPath = os.path.dirname(os.path.abspath(__file__)) + path

    #split out the parts of the year
    year = ("{date.year:04}".format(date=querydate))
    tt = querydate.timetuple()
    julianday = format(tt.tm_yday, '03')

    fileName = fullPath + "NLDAS_" + year + "_" + julianday + ".nc"

    return fileName

#This function will return an array of netCDF file names for a date range
def getfilenames(querystartdate, queryenddate):
    file_name_list = []
    fullPath = os.path.dirname(os.path.abspath(__file__)) + path

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

#this function will return a varialbe for a single date for a
#rectangular area represented by upper and lower lat/lon
#lat_bounds and lon_boundsshould be an array with 2 variables in radians [lower value, upper value]
#returns a 2d array
def queryFileSingleDateRectangle(querydate, variable, lat_bounds, lon_bounds):
    ds = Dataset(getfilename(querydate))

    #grab the lat and lon variable arrays
    lats = ds.variables['lat_110'][:]
    lons = ds.variables['lon_110'][:]

    #calculate the lower and upper indicies of the lat array
    latlowerindex = np.argmin(np.abs(lats - lat_bounds[0]))
    latupperindex = np.argmin(np.abs(lats - lat_bounds[1]))

    #calculate the lower and upper indices of the lon array
    lonlowerindex = np.argmin(np.abs(lons - lon_bounds[0]))
    lonupperindex = np.argmin(np.abs(lons - lon_bounds[1]))

    #grab the dataset for the given variable name and rectangle
    dataSubset = ds.variables[variable][latlowerindex:latupperindex, lonlowerindex:lonupperindex]

    return dataSubset

#this function will return a varialbe for a single date for a
#single coordinate represented by  lat/lon
#returns a single value
def queryFileSingleDateSingleCoordinate(querydate, variable, lat, lon):
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


#this function will return the maximuum, minimum, or average of a varialbe for a date range for a
#rectangular area represented by upper and lower lat/lon
#lat_bounds and lon_boundsshould be an array with 2 variables in radians [lower value, upper value]
#aggregatefunction can be max, min, or avg
#returns a 2d array
def queryFileAggregateDateRangeRectangle(querystartdate, queryenddate, variable, aggregatefunction, lat_bounds, lon_bounds):
    file_name_list = getfilenames(querystartdate, queryenddate)

    aggregate = []

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

    return aggregate

#this function will return the maximuum, minimum, or average of a varialbe for a date range for a
#single coordinate represented by  lat/lon
#aggregatefunction can be max, min, or avg
#returns a single value
def queryFileAggregateDateRangeSingleCoordinate(querystartdate, queryenddate, variable, aggregatefunction, lat, lon):
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



#this function will return the consecutive hot or cold days a date range for a
#single coordinate represented by  lat/lon
#aggregatefunction can be hot or cold
#returns a single value
def queryFileConsecutiveHotColdDateRangeSingleCoordinate(querystartdate, queryenddate, variable, aggregatefunction, lat, lon):
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
        dataSubset = convert.kelvin2celsius(dataSubset)

        if aggregatefunction == "hot":
            if dataSubset>=hotTemp:
                aggregate += 1
            else:
                aggregate = 0

        elif aggregatefunction == "cold":
            if dataSubset<=coldTemp:
                aggregate += 1
            else:
                aggregate = 0


    return aggregate

#this function will return the consecutive hot or cold days a date range for a
#rectangular area represented by upper and lower lat/lon
#lat_bounds and lon_boundsshould be an array with 2 variables in radians [lower value, upper value]
#aggregatefunction can be hot or cold
#returns a 2d array
def queryFileConsecutiveHotColdDateRangeRectangle(querystartdate, queryenddate, variable, aggregatefunction, lat_bounds, lon_bounds):
    file_name_list = getfilenames(querystartdate, queryenddate)

    aggregate = []
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

                dataSubset[i, j] = convert.kelvin2celsius(dataSubset[i, j])
                if aggregatefunction == "hot":
                    if dataSubset[i, j] >= hotTemp:
                        aggregate[i, j] += 1
                    else:
                        aggregate[i, j] = 0

                elif aggregatefunction == "cold":
                    if dataSubset[i, j] <= coldTemp:
                        aggregate[i, j] += 1
                    else:
                        aggregate[i, j] = 0


    return aggregate


lat_bnds = [25.0, 26.0]
lon_bnds = [-108, -107]

#print(queryFileSingleDateRectangle(date(2018, 1, 1), 'MAX_TMP_110_HTGL', lat_bnds, lon_bnds))
#print(queryFileSingleDateSingleCoordinate(date(2018, 1, 1), 'MAX_TMP_110_HTGL', 25.063, -107.938))

#print(queryFileAggregateDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'avg', lat_bnds, lon_bnds))

#print(queryFileAggregateDateRangeSingleCoordinate(date(2018, 1, 1), date(2018, 1, 3), 'MAX_TMP_110_HTGL', 'min', 25.063, -107.938))


#print(queryFileConsecutiveHotColdDateRangeSingleCoordinate(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'cold', 25.063, -107.938))


print(queryFileConsecutiveHotColdDateRangeRectangle(date(2018, 1, 1), date(2018, 1, 3), 'AVG_MAX_MIN_TMP_110_HTGL', 'hot', lat_bnds, lon_bnds))