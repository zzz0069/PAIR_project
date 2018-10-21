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

#variables that not in new file
ignore_varnames = ['NCRAIN_110_SFC_acc1h',	
				  'CAPE_110_SPDY', 			
				  'DSWRF_110_SFC', 			
				  'DLWRF_110_SFC', 			
				  'PEVAP_110_SFC_acc1h']

#varlables that not divide HOURS
daily_varnames = ['A_PCP_110_SFC_acc1h', 
				  'MAX_TMP_110_HTGL', 
				  'MAX_TMP_110_HTGL', 
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
				elif varName == 'TMP_110_HTGL':
					grb_one_day['MAX_%s'%varName] = np.maximum(nios.variables[varName].get_value(), grb_one_day['MAX_%s'%varName])	
					grb_one_day['MIN_%s'%varName] = np.minimum(nios.variables[varName].get_value(), grb_one_day['MIN_%s'%varName])
				elif varName in ['lat_110', 'lon_110']:
					continue
				else:
					grb_one_day['%s'%varName] += nios.variables[varName].get_value()
	
	for key, value in grb_one_day.items():
		if key in daily_varnames:
			continue
		else:
			grb_one_day[key] = value / HOURS

	netCDF_data = Dataset("test.nc", "w", format="NETCDF4")

	#add dimensions
	lat = netCDF_data.createDimension('lat_110', 224)
	lon = netCDF_data.createDimension('lon_110', 464)

	#create and assign attr for all variables
	for varName in varNames:
		if varName in ignore_varnames:
			continue
		elif varName == 'TMP_110_HTGL':
			netCDF_data.createVariable('MAX_%s'%varName, 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
			netCDF_data.createVariable('MIN_%s'%varName, 'f', ('lat_110', 'lon_110'), fill_value=1.0e+20)
		elif varName in ['lat_110', 'lon_110']:
			netCDF_data.createVariable(str(varName), 'f', (varName,))
		else:
			netCDF_data.createVariable(str(varName),'f',('lat_110', 'lon_110'), fill_value=1.0e+20)

		nio_vari = nios.variables[varName]
		grb_attr = nio_vari.attributes
		for key, value in grb_attr.items():
			if key == '_FillValue':
				continue
			if varName == 'TMP_110_HTGL':
				setattr(netCDF_data.variables['MAX_%s'%varName], key, value)
				setattr(netCDF_data.variables['MIN_%s'%varName], key, value)
			else:
				setattr(netCDF_data.variables[varName], key, value)


		if varName == 'TMP_110_HTGL':
			netCDF_data.variables['MAX_%s'%varName][:] = grb_one_day['MAX_%s'%varName]
			netCDF_data.variables['MIN_%s'%varName][:] = grb_one_day['MIN_%s'%varName]
		else:
			netCDF_data.variables[varName][:] = grb_one_day[varName]
	return netCDF_data

print(hour_to_daily_one_day())

def netCDF_daily_file_one_year():
	pass

def netCDF_daily_file_all_year(start_year, end_year):
	pass
