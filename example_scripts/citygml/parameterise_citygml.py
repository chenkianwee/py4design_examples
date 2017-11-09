import os
import time
from py4design import gmlparmpalette, gmlparameterise
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files","citygml", "punggol_luse101.gml")
result_citygml_filepath = os.path.join(parent_path, "example_files","citygml", "results", "punggol_variant.gml" )

'''citygml_filepath = "C://file2analyse.gml"
result_citygml_filepath = "C://result.gml'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================

time1 = time.clock()   
display_2dlist = []
colour_list = []

#define the parameters
#bldg_height_parm = gmlparmpalette.BldgHeightParm()
#bldg_height_parm.define_int_range(30,200,3)
#bldg_height_parm.apply_2_bldg_function("1000")#residential bldg

bldg_height_parm = gmlparmpalette.BldgFlrAreaHeightParm()
bldg_height_parm.define_int_range(30,200,3)
bldg_height_parm.apply_2_bldg_function("1000")#residential bldg

bldg_orientation_parm = gmlparmpalette.BldgOrientationParm()
bldg_orientation_parm.define_int_range(0,350,10)
bldg_orientation_parm.set_clash_detection(True)
bldg_orientation_parm.set_boundary_detection(True)

bldg_pos_parm = gmlparmpalette.BldgPositionParm()
bldg_pos_parm.set_xdim_ydim(10,10)
bldg_pos_parm.set_boundary_detection(True)
bldg_pos_parm.set_clash_detection(True)

#append all the parameters into the parameterise class
parameterise = gmlparameterise.Parameterise(citygml_filepath)
parameterise.add_parm(bldg_height_parm)
parameterise.add_parm(bldg_orientation_parm)
parameterise.add_parm(bldg_pos_parm)
parameters = parameterise.generate_random_parameters()
#parameters = [0.8947922637867739, 0.41554367606331843, 0.7001080436039618, 0.9956572805642249, 0.685843180411325, 0.738362664534732, 0.10747116742290064, 0.048713242937747814, 0.2527977782216123, 0.9680887432037879, 0.15891368273268103, 0.9247925429076911, 0.22005469775711906, 0.8238443660142792, 0.1042960065836398]
parameterise.generate_design_variant(parameters, result_citygml_filepath)
print parameters
time2 = time.clock() 
print "TIME TAKEN", (time2-time1)/60.0