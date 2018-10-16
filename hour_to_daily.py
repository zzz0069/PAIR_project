###################################################
#1. Create a grb dict of all variables for one day# 
#2. Create empty netCDF file 					  #	
#3. write all tho netCDF file 					  #
###################################################

import Nio
import os
import numpy as np
import glob

from netCDF4 import Dataset

PATH = '/Users/yymjzq/hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/2012/007/'
lat_110 = 224
lon_110 = 464
HOURS = 24

#variables in original grb file of NLDAS-2 monitor data
variable_names = ['PRES_110_SFC', 			#Pressure
				  'TMP_110_HTGL', 			#Temperature
				  'U_GRD_110_HTGL',			#u-component of wind 
				  'V_GRD_110_HTGL',			#v-component of wind 
				  'SPF_H_110_HTGL', 		#Specific humidity
				  'A_PCP_110_SFC_acc1h', 	#Total precipitation
				  'NCRAIN_110_SFC_acc1h',	#Number concentration for rain particles 
				  'CAPE_110_SPDY', 			#Convective available potential energy
				  'DSWRF_110_SFC', 			#Downward shortwave radiation flux
				  'DLWRF_110_SFC', 			#Downward longwave radiation flux
				  'PEVAP_110_SFC_acc1h',	#Potential evaporation
				  'lat_110',				#latitude
				  'lon_110']				#longitude	

ignore_varnames = ['NCRAIN_110_SFC_acc1h',	
				  'CAPE_110_SPDY', 			
				  'DSWRF_110_SFC', 			
				  'DLWRF_110_SFC', 			
				  'PEVAP_110_SFC_acc1h',
				  'lat_110',
				   'lon_110']

def grb_file_name_one_day(file_path):
	file_name_list = []
	for grb_file in glob.glob(os.path.join(file_path, '*.grb')):
		file_name_list.append(grb_file)
	return file_name_list

def hour_to_daily_one_day():
	#Create a grb dict of all variables for one day
	grbs = grb_file_name_one_day(PATH)
	grb_one_day = {}

	for grb in grbs:
		nios = Nio.open_file(grb, mode='r', options=None, history='', format='')
		varNames = nios.variables.keys()
		if grb_one_day == {}:
			for varName in varNames:
				if varName in ignore_varnames:
					continue
				if varName == 'TMP_110_HTGL':
					grb_one_day['MAX_%s'%varName] = nios.variables[varName].get_value()	
					grb_one_day['MIN_%s'%varName] = nios.variables[varName].get_value()
				else:
					grb_one_day['%s'%varName] = nios.variables[varName].get_value()
		else:
			for varName in varNames:
				if varName in ignore_varnames:
					continue
				if varName == 'TMP_110_HTGL':
					grb_one_day['MAX_%s'%varName] = np.maximum(nios.variables[varName].get_value(), grb_one_day['MAX_%s'%varName])	
					grb_one_day['MIN_%s'%varName] = np.minimum(nios.variables[varName].get_value(), grb_one_day['MIN_%s'%varName])
				else:
					grb_one_day['%s'%varName] += nios.variables[varName].get_value()
	for key, value in grb_one_day.items():
		if key in ['A_PCP_110_SFC_acc1h', 'MAX_TMP_110_HTGL', 'MAX_TMP_110_HTGL']:
			continue
		else:
			grb_one_day[key] = value / HOURS
	return grb_one_day

def create_empty_netCDF():
	rootgrp = Dataset("test.nc", "w", format="NETCDF4")

def write_to_netCDF():
	pass

def close_and_output_netCDF():
	rootgrp.close()

def netCDF_daily_file_one_year():
	pass

def netCDF_daily_file_all_year(start_year, end_year):
	pass
