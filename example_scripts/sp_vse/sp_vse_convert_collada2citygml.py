import time
import pyliburo

filename = "test_tower"
site_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\site.dae"
design_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\" + filename + ".dae"
site_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\site.gml"
design_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\" + filename + ".gml"

time1 = time.clock()
for cnt in range(2):
    massing_2_citygml = pyliburo.massing2citygml.Massing2Citygml()
    if cnt == 0:
        massing_2_citygml.read_collada(site_dae_file)
        citygml_filepath = site_citygml_filepath
    if cnt == 1:
        massing_2_citygml.read_collada(design_dae_file)
        citygml_filepath = design_citygml_filepath
    
    #first set up the analysis rule necessary for the template rules
    is_shell_closed = pyliburo.analysisrulepalette.IsShellClosed()
    is_shell_in_boundary = pyliburo.analysisrulepalette.IsShellInBoundary()
    shell_boundary_contains = pyliburo.analysisrulepalette.ShellBoundaryContains()
    
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
    print "WRITING CITYGML ... ...", citygml_filepath
    print "#==================================="
    massing_2_citygml.execute_template_rule(citygml_filepath)

print "#==================================="
print "PARAMETERISING ... ...", design_citygml_filepath
print "#==================================="

time2 = time.clock()
total_time = (time2-time1)/60
print "TOTAL TIME TAKEN:", total_time

#define the parameters
layer_height = 4
bldg_height_parm = pyliburo.gmlparmpalette.BldgHeightParm()
bldg_height_parm.define_int_range(40,88,4)

bldg_orientation_parm = pyliburo.gmlparmpalette.BldgOrientationParm()
bldg_orientation_parm.define_int_range(0,350,45)
bldg_orientation_parm.set_clash_detection(False)
bldg_orientation_parm.set_boundary_detection(True)

bldg_twist_parm = pyliburo.gmlparmpalette.BldgTwistParm()
bldg_twist_parm.define_int_range(0,90,5)
bldg_twist_parm.define_flr2flr_height(layer_height)

bldg_slant_parm = pyliburo.gmlparmpalette.BldgSlantParm()
bldg_slant_parm.define_int_range(0,20,2)
bldg_slant_parm.define_flr2flr_height(layer_height)

bldg_taper_parm = pyliburo.gmlparmpalette.BldgTaperParm()
bldg_taper_parm.define_float_range(0.5,1.5,0.1)
bldg_taper_parm.define_flr2flr_height(layer_height)

bldg_bend_parm = pyliburo.gmlparmpalette.BldgBendParm()
bldg_bend_parm.define_int_range(0,90,5)
bldg_bend_parm.define_flr2flr_height(layer_height)

#append all the parameters into the parameterise class
parameterise = pyliburo.gmlparameterise.Parameterise(citygml_filepath)
parameterise.add_parm(bldg_height_parm)
parameterise.add_parm(bldg_orientation_parm)
parameterise.add_parm(bldg_twist_parm)
parameterise.add_parm(bldg_taper_parm)
parameterise.add_parm(bldg_slant_parm)
parameterise.add_parm(bldg_bend_parm)


for cnt in range(100):
    parameters = parameterise.generate_random_parameters()
    #parameters = [0.21358148505738006, 0.623653068973939, 0.03392354535880737, 0.23762847666847686, 0.16201434805512738, 0.519238065340125]
    print parameters
    design_variant_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\" + filename + "_res" + str(cnt) +".gml"
    parameterise.generate_design_variant(parameters, design_variant_citygml_filepath)
    print cnt
time3 = time.clock() 
print "TIME TAKEN", (time3-time1)/60.0