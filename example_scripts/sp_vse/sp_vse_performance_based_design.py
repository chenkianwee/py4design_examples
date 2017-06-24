import os
import time
import pyliburo
import ntpath

#====================================================================================================================
#INPUTS
#====================================================================================================================
design_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower.dae"
site_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\site.dae"
weatherfilepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_files\\weatherfile\\SGP_Singapore.486980_IWEC.epw"
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

time1 = time.clock()
for cnt in range(2):
    massing_2_citygml = pyliburo.massing2citygml.Massing2Citygml()
    #first set up the analysis rule necessary for the template rules
    is_shell_closed = pyliburo.analysisrulepalette.IsShellClosed()
    is_shell_in_boundary = pyliburo.analysisrulepalette.IsShellInBoundary()
    shell_boundary_contains = pyliburo.analysisrulepalette.ShellBoundaryContains()
    
    if cnt == 0:
        massing_2_citygml.read_collada(site_dae_file)
        #then set up the template rules and append it into the massing2citygml obj
        id_bldgs = pyliburo.templaterulepalette.IdentifyBuildingMassings()
        id_bldgs.add_analysis_rule(is_shell_closed, True)
        
        id_landuses = pyliburo.templaterulepalette.IdentifyLandUseMassings()
        id_landuses.add_analysis_rule(is_shell_closed, False)
        id_landuses.add_analysis_rule(shell_boundary_contains, True)
        id_landuses.add_analysis_rule(is_shell_in_boundary, True)
        
        id_terrains = pyliburo.templaterulepalette.IdentifyTerrainMassings()
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
        id_bldgs = pyliburo.templaterulepalette.IdentifyBuildingMassings()
        id_bldgs.add_analysis_rule(is_shell_closed, True)
        
        id_landuses = pyliburo.templaterulepalette.IdentifyLandUseMassings()
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
print "EVALUATING MODEL ... ...", design_citygml_filepath
print "#==================================="

dae_dir = os.path.join(pef_dir, "dae")
if not os.path.exists(dae_dir):
    os.makedirs(dae_dir)
    
nshffai2_dae_filepath = os.path.join(dae_dir, design_filename + "nshffai.dae")
pv_dae_filepath = os.path.join(dae_dir, design_filename + "pv.dae")

evaluations = pyliburo.citygml2eval.Evals(design_citygml_filepath)

print "#====================================="
print "PERFORMANCE RESULTS"
print "#====================================="
#evaluate the floor area of the design 
far_list = evaluations.calculate_far(4)
far = round(far_list[0],1)
print "PLOT RATIO:", far

evaluations.add_shadings_4_solar_analysis(site_citygml_filepath)
xdim = 9
ydim = 9

lower_irrad_threshold = 58#kw/m2
upper_irrad_threshold = 364#kw/m2
roof_irrad_threshold = 1280 #kwh/m2
facade_irrad_threshold = 512 #kwh/m2

res_dict  = evaluations.nshffai2(lower_irrad_threshold, upper_irrad_threshold, weatherfilepath, xdim, ydim)

nshffai = round(res_dict["afi"],2)

print "NON SOLAR HEATED FACADE TO FLOOR AREA INDEX:", nshffai
d_str = "NSHFFAI: " + str(nshffai) + "\n" + "Plot Ratio: " + str(far)

pyliburo.utility3d.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                               "kWh/m2", nshffai2_dae_filepath, description_str = d_str, 
                                               minval = 58, maxval = 364)

res_dict = evaluations.pvefai(roof_irrad_threshold, facade_irrad_threshold,weatherfilepath,xdim,ydim)
pvefai = round(res_dict["afi"][0],2)
print "PV ENVELOPE TO FLOOR AREA INDEX :", pvefai

d_str = "PVEFAI: " + str(pvefai) + "\n" + "Plot Ratio: " + str(far)
pyliburo.utility3d.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], "kWh/m2", pv_dae_filepath, 
                                               description_str = d_str, minval = 180, maxval = roof_irrad_threshold)
    
time3 = time.clock()
print "TOTAL TIME:",  (time3-time1)/60.0