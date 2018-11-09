####################################################
# 1. Create a grb dict of all variables for one day#
# 2. Calculate daily aggregates                    #
# 3. Calculate et                                  #
# 4. Create empty netCDF file 					   #
# 5. write all data to  netCDF file 			   #
####################################################

import Nio
import os
import numpy as np
import glob
import math
from netCDF4 import Dataset

import pyeto
from pyeto import convert


altitude = 200
LAT = 224
LON = 464
HOURS = 24

# variables in original grb file of NLDAS-2 monitor data
VARIABLE_NAMES = ['PRES_110_SFC',  # Pressure
                  'TMP_110_HTGL',  # Temperature
                  'U_GRD_110_HTGL',  # u-component of wind
                  'V_GRD_110_HTGL',  # v-component of wind
                  'SPF_H_110_HTGL',  # Specific humidity
                  'A_PCP_110_SFC_acc1h',  # Total precipitation
                  'NCRAIN_110_SFC_acc1h',  # Number concentration for rain particles
                  'CAPE_110_SPDY',  # Convective available potential energy
                  'DSWRF_110_SFC',  # Downward shortwave radiation flux
                  'DLWRF_110_SFC',  # Downward longwave radiation flux
                  'PEVAP_110_SFC_acc1h',  # Potential evaporation
                  'lat_110',  # latitude
                  'lon_110', # longitude
                   'DSWRF_110_SFC', #Downward Shortwave Radiation
                   'DLWRF_110_SFC'] #Downward Longwave Radiation

# variables that not in new file
IGNORE_VARNAMES = ['NCRAIN_110_SFC_acc1h',
                   'CAPE_110_SPDY',
                   'PEVAP_110_SFC_acc1h']

# varlables that not divide HOURS
DAILY_VARNAMES = ['A_PCP_110_SFC_acc1h',
                  'MAX_TMP_110_HTGL',
                  'MIN_TMP_110_HTGL',
                  'MAX_SPF_H_110_HTGL',
                  'MIN_SPF_H_110_HTGL',
                  'lat_110',
                  'lon_110',
                  'SOL_DEC']


def grb_file_name_one_day(path, year, julianday):
    file_name_list = []
    for grb_file in glob.glob(os.path.join(path + year + '/' + julianday + '/', '*.grb')):
        file_name_list.append(grb_file)
    return file_name_list


def hourly_to_daily_one_day(path, year, julianday):
    # Create a grb dict of all variables for one day
    grbs = grb_file_name_one_day(path, year, julianday)
    grb_one_day = {}

    for grb in grbs:
        nios = Nio.open_file(grb, mode='r', options=None, history='', format='')
        varNames = nios.variables.keys()
        if grb_one_day == {}:
            for varName in varNames:
                if varName in IGNORE_VARNAMES:
                    continue
                if varName == 'TMP_110_HTGL':
                    grb_one_day['MAX_%s' % varName] = nios.variables[varName].get_value()
                    grb_one_day['MIN_%s' % varName] = nios.variables[varName].get_value()
                elif varName == 'SPF_H_110_HTGL':
                    grb_one_day['MAX_%s' % varName] = nios.variables[varName].get_value()
                    grb_one_day['MIN_%s' % varName] = nios.variables[varName].get_value()
                    grb_one_day['%s' % varName] = nios.variables[varName].get_value()
                else:
                    grb_one_day['%s' % varName] = nios.variables[varName].get_value()
        else:
            for varName in varNames:
                if varName in IGNORE_VARNAMES:
                    continue
                if varName == 'TMP_110_HTGL':
                    grb_one_day['MAX_%s' % varName] = np.maximum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MAX_%s' % varName])
                    grb_one_day['MIN_%s' % varName] = np.minimum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MIN_%s' % varName])
                elif varName == 'SPF_H_110_HTGL':
                    grb_one_day['MAX_%s' % varName] = np.maximum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MAX_%s' % varName])
                    grb_one_day['MIN_%s' % varName] = np.minimum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MIN_%s' % varName])
                    grb_one_day['%s' % varName] += nios.variables[varName].get_value()
                elif varName in ['lat_110', 'lon_110']:
                    continue
                else:
                    grb_one_day['%s' % varName] += nios.variables[varName].get_value()

    for key, value in grb_one_day.items():
        if key in DAILY_VARNAMES:
            continue
        else:
            grb_one_day[key] = value / HOURS

    #calculate avgerage temperature
    grb_one_day['AVG_MAX_MIN_TMP_110_HTGL'] = (grb_one_day['MAX_TMP_110_HTGL'] + grb_one_day['MIN_TMP_110_HTGL']) / 2

    #calclate windspeed
    wind_speed = np.sqrt(np.square(grb_one_day['U_GRD_110_HTGL']) + np.square(grb_one_day['V_GRD_110_HTGL']))
    grb_one_day['WIND_SPEED'] = wind_speed

    #calculate ET
    et = grb_one_day['WIND_SPEED'][:]  #create array to hold et values
    rows = et.shape[0] #calculate number of rows in array
    cols = et.shape[1] #calculate number of columns in array

    #loop over the array and calculate et for each lat/lon
    for i in range(0, rows):
        for j in range(0, cols):
            # calculate avgerage temperature
            avg_max_min_tmp = (grb_one_day['MAX_TMP_110_HTGL'][i,j] + grb_one_day['MIN_TMP_110_HTGL'][i,j]) / 2
            #skip of there is no value to calculate
            if avg_max_min_tmp != "--":
              # convert temps to celcius
              min_tmp_c = convert.kelvin2celsius(grb_one_day['MIN_TMP_110_HTGL'][i,j])
              max_tmp_c = convert.kelvin2celsius(grb_one_day['MAX_TMP_110_HTGL'][i,j])
              avg_max_min_tmp_c = convert.kelvin2celsius(avg_max_min_tmp)
              #calculate solar declination
              sol_dec = pyeto.sol_dec(int(julianday))
              #convert lattitude to radians
              radlat = pyeto.deg2rad(grb_one_day['lat_110'][i])
              #calculate inverse relative distance between earth and sun
              ird = pyeto.inv_rel_dist_earth_sun(int(julianday))
              #calculate sunset hour angle
              sha = pyeto.sunset_hour_angle(pyeto.deg2rad(grb_one_day['lat_110'][i]), sol_dec)
              #calclate extraterrestrial radiation
              et_rad = pyeto.et_rad(pyeto.deg2rad(grb_one_day['lat_110'][i]), sol_dec, sha, ird)
              #calculate clear sky radiation
              cs_rad = pyeto.cs_rad(altitude, et_rad)
              #calculate net outgoing lonwave radation
              no_lw_rad = pyeto.net_out_lw_rad(grb_one_day['MIN_TMP_110_HTGL'][i,j], grb_one_day['MAX_TMP_110_HTGL'][i,j], grb_one_day['DSWRF_110_SFC'][i,j], cs_rad, pyeto.avp_from_tmin(min_tmp_c))
              #calculate net radiation
              net_rad = pyeto.net_rad(grb_one_day['DSWRF_110_SFC'][i,j], no_lw_rad)
              # calculate pyschometric constant
              psy = pyeto.psy_const(grb_one_day['PRES_110_SFC'][i, j])
              #calculat slope of saturation vapor pressure
              delta_svp=pyeto.delta_svp(avg_max_min_tmp_c)
              #calculate saturated vapor pressure
              svp = pyeto.svp_from_t(avg_max_min_tmp_c)
              #calculate actual vapor pressure
              avp = pyeto.avp_from_tmin(min_tmp_c)
              et[i,j] = pyeto.fao56_penman_monteith(
                    net_rad=net_rad,
                    t=avg_max_min_tmp,
                    ws=wind_speed[i,j],
                    svp=pyeto.svp_from_t(avg_max_min_tmp_c),
                    avp=pyeto.avp_from_tmin(min_tmp_c),
                    delta_svp=pyeto.delta_svp(avg_max_min_tmp_c),
                    psy=psy)
    grb_one_day['ET'] = et


    #create netCDF file
    netCDF_data = Dataset(os.path.dirname(__file__) + "/netCDF/NLDAS_" + year + "_" + julianday + ".nc", "w", format="NETCDF4")

    # add dimensions
    lat = netCDF_data.createDimension('lat_110', LAT)
    lon = netCDF_data.createDimension('lon_110', LON)

    # create and assign attr for all variables
    for varName in varNames:
        if varName in IGNORE_VARNAMES:
            continue
        if varName == 'TMP_110_HTGL':
            netCDF_data.createVariable('MAX_%s' % varName, 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
            netCDF_data.createVariable('MIN_%s' % varName, 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
        elif varName == 'SPF_H_110_HTGL':
            netCDF_data.createVariable('MAX_%s' % varName, 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
            netCDF_data.createVariable('MIN_%s' % varName, 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
            netCDF_data.createVariable(str(varName), 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
        elif varName in ['lat_110', 'lon_110']:
            netCDF_data.createVariable(str(varName), 'f', (varName,))
        else:
            netCDF_data.createVariable(str(varName), 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)

        nio_vari = nios.variables[varName]
        grb_attr = nio_vari.attributes
        for key, value in grb_attr.items():
            if key == '_FillValue':
                continue
            if varName == 'TMP_110_HTGL':
                setattr(netCDF_data.variables['MAX_%s' % varName], key, value)
                setattr(netCDF_data.variables['MIN_%s' % varName], key, value)
            elif varName == 'SPF_H_110_HTGL':
                setattr(netCDF_data.variables['MAX_%s' % varName], key, value)
                setattr(netCDF_data.variables['MIN_%s' % varName], key, value)
                setattr(netCDF_data.variables[varName], key, value)
            else:
                setattr(netCDF_data.variables[varName], key, value)
        # change attr 'forecast_time_units' from 'hours' to 'daily'

        if varName == 'TMP_110_HTGL':
            netCDF_data.variables['MAX_%s' % varName][:] = grb_one_day['MAX_%s' % varName]
            netCDF_data.variables['MIN_%s' % varName][:] = grb_one_day['MIN_%s' % varName]
        elif varName == 'SPF_H_110_HTGL':
            netCDF_data.variables['MAX_%s' % varName][:] = grb_one_day['MAX_%s' % varName]
            netCDF_data.variables['MIN_%s' % varName][:] = grb_one_day['MIN_%s' % varName]
            netCDF_data.variables[varName][:] = grb_one_day[varName]
        else:
            netCDF_data.variables[varName][:] = grb_one_day[varName]

    # add 'AVG_MAX_MIN_TMP_110_HTGL' variable
    netCDF_data.createVariable('AVG_MAX_MIN_TMP_110_HTGL', 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
    for key, value in nios.variables['TMP_110_HTGL'].attributes.items():
        if key == '_FillValue':
            continue
        setattr(netCDF_data.variables['AVG_MAX_MIN_TMP_110_HTGL'], key, value)
    netCDF_data.variables['AVG_MAX_MIN_TMP_110_HTGL'][:] = grb_one_day['AVG_MAX_MIN_TMP_110_HTGL']

    # add 'ET' variable
    netCDF_data.createVariable('ET', 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
    for key, value in nios.variables['TMP_110_HTGL'].attributes.items():
        if key == '_FillValue':
            continue
        setattr(netCDF_data.variables['ET'], key, value)
    netCDF_data.variables['ET'][:] = grb_one_day['ET']

    # add 'WIND_SPEED' variable
    netCDF_data.createVariable('WIND_SPEED', 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
    netCDF_data.variables['WIND_SPEED'][:] = grb_one_day['WIND_SPEED']

    # change some values of attr for different vari
    netcdf_varis = netCDF_data.variables.keys()
    for netcdf_vari in netcdf_varis:
        if netcdf_vari in ['lat_110', 'lon_110', 'WIND_SPEED']:
            continue
        else:
            setattr(netCDF_data.variables[netcdf_vari], 'forecast_time_units', 'daily')
    # 'A_PCP_110_SFC_acc1h'
    setattr(netCDF_data.variables['AVG_MAX_MIN_TMP_110_HTGL'], 'long_name', 'Average of max and min temperture')
    setattr(netCDF_data.variables['ET'], 'long_name', 'reference evapotranspiration')
    # 'AVG_MAX_MIN_TMP_110_HTGL'
    # 'lat_110'
    # 'lon_110'
    # 'MAX_SPF_H_110_HTGL'
    setattr(netCDF_data.variables['MAX_SPF_H_110_HTGL'], 'long_name', 'Maximum specific humidity')
    # 'MAX_TMP_110_HTGL'
    setattr(netCDF_data.variables['MAX_TMP_110_HTGL'], 'long_name', 'Maximum Temperature')
    # 'MIN_SPF_H_110_HTGL'
    setattr(netCDF_data.variables['MIN_SPF_H_110_HTGL'], 'long_name', 'Minimum specific humidity')
    # 'MIN_TMP_110_HTGL'
    setattr(netCDF_data.variables['MIN_TMP_110_HTGL'], 'long_name', 'Minimum Temperature')
    # 'PRES_110_SFC'
    # 'SPF_H_110_HTGL'
    # 'U_GRD_110_HTGL'
    # 'V_GRD_110_HTGL'
    # 'WIND_SPEED'
    setattr(netCDF_data.variables['WIND_SPEED'], 'long_name', 'Wind speed')
    netCDF_data.close()
    return



#print(hourly_to_daily_one_day('2018','001'))


def netCDF_daily_file_one_year():
    pass


def netCDF_daily_file_all_year(start_year, end_year):
    pass