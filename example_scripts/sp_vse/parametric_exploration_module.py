import os
import time
from py4design import py3dmodel, citygml2eval, massing2citygml, analysisrulepalette, templaterulepalette, gmlparmpalette, gmlparameterise,gml3dmodel
import ntpath

#====================================================================================================================
#INPUTS
#====================================================================================================================
design_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\sp_vse_materials\\dae\\test_tower1.dae"
site_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\sp_vse_materials\\dae\\site.dae"
weatherfilepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\sp_vse_materials\\epw\\SGP_Singapore.486980_IWEC.epw"

#configure the parameterisation
height = True
height_value = 72

taper = True
taper_value = 1.6

twist = True
twist_value = 45

slant = True
slant_value = 5

bend = True
bend_value = 30

orientation = True
orientation_value = 40
#====================================================================================================================
#INPUTS
#====================================================================================================================

#====================================================================================================================
#THE MAIN SCRIPT
#====================================================================================================================
site_filename = ntpath.basename(site_dae_file)
site_filename = site_filename.split(".")[0]

design_filename = ntpath.basename(design_dae_file)
design_filename = design_filename.split(".")[0]

parent_path = os.path.abspath(os.path.join(design_dae_file, os.pardir))
pef_dir = os.path.join(parent_path, design_filename + "_performance")

if not os.path.exists(pef_dir):
    os.makedirs(pef_dir)
    
citygml_dir = os.path.join(pef_dir, "citygml")
if not os.path.exists(citygml_dir):
    os.makedirs(citygml_dir)

site_citygml_filepath = os.path.join(citygml_dir, site_filename + ".gml")
design_citygml_filepath = os.path.join(citygml_dir, design_filename + ".gml")

#write exploration log
log_dir = os.path.join(pef_dir, "csv")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    
log_filepath = os.path.join(log_dir, "parametric_log.csv")
if not os.path.isfile(log_filepath):
    log_file = open(log_filepath, "w")
    header_str = "design_file_name,plot_ratio,nshffai,height,height_value,orientation,orientation_value,twist,twist_value,taper,taper_value,slant,slant_value,bend,bend_value,nparms,number_of_surfaces,total_time\n"
    log_file.write(header_str)
else:
    log_file = open(log_filepath, "a")

time1 = time.clock()
for cnt in range(2):
    massing_2_citygml = massing2citygml.Massing2Citygml()
    #first set up the analysis rule necessary for the template rules
    is_shell_closed = analysisrulepalette.IsShellClosed()
    is_shell_in_boundary = analysisrulepalette.IsShellInBoundary()
    shell_boundary_contains = analysisrulepalette.ShellBoundaryContains()
    
    if cnt == 0:
        massing_2_citygml.read_collada(site_dae_file)
        #then set up the template rules and append it into the massing2citygml obj
        id_bldgs = templaterulepalette.IdentifyBuildingMassings()
        id_bldgs.add_analysis_rule(is_shell_closed, True)
        
        id_landuses = templaterulepalette.IdentifyLandUseMassings()
        id_landuses.add_analysis_rule(is_shell_closed, False)
        id_landuses.add_analysis_rule(shell_boundary_contains, True)
        id_landuses.add_analysis_rule(is_shell_in_boundary, True)
        
        id_terrains = templaterulepalette.IdentifyTerrainMassings()
        id_terrains.add_analysis_rule(is_shell_closed, False)
        id_terrains.add_analysis_rule(is_shell_in_boundary, False)
        id_terrains.add_analysis_rule(shell_boundary_contains, True)
        
        massing_2_citygml.add_template_rule(id_bldgs)
        massing_2_citygml.add_template_rule(id_landuses)
        massing_2_citygml.add_template_rule(id_terrains)
        
        #execute the massing2citygml obj
        print "EXECUTE ANALYSIS"
        massing_2_citygml.execute_analysis_rule()
            
        print "#==================================="
        print "WRITING CITYGML ... ...", site_citygml_filepath
        print "#==================================="
        massing_2_citygml.execute_template_rule(site_citygml_filepath)
        
    if cnt == 1:
        massing_2_citygml.read_collada(design_dae_file)
        #then set up the template rules and append it into the massing2citygml obj
        id_bldgs = templaterulepalette.IdentifyBuildingMassings()
        id_bldgs.add_analysis_rule(is_shell_closed, True)
        
        id_landuses = templaterulepalette.IdentifyLandUseMassings()
        id_landuses.add_analysis_rule(is_shell_closed, False)
        id_landuses.add_analysis_rule(shell_boundary_contains, True)
        
        massing_2_citygml.add_template_rule(id_bldgs)
        massing_2_citygml.add_template_rule(id_landuses)
        
        #execute the massing2citygml obj
        print "EXECUTE ANALYSIS"
        massing_2_citygml.execute_analysis_rule()
            
        print "#==================================="
        print "WRITING CITYGML ... ...", design_citygml_filepath
        print "#==================================="
        massing_2_citygml.execute_template_rule(design_citygml_filepath)

time2 = time.clock()
print "#==================================="
print "PARAMETERISING ... ...", design_citygml_filepath
print "#==================================="
#define the parameters
parameterise = gmlparameterise.Parameterise(design_citygml_filepath)
parameters = []
layer_height = 4

if height == True:
    parameters.append(1.0)
    bldg_height_parm = gmlparmpalette.BldgHeightParm()
    bldg_height_parm.define_int_range(0,height_value,1)
    parameterise.add_parm(bldg_height_parm)
    
if taper == True:
    parameters.append(1.0)
    bldg_taper_parm = gmlparmpalette.BldgTaperParm()
    bldg_taper_parm.define_float_range(0.0,taper_value,0.1)
    bldg_taper_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_taper_parm)

if twist == True:
    parameters.append(1.0)
    bldg_twist_parm = gmlparmpalette.BldgTwistParm()
    bldg_twist_parm.define_int_range(0,twist_value,1)
    bldg_twist_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_twist_parm)

if slant == True:
    parameters.append(1.0)
    bldg_slant_parm = gmlparmpalette.BldgSlantParm()
    bldg_slant_parm.define_int_range(0,slant_value,1)
    bldg_slant_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_slant_parm)
    
if bend == True:
    parameters.append(1.0)
    bldg_bend_parm = gmlparmpalette.BldgBendParm()
    bldg_bend_parm.define_int_range(0,bend_value,1)
    bldg_bend_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_bend_parm)

if orientation == True:
    parameters.append(1.0)
    bldg_orientation_parm = gmlparmpalette.BldgOrientationParm()
    bldg_orientation_parm.define_int_range(0,orientation_value,1)
    bldg_orientation_parm.set_clash_detection(False)
    bldg_orientation_parm.set_boundary_detection(False)
    parameterise.add_parm(bldg_orientation_parm)
    
#generate a design variant base on the parameters
nparms = len(parameterise.parm_obj_dict_list)
dv_citygml_file = os.path.join(citygml_dir, design_filename + "dv.gml")
parameterise.generate_design_variant(parameters, dv_citygml_file)

time3 = time.clock()
print "#==================================="
print "EVALUATING MODEL ... ...", dv_citygml_file
print "#==================================="

dae_dir = os.path.join(pef_dir, "dae")
if not os.path.exists(dae_dir):
    os.makedirs(dae_dir)
    
print "#====================================="
print "PERFORMANCE RESULTS"
print "#====================================="
nshffai2_dae_filepath = os.path.join(dae_dir, design_filename + "dv_nshffai.dae")
dv_dae_filepath = os.path.join(dae_dir, design_filename + "dv.dae")
gml3dmodel.citygml2collada(dv_citygml_file, dv_dae_filepath)

evaluations = citygml2eval.Evals(dv_citygml_file)

#evaluate the floor area of the design 
far_list = evaluations.calculate_far(4)
far = round(far_list[0],1)
print "PLOT RATIO:", far

occsolids = evaluations.building_occsolids
total_face_list = []
for occsolid in occsolids:
    face_list = py3dmodel.fetch.topo_explorer(occsolid, "face")
    total_face_list.extend(face_list)

nfaces = len(total_face_list)

luse_face = evaluations.landuse_occpolygons

evaluations.add_shadings_4_solar_analysis(site_citygml_filepath)
xdim = 9
ydim = 9

lower_irrad_threshold = 245#kw/m2
upper_irrad_threshold = 355#kw/m2
roof_irrad_threshold = 1280 #kwh/m2
facade_irrad_threshold = 512 #kwh/m2

res_dict  = evaluations.usffai(lower_irrad_threshold, upper_irrad_threshold, weatherfilepath, xdim, ydim)
nshffai = round(res_dict["afi"],2)
print "NON SOLAR HEATED FACADE TO FLOOR AREA INDEX:", nshffai
d_str = design_filename + "design variant\n" + "NSHFFAI: " + str(nshffai) + "\n" + "Plot Ratio: " + str(far)
py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                               "kWh/m2", nshffai2_dae_filepath, description_str = d_str, 
                                               minval = 263, maxval = 1273, other_occface_list = luse_face)
'''
res_dict = evaluations.pvefai(roof_irrad_threshold, facade_irrad_threshold,weatherfilepath,xdim,ydim)
pvefai = round(res_dict["afi"][0],2)
print "PV ENVELOPE TO FLOOR AREA INDEX :", pvefai
d_str = design_filename + "design variant\n" + "PVEFAI: " + str(pvefai) + "\n" + "Plot Ratio: " + str(far)
py3dmodel.export_collada..write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], "kWh/m2", pv_dae_filepath, 
                                               description_str = d_str, minval = 180, maxval = roof_irrad_threshold, 
                                               other_occface_list = luse_face)
'''
time4 = time.clock()
total_time = (time4-time1)/60.0
print "TOTAL TIME:",  total_time

content_str = design_dae_file + "," + str(far) + "," + str(nshffai)  +","+  str(height) + "," + str(height_value) + "," +\
str(orientation) + "," + str(orientation_value) + "," + str(twist) + "," + str(twist_value) + "," + str(taper) + "," +\
str(taper_value) + "," + str(slant) + "," + str(slant_value) + "," + str(bend) + "," + str(bend_value) + "," +\
str(nparms) + "," + str(nfaces) + "," + str(total_time) + "\n"
log_file.write(content_str)
log_file.close()