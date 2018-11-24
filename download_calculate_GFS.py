####################################################
# driver to download and create daily calculations #
# of GFS data                                    #
####################################################


import hourly_to_daily_GFS
from datetime import date, timedelta
import os
import gc

path = '/nomads.ncdc.noaa.gov/data/gfs4/'

startDate = date(2018, 1, 1)
endDate = date(2018, 1, 1)
myDate = startDate

#loop over dates from startDate to endDate
while myDate <= endDate:
    #split out the parts of the year
    year = ("{date.year:04}".format(date=myDate))
    month = ("{date.month:02}".format(date=myDate))
    day = ("{date.day:02}".format(date=myDate))
    tt = myDate.timetuple()
    julianday = format(tt.tm_yday, '03')

    #get current path
    fullPath = os.path.dirname(os.path.abspath(__file__)) + path

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

            #print('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies -np -r --content-disposition https://nomads.ncdc.noaa.gov/data/gfs4/' + year + month + '/' + year + month + day + '/ -A grb2')
            #os.system('wget -np -r --content-disposition https://nomads.ncdc.noaa.gov/data/gfs4/' + year + month + '/' + year + month + day  + '/' + filename)

    #create daily averages and output netCDF file
    #loop over all forecast intervals for the given day (000, 003, 006, ....384)
    for j in range(129):
        #os.system('python -c "import hourly_to_daily_GFS; hourly_to_daily_GFS.hourly_to_daily_one_day(\'' + fullPath + '\',\'' + year + '\',\'' + month + '\',\'' + day + '\',\'' + str(j*3).zfill(3) + '\')')
        #print('python hourly_to_daily_GFS.hourly_to_daily_one_day(' + fullPath + ',' + year + ', ' + month + ', ' + day + ', ' + str(j*3).zfill(3) + ')')
        os.system('python -c "import hourly_to_daily_GFS; hourly_to_daily_GFS.hourly_to_daily_one_day(\'' + fullPath + '\',\'' + year + '\',\'' + month + '\',\'' + day + '\',\'' + str(j*3).zfill(3) + '\')"')
        gc.collect()
    myDate += timedelta(days=1)