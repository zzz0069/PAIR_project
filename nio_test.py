import Nio
print(Nio.__version__)

PATH = '/Users/yymjzq/hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/2012/007/NLDAS_FORA0125_H.A20120107.0000.002.grb'

#Open and print a summary of the file contents
nios = Nio.open_file(PATH, mode='r', options=None, history='', format='')
print(nios)

#Get the dimension names from the file
dimNames = nios.dimensions.keys()

#Get the size of a dimension by name
dimSize = nios.dimensions['lat_110']
#print(dimSize)

#Get all the variable names in the file
varNames = nios.variables.keys()
#print(varNames)

#Print a summary of a variable in the file
var = nios.variables['PEVAP_110_SFC_acc1h']
print(var)

#Get the type, number of dimensions, dimension sizes, 
#and dimension names of a variable object
var_type = var.typecode()
numDims = var.rank
dimSizes = var.shape
dimNames = var.dimensions

#Get the attributes of a variable
varAtts = var.attributes.keys()
print(varAtts)

#Get all the variable attributes and their associated values
varAttsAndVals = var.attributes
print(varAttsAndVals)

#Get the value of a variable attribute
varAttVal = var.attributes['forecast_time_units']
print(varAttVal)

#Get the data in a variable object into a NumPy array
data = nios.variables['PEVAP_110_SFC_acc1h'].get_value()
print(data)

#Create a global attribute in the file(will change the file!!!)
#nioss.globalAttName = globalAttVal

#Assuming 'dimName' is a string, rather than a variable, 
#create a dimension of length 74(will change the file!!!)
#nioss.create_dimension('dimName',74)

#Create a variable in the file(will change the file!!!)
#var = nioss.create_variable('varName','f',('dim1',dim2'))

#Create an attribute of a variable in the file(will change the file!!!)
#nioss.variables['varName'].varAttName = varAttVal

#Assigning values to a variable in the file(will change the file!!!)
#data is a NumPy array or a Python sequence containing the same 
#number of elements as the target file variable
#nioss.variables['varName'][:] = data


















