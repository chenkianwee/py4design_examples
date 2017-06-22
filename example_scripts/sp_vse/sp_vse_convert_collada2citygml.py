import time
import pyliburo


site_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\site.dae"
design_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2.dae"
site_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\site.gml"
design_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\test_tower2.gml"
#design_variant_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\test_tower_res.gml"

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
bldg_height_parm = pyliburo.gmlparmpalette.BldgHeightParm()
bldg_height_parm.define_int_range(40,80,4)

bldg_orientation_parm = pyliburo.gmlparmpalette.BldgOrientationParm()
bldg_orientation_parm.define_int_range(0,350,10)
bldg_orientation_parm.set_clash_detection(False)
bldg_orientation_parm.set_boundary_detection(True)

bldg_twist_parm = pyliburo.gmlparmpalette.BldgTwistParm()
bldg_twist_parm.define_int_range(0,90,5)
bldg_twist_parm.define_flr2flr_height(4)

bldg_bend_parm = pyliburo.gmlparmpalette.BldgBendParm()
bldg_bend_parm.define_int_range(0,90,5)
bldg_bend_parm.define_flr2flr_height(4)

#append all the parameters into the parameterise class
parameterise = pyliburo.gmlparameterise.Parameterise(citygml_filepath)
parameterise.add_parm(bldg_height_parm)
parameterise.add_parm(bldg_orientation_parm)
parameterise.add_parm(bldg_twist_parm)
parameterise.add_parm(bldg_bend_parm)

for cnt in range(10):
    parameters = parameterise.generate_random_parameters()
    #parameters = [0.3884060551286753, 0.2420593187795531, 0.630990932565577, 0.4406287061645846]
    #parameters = [0.1087480259695543, 0.11741306342602364, 0.17541402323153532, 0.28934495193261356]
    #parameters = [0.07732975637179462, 0.9816693833334377, 0.43137778216553857, 0.6150097081703361]
    #parameters = [0.8047426004822341, 0.698679189051934, 0.7931828730644793] # dont work
    #parameters = [0.6521894144684426, 0.5103187645188341, 0.0865283523816307] #works
    #parameters = [0.5, 0.6, 0.8, 0.2]
    print parameters
    design_variant_citygml_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\citygml\\test_tower2_res " + str(cnt) +".gml"
    parameterise.generate_design_variant(parameters, design_variant_citygml_filepath)
    
    print cnt
time3 = time.clock() 
print "TIME TAKEN", (time3-time1)/60.0