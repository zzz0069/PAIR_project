####################################################
# driver to download and create daily calculations #
# of NLDAS data                                    #
####################################################

#files required for wget
#.netrc - need to update with username/password to NLDAS data website
#.usr_cookies

import hourly_to_daily_NLDAS
from datetime import date, timedelta
import os

path = '/hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/'

startDate = date(2018, 1, 1)
endDate = date(2018, 1, 1)
myDate = startDate

while myDate <= endDate:
    year = ("{date.year:04}".format(date=myDate))
    tt = myDate.timetuple()
    julianday = format(tt.tm_yday, '03')
    print(year + julianday)

    fullPath = os.path.dirname(__file__) + path
    #call wget to download files for given year/day
    os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies -np -r --content-disposition https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/' + year + '/' + julianday + '/ -A grb')

    #create daily averages and output netCDF file
    hourly_to_daily_NLDAS.hourly_to_daily_one_day(fullPath, year, julianday)
    myDate += timedelta(days=1)
