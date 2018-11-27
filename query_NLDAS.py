
from datetime import date, timedelta
import os
import Nio
import os
import numpy as np
import glob
import math
from netCDF4 import Dataset


path = '/netCDF/'


def getfilename(querydate):

    fullPath = os.path.dirname(os.path.abspath(__file__)) + path

    #split out the parts of the year
    year = ("{date.year:04}".format(date=querydate))
    tt = querydate.timetuple()
    julianday = format(tt.tm_yday, '03')

    fileName = fullPath + "NLDAS_" + year + "_" + julianday + ".nc"

    return fileName

def queryFile(querydate, variable, lat_bnds, lon_bnds):
    ds = Dataset(getfilename(querydate))

    lats = ds.variables['lat_110'][:]
    lons = ds.variables['lon_110'][:]

    latli = np.argmin(np.abs(lats - lat_bnds[0]))
    latui = np.argmin(np.abs(lats - lat_bnds[1]))

    lonli = np.argmin(np.abs(lons - lon_bnds[0]))
    lonui = np.argmin(np.abs(lons - lon_bnds[1]))


    dataSubset = ds.variables[variable][latli:latui, lonli:lonui]

    return dataSubset


lat_bnds = [25.0, 26.0]
lon_bnds = [-108, -107]

print(queryFile(date(2018, 1, 1), 'MAX_TMP_110_HTGL', lat_bnds, lon_bnds))

