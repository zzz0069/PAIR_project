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
variable_names = ['PRES_110_SFC', 'TMP_110_HTGL', 'U_GRD_110_HTGL', 
				  'V_GRD_110_HTGL', 'SPF_H_110_HTGL', 'A_PCP_110_SFC_acc1h', 
				  'NCRAIN_110_SFC_acc1h', 'CAPE_110_SPDY', 'DSWRF_110_SFC', 
				  'DLWRF_110_SFC', 'PEVAP_110_SFC_acc1h',]

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
		ignore_varnames = ['lat_110', 'lon_110']
		if grb_one_day == {}:
			for varName in varNames:
				if varName in ignore_varnames:
					continue
				grb_one_day['%s'%varName] = nios.variables[varName].get_value()
		else:
			for varName in varNames:
				if varName in ignore_varnames:
					continue
				grb_one_day['%s'%varName] += nios.variables[varName].get_value()
	return grb_one_day
	
def create_empty_netCDF():
	rootgrp = Dataset("test.nc", "w", format="NETCDF4")

def grb_daily_file_one_year():
	pass

