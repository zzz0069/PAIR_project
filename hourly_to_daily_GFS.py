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
import gc
from netCDF4 import Dataset

import pyeto
from pyeto import convert


LAT = 361
LON = 720
HOURS = 24

# variables in original grb file
VARIABLE_NAMES = ['TMP_P0_L1_GLL0',  # Temperature
                  'UGRD_P0_L104_GLL0',  # u-component of wind
                  'VGRD_P0_L104_GLL0',  # v-component of wind
                  'RH_P0_L200_GLL0',  # Relative     humidity
                  'APCP_P8_L1_GLL0_acc',  # Total precipitation
                  'lat_0',  # latitude
                  'lon_0'] # longitude


# varlables that not divide HOURS
DAILY_VARNAMES = ['APCP_P8_L1_GLL0_acc',
                  'MAX_TMP_P0_L1_GLL0',
                  'MIN_TMP_P0_L1_GLL0',
                  'MAX_RH_P0_L200_GLL0',
                  'MIN_RH_P0_L200_GLL0',
                  'lat_0',
                  'lon_0']


def grb_file_name_one_day(path, year, month, day, forecastInterval):
    file_name_list = []
    for grb_file in glob.glob(os.path.join(path + year + month + '/' + year + month + day + '/', '*' + forecastInterval + '.grb2')):
        file_name_list.append(grb_file)
    return file_name_list


def hourly_to_daily_one_day(path, year, month, day, forecastInterval):
    # Create a grb dict of all variables for one day
    grbs = grb_file_name_one_day(path, year, month, day, forecastInterval)
    grb_one_day = {}

    for grb in grbs:
        print(grb)
        nios = Nio.open_file(grb, mode='r', options=None, history='', format='')
        varNames = nios.variables.keys()
        if grb_one_day == {}:
            for varName in varNames:
                if varName not in VARIABLE_NAMES:
                    continue
                if varName == 'TMP_P0_L1_GLL0' :
                    grb_one_day['MAX_%s' % varName] = nios.variables[varName].get_value()
                    grb_one_day['MIN_%s' % varName] = nios.variables[varName].get_value()
                elif varName == 'RH_P0_L200_GLL0':
                    grb_one_day['MAX_%s' % varName] = nios.variables[varName].get_value()
                    grb_one_day['MIN_%s' % varName] = nios.variables[varName].get_value()
                    grb_one_day['%s' % varName] = nios.variables[varName].get_value()
                else:
                    grb_one_day['%s' % varName] = nios.variables[varName].get_value()
        else:
            for varName in varNames:
                if varName not in VARIABLE_NAMES:
                    continue
                if varName == 'TMP_P0_L1_GLL0':
                    grb_one_day['MAX_%s' % varName] = np.maximum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MAX_%s' % varName])
                    grb_one_day['MIN_%s' % varName] = np.minimum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MIN_%s' % varName])
                elif varName == 'RH_P0_L200_GLL0':
                    grb_one_day['MAX_%s' % varName] = np.maximum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MAX_%s' % varName])
                    grb_one_day['MIN_%s' % varName] = np.minimum(nios.variables[varName].get_value(),
                                                                 grb_one_day['MIN_%s' % varName])
                    grb_one_day['%s' % varName] += nios.variables[varName].get_value()
                elif varName in ['lat_0', 'lon_0']:
                    continue
                else:
                    grb_one_day['%s' % varName] += nios.variables[varName].get_value()


    for key, value in grb_one_day.items():
        if key in DAILY_VARNAMES:
            continue
        elif key not in VARIABLE_NAMES:
            continue
        else:
            grb_one_day[key] = value / HOURS

    # calculate avgerage temperature
    grb_one_day['AVG_MAX_MIN_TMP_P0_L1_GLL0'] = (grb_one_day['MAX_TMP_P0_L1_GLL0'] + grb_one_day['MIN_TMP_P0_L1_GLL0']) / 2

    # calclate windspeed
    wind_speed = np.sqrt(np.square(grb_one_day['UGRD_P0_L104_GLL0']) + np.square(grb_one_day['VGRD_P0_L104_GLL0']))
    grb_one_day['WIND_SPEED'] = wind_speed

    # create netCDF file
    netCDF_data = Dataset(os.path.dirname(__file__) + "/netCDF/GFS_" + year + month + day + "_" + forecastInterval + ".nc", "w",
                          format="NETCDF4")

    # add dimensions
    lat = netCDF_data.createDimension('lat_0', LAT)
    lon = netCDF_data.createDimension('lon_0', LON)

    # create and assign attr for all variables
    for varName in varNames:
        if varName not in VARIABLE_NAMES:
            continue
        if varName == 'TMP_P0_L1_GLL0':
            netCDF_data.createVariable('MAX_%s' % varName, 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
            netCDF_data.createVariable('MIN_%s' % varName, 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
        elif varName == 'RH_P0_L200_GLL0':
            netCDF_data.createVariable('MAX_%s' % varName, 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
            netCDF_data.createVariable('MIN_%s' % varName, 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
            netCDF_data.createVariable(str(varName), 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
        elif varName in ['lat_0', 'lon_0']:
            netCDF_data.createVariable(str(varName), 'f', (varName,))
        else:
            netCDF_data.createVariable(str(varName), 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)

        nio_vari = nios.variables[varName]
        grb_attr = nio_vari.attributes
        for key, value in grb_attr.items():
            if key == '_FillValue':
                continue
            if varName == 'TMP_P0_L1_GLL0':
                setattr(netCDF_data.variables['MAX_%s' % varName], key, value)
                setattr(netCDF_data.variables['MIN_%s' % varName], key, value)
            elif varName == 'RH_P0_L200_GLL0':
                setattr(netCDF_data.variables['MAX_%s' % varName], key, value)
                setattr(netCDF_data.variables['MIN_%s' % varName], key, value)
                setattr(netCDF_data.variables[varName], key, value)
            else:
                setattr(netCDF_data.variables[varName], key, value)
        # change attr 'forecast_time_units' from 'hours' to 'daily'

        if varName == 'TMP_P0_L1_GLL0':
            netCDF_data.variables['MAX_%s' % varName][:] = grb_one_day['MAX_%s' % varName]
            netCDF_data.variables['MIN_%s' % varName][:] = grb_one_day['MIN_%s' % varName]
        elif varName == 'RH_P0_L200_GLL0':
            netCDF_data.variables['MAX_%s' % varName][:] = grb_one_day['MAX_%s' % varName]
            netCDF_data.variables['MIN_%s' % varName][:] = grb_one_day['MIN_%s' % varName]
            netCDF_data.variables[varName][:] = grb_one_day[varName]
        else:
            netCDF_data.variables[varName][:] = grb_one_day[varName]

    # add 'AVG_MAX_MIN_TMP_P0_L1_GLL0' variable
    netCDF_data.createVariable('AVG_MAX_MIN_TMP_P0_L1_GLL0', 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
    for key, value in nios.variables['TMP_P0_L1_GLL0'].attributes.items():
        if key == '_FillValue':
            continue
        setattr(netCDF_data.variables['AVG_MAX_MIN_TMP_P0_L1_GLL0'], key, value)
    netCDF_data.variables['AVG_MAX_MIN_TMP_P0_L1_GLL0'][:] = grb_one_day['AVG_MAX_MIN_TMP_P0_L1_GLL0']


    # add 'WIND_SPEED' variable
    netCDF_data.createVariable('WIND_SPEED', 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
    netCDF_data.variables['WIND_SPEED'][:] = grb_one_day['WIND_SPEED']

    # change some values of attr for different vari
    netcdf_varis = netCDF_data.variables.keys()
    for netcdf_vari in netcdf_varis:
        if netcdf_vari in ['lat_0', 'lon_0', 'WIND_SPEED']:
            continue
        else:
            setattr(netCDF_data.variables[netcdf_vari], 'forecast_time_units', 'daily')
    # 'A_PCP_110_SFC_acc1h'
    setattr(netCDF_data.variables['AVG_MAX_MIN_TMP_P0_L1_GLL0'], 'long_name', 'Average of max and min temperture')
    # 'AVG_MAX_MIN_TMP_P0_L1_GLL0'
    # 'lat_0'
    # 'lon_0'
    # 'MAX_RH_P0_L200_GLL0'
    setattr(netCDF_data.variables['MAX_RH_P0_L200_GLL0'], 'long_name', 'Maximum relative humidity')
    # 'MAX_TMP_P0_L1_GLL0'
    setattr(netCDF_data.variables['MAX_TMP_P0_L1_GLL0'], 'long_name', 'Maximum Temperature')
    # 'MIN_RH_P0_L200_GLL0'
    setattr(netCDF_data.variables['MIN_RH_P0_L200_GLL0'], 'long_name', 'Minimum relative humidity')
    # 'MIN_TMP_P0_L1_GLL0'
    setattr(netCDF_data.variables['MIN_TMP_P0_L1_GLL0'], 'long_name', 'Minimum Temperature')
    # 'PRES_110_SFC'
    # 'RH_P0_L200_GLL0'
    # 'U_GRD_110_HTGL'
    # 'V_GRD_110_HTGL'
    # 'WIND_SPEED'
    setattr(netCDF_data.variables['WIND_SPEED'], 'long_name', 'Wind speed')
    netCDF_data.close()
    del grb_one_day
    del netCDF_data
    nios.close()
    del nios
    del varNames
    del grbs
    del nio_vari
    del grb_attr
    gc.collect()
    return
