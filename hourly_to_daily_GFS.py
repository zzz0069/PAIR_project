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


LAT = 361
LON = 720
HOURS = 24

# variables in original grb file
VARIABLE_NAMES = ['TMP_P0_L1_GLL0',  # Temperature
                  'UGRD_P0_L104_GLL0',  # u-component of wind
                  'VGRD_P0_L104_GLL0',  # v-component of wind
                  'RH_P0_L200_GLL0',  # Relative     humidity
                  'PWAT_P0_L200_GLL0',  # Total precipitation
                  'lat_0',  # latitude
                  'lon_0'] # longitude

# variables that not in new file
IGNORE_VARNAMES = ['TMP_P0_L6_GLL0',
                   'TMP_P0_L7_GLL0',
                   'TMP_P0_L100_GLL0',
                   'TMP_P0_L102_GLL0',
                   'TMP_P0_L103_GLL0',
                   'TMP_P0_L104_GLL0',
                   'TMP_P0_2L108_GLL0',
                   'TMP_P0_L109_GLL0',
                   'POT_P0_L104_GLL0',
                   'APTMP_P0_L103_GLL0',
                   'SPFH_P0_L103_GLL0',
                   'SPFH_P0_2L108_GLL0',
                   'RH_P0_L4_GLL0',
                   'RH_P0_L100_GLL0',
                   'RH_P0_L103_GLL0',
                   'RH_P0_2L104_GLL0',
                   'RH_P0_L104_GLL0',
                   'RH_P0_2L108_GLL0',
                   'RH_P0_L204_GLL0',
                   'SNOD_P0_L1_GLL0',
                   'WEASD_P0_L1_GLL0',
                   'CLWMR_P0_L100_GLL0',
                   'CPOFP_P0_L1_GLL0',
                   'PEVPR_P0_L1_GLL0',
                   'UGRD_P0_L6_GLL0',
                   'UGRD_P0_L7_GLL0',
                   'UGRD_P0_L100_GLL0',
                   'UGRD_P0_L102_GLL0',
                   'UGRD_P0_L103_GLL0',
                   'UGRD_P0_2L108_GLL0',
                   'UGRD_P0_L109_GLL0',
                   'UGRD_P0_L220_GLL0',
                   'VGRD_P0_L6_GLL0',
                   'VGRD_P0_L7_GLL0',
                   'VGRD_P0_L100_GLL0',
                   'VGRD_P0_L102_GLL0',
                   'VGRD_P0_L103_GLL0',
                   'VGRD_P0_2L108_GLL0',
                   'VGRD_P0_L109_GLL0',
                   'VGRD_P0_L220_GLL0',
                   'VVEL_P0_L100_GLL0',
                   'VVEL_P0_L104_GLL0',
                   'ABSV_P0_L100_GLL0',
                   'GUST_P0_L1_GLL0',
                   'VWSH_P0_L7_GLL0',
                   'VWSH_P0_L109_GLL0',
                   'USTM_P0_2L103_GLL0',
                   'VSTM_P0_2L103_GLL0',
                   'VRATE_P0_L220_GLL0',
                   'PRES_P0_L1_GLL0',
                   'PRES_P0_L6_GLL0',
                   'PRES_P0_L7_GLL0',
                   'PRES_P0_L103_GLL0',
                   'PRES_P0_L109_GLL0',
                   'PRES_P0_L242_GLL0',
                   'PRES_P0_L243_GLL0',
                   'PRMSL_P0_L101_GLL0',
                   'ICAHT_P0_L6_GLL0',
                   'ICAHT_P0_L7_GLL0',
                   'HGT_P0_L1_GLL0',
                   'HGT_P0_L4_GLL0',
                   'HGT_P0_L6_GLL0',
                   'HGT_P0_L7_GLL0',
                   'HGT_P0_L100_GLL0',
                   'HGT_P0_L109_GLL0',
                   'HGT_P0_L204_GLL0',
                   'MSLET_P0_L101_GLL0',
                   '5WAVH_P0_L100_GLL0',
                   'HPBL_P0_L1_GLL0',
                   'PLPL_P0_2L108_GLL0',
                   'TCDC_P0_L244_GLL0',
                   'CWAT_P0_L200_GLL0',
                   'SUNSD_P0_L1_GLL0',
                   'CAPE_P0_L1_GLL0',
                   'CAPE_P0_2L108_GLL0',
                   'CIN_P0_L1_GLL0',
                   'CIN_P0_2L108_GLL0',
                   'HLCY_P0_2L103_GLL0',
                   'LFTX_P0_L1_GLL0',
                   '4LFTX_P0_L1_GLL0',
                   'TOZNE_P0_L200_GLL0',
                   'O3MR_P0_L100_GLL0',
                   'VIS_P0_L1_GLL0',
                   'ICSEV_P0_L100_GLL0',
                   'LAND_P0_L1_GLL0',
                   'TSOIL_P0_2L106_GLL0',
                   'SOILW_P0_2L106_GLL0',
                   'WILT_P0_L1_GLL0',
                   'LANDN_P0_L1_GLL0',
                   'FLDCP_P0_L1_GLL0',
                   'HINDEX_P0_L1_GLL0',
                   'ICEC_P0_L1_GLL0',
                   'TMP_P8_L213_GLL0_avg3h',
                   'TMP_P8_L223_GLL0_avg3h',
                   'TMP_P8_L233_GLL0_avg3h',
                   'TMAX_P8_L103_GLL0_max3h',
                   'TMIN_P8_L103_GLL0_min3h',
                   'LHTFL_P8_L1_GLL0_avg3h',
                   'SHTFL_P8_L1_GLL0_avg3h',
                   'PRATE_P8_L1_GLL0_avg3h',
                   'APCP_P8_L1_GLL0_acc3h',
                   'ACPCP_P8_L1_GLL0_acc3h',
                   'CRAIN_P8_L1_GLL0_avg3h',
                   'CFRZR_P8_L1_GLL0_avg3h',
                   'CICEP_P8_L1_GLL0_avg3h',
                   'CSNOW_P8_L1_GLL0_avg3h',
                   'CPRAT_P8_L1_GLL0_avg3h',
                   'UFLX_P8_L1_GLL0_avg3h',
                   'VFLX_P8_L1_GLL0_avg3h',
                   'PRES_P8_L212_GLL0_avg3h',
                   'PRES_P8_L213_GLL0_avg3h',
                   'PRES_P8_L222_GLL0_avg3h',
                   'PRES_P8_L223_GLL0_avg3h',
                   'PRES_P8_L232_GLL0_avg3h',
                   'PRES_P8_L233_GLL0_avg3h',
                   'UGWD_P8_L1_GLL0_avg3h',
                   'VGWD_P8_L1_GLL0_avg3h',
                   'DSWRF_P8_L1_GLL0_avg3h',
                   'USWRF_P8_L1_GLL0_avg3h',
                   'USWRF_P8_L8_GLL0_avg3h',
                   'DLWRF_P8_L1_GLL0_avg3h',
                   'ULWRF_P8_L1_GLL0_avg3h',
                   'ULWRF_P8_L8_GLL0_avg3h',
                   'TCDC_P8_L10_GLL0_avg3h',
                   'TCDC_P8_L211_GLL0_avg3h',
                   'TCDC_P8_L214_GLL0_avg3h',
                   'TCDC_P8_L224_GLL0_avg3h',
                   'TCDC_P8_L234_GLL0_avg3h',
                   'CWORK_P8_L200_GLL0_avg3h',
                   'ALBDO_P8_L1_GLL0_avg3h',
                   'WATR_P8_L1_GLL0_acc3h',
                   'GFLUX_P8_L1_GLL0_avg3h',
                   'lv_DBLL12_l1',
                   'lv_DBLL12_l0',
                   'lv_ISBL11',
                   'lv_ISBL10',
                   'lv_SPDL9_l1',
                   'lv_SPDL9_l0',
                   'lv_ISBL8',
                   'lv_HTGL7',
                   'lv_ISBL6',
                   'lv_SIGL5_l1',
                   'lv_SIGL5_l0',
                   'lv_HTGL4',
                   'lv_PVL3',
                   'lv_HTGL2',
                   'lv_AMSL1',
                   'lv_ISBL0']

# varlables that not divide HOURS
DAILY_VARNAMES = ['PWAT_P0_L200_GLL0',
                  'MAX_TMP_P0_L1_GLL0',
                  'MIN_TMP_P0_L1_GLL0',
                  'MAX_RH_P0_L200_GLL0',
                  'MIN_RH_P0_L200_GLL0',
                  'lat_0',
                  'lon_0']


def grb_file_name_one_day(path, year, month, day):
    file_name_list = []
    for grb_file in glob.glob(os.path.join(path + year + month + '/' + year + month + day + '/', '*.grb2')):
        file_name_list.append(grb_file)
    return file_name_list

def hourly_to_daily_one_day(path, year, month, day):
    # Create a grb dict of all variables for one day
    grbs = grb_file_name_one_day(path, year, month, day)
    grb_one_day = {}

    for grb in grbs:
        nios = Nio.open_file(grb, mode='r', options=None, history='', format='')
        varNames = nios.variables.keys()
        if grb_one_day == {}:
            for varName in varNames:
                if varName in IGNORE_VARNAMES:
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
                if varName in IGNORE_VARNAMES:
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
        else:
            grb_one_day[key] = value / HOURS

    # calculate avgerage temperature
    grb_one_day['AVG_MAX_MIN_TMP_P0_L1_GLL0'] = (grb_one_day['MAX_TMP_P0_L1_GLL0'] + grb_one_day['MIN_TMP_P0_L1_GLL0']) / 2

    # calclate windspeed
    wind_speed = np.sqrt(np.square(grb_one_day['U_GRD_110_HTGL']) + np.square(grb_one_day['V_GRD_110_HTGL']))
    grb_one_day['WIND_SPEED'] = wind_speed

    # create netCDF file
    netCDF_data = Dataset(os.path.dirname(__file__) + "/netCDF/GFS_" + year + month + day + ".nc", "w",
                          format="NETCDF4")

    # add dimensions
    lat = netCDF_data.createDimension('lat_0', LAT)
    lon = netCDF_data.createDimension('lon_0', LON)

    # create and assign attr for all variables
    for varName in varNames:
        if varName in IGNORE_VARNAMES:
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

    # add 'ET' variable
    netCDF_data.createVariable('ET', 'f', ('lat_0', 'lon_0'), fill_value=1.0e+20)
    for key, value in nios.variables['TMP_P0_L1_GLL0'].attributes.items():
        if key == '_FillValue':
            continue
        setattr(netCDF_data.variables['ET'], key, value)
    netCDF_data.variables['ET'][:] = grb_one_day['ET']

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
    return
