import os
import time
from py4design import urbanformeval, py3dmodel
import read_collada_4_evalurbanform as read_collada

#========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

dae_file = os.path.join(parent_path, "example_files", "dae", "example1_1.dae")
weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
nshffai_filepath = os.path.join(parent_path, "example_files", "dae", "results", "py2radiance_nshffai")
dffai_filepath = os.path.join(parent_path, "example_files", "dae", "results", "py2radiance_dffai")
pvafai_filepath = os.path.join(parent_path, "example_files", "dae", "results", "py2radiance_pvafai")
pvefai_filepath = os.path.join(parent_path, "example_files", "dae", "results", "py2radiance_pvefai")
daysim_filepath = os.path.join(parent_path, "example_files", "dae", "results", "daysim_data")

lower_irrad_threshold = 254#kw/m2
upper_irrad_threshold = 364#kw/m2
illum_threshold = 10000#lux ~~254kw/m2
roof_irrad_threshold = 1280 #kwh/m2
facade_irrad_threshold = 512 #kwh/m2

display2dlist = []
colourlist = []
#==================================================================================================
#read and sort collada file
#==================================================================================================
print "READING COLLADA ..."
time1 = time.clock()

solid_list, opengeom_shells, opengeom_faces, edges = read_collada.read_collada(dae_file)
time2 = time.clock()
tt1 = time2-time1
print "TIME TAKEN 4 COLLADA:", tt1/60.0

#==================================================================================================
#calculate nshffai
#==================================================================================================
print "CALCULATING NSHFFAI ..."
time7 = time.clock()
nshffai_dict = urbanformeval.nshffai(solid_list, upper_irrad_threshold, weatherfilepath, 10,10, nshffai_filepath)
                                                                                
print "NSHFFAI", nshffai_dict["afi"]
time8 = time.clock()
tt4 = time8-time7
print "TIME TAKEN 4 NSHFFAI:", tt4/60.0

#==========================================================================================================================
#calculate USFFAI
#==========================================================================================================================
print "CALCULATING USFFAI ..."
time7 = time.clock()
usffai_dict = urbanformeval.usffai(solid_list, lower_irrad_threshold, upper_irrad_threshold, weatherfilepath, 10,10, nshffai_filepath)
                                                                                
print "USFFAI", usffai_dict["afi"]
time8 = time.clock()
tt4 = time8-time7
print "TIME TAKEN 4 USFFAI:", tt4/60.0

#==========================================================================================================================
#calculate DFAVI
#==========================================================================================================================
print "CALCULATING DFFAI ..."
time9 = time.clock()
dffai_dict = urbanformeval.dffai(solid_list, illum_threshold, weatherfilepath, 10,10, dffai_filepath, daysim_filepath)

print "DFFAI", dffai_dict["afi"]
time10 = time.clock()
tt5 = time10-time9
print "TIME TAKEN 4 DFFAI:", tt5/60.0
#==========================================================================================================================
#calculate PVEAVI
#==========================================================================================================================
print "CALCULATING PVEFAI ..."
time11 = time.clock()
pvefai_dict = urbanformeval.pvefai(solid_list, roof_irrad_threshold, facade_irrad_threshold, weatherfilepath, 10, 10, pvefai_filepath)
                                                                                             
print 'PVEFAI', pvefai_dict["afi"][0]
print 'PVRFAI', pvefai_dict["afi"][1]
print 'PVFFAI', pvefai_dict["afi"][2]

time12 = time.clock()  
tt7 = time12- time11
print "TIME TAKEN7 4 PVEFAI:", tt7/60.0
print "TOTAL TIME TAKEN:", (time12-time1)/60.0

#VISUALISE
py3dmodel.utility.visualise_falsecolour_topo(pvefai_dict["sensor_surfaces"], pvefai_dict["solar_results"])