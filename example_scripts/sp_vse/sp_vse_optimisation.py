import time
import os
import ntpath
import pyliburo

#====================================================================================================================
#INPUTS
#====================================================================================================================
design_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower.dae"
site_dae_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\site.dae"
weatherfilepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_files\\weatherfile\\SGP_Singapore.486980_IWEC.epw"

#configure the parameterisation
height = True
height_value_range = [120,194,4]

orientation = True
orientation_value_range = [0,350,45]

twist = True
twist_value_range = [0,90,5] 

taper = True
taper_value_range = [1.0, 2.0, 0.1]

slant = True
slant_value_range = [0, 30, 3]

bend = True
bend_value_range = [0,90,5]
#====================================================================================================================
#INPUTS
#====================================================================================================================

#====================================================================================================================
#MAIN SCRIPT PLEASE DO NOT ALTER ANYTHING
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
print "PARAMETERISING ... ...", design_citygml_filepath
print "#==================================="
#define the parameters
parameterise = pyliburo.gmlparameterise.Parameterise(design_citygml_filepath)
layer_height = 4

if height == True:
    bldg_height_parm = pyliburo.gmlparmpalette.BldgHeightParm()
    bldg_height_parm.define_int_range(height_value_range[0],height_value_range[1],height_value_range[2])
    parameterise.add_parm(bldg_height_parm)

if orientation == True:
    bldg_orientation_parm = pyliburo.gmlparmpalette.BldgOrientationParm()
    bldg_orientation_parm.define_int_range(orientation_value_range[0],orientation_value_range[1],orientation_value_range[2])
    bldg_orientation_parm.set_clash_detection(False)
    bldg_orientation_parm.set_boundary_detection(True)
    parameterise.add_parm(bldg_orientation_parm)

if twist == True:
    bldg_twist_parm = pyliburo.gmlparmpalette.BldgTwistParm()
    bldg_twist_parm.define_int_range(twist_value_range[0],twist_value_range[1],twist_value_range[2])
    bldg_twist_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_twist_parm)

if taper == True:
    bldg_taper_parm = pyliburo.gmlparmpalette.BldgTaperParm()
    bldg_taper_parm.define_float_range(taper_value_range[0],taper_value_range[1],taper_value_range[2])
    bldg_taper_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_taper_parm)
    
if slant == True:
    bldg_slant_parm = pyliburo.gmlparmpalette.BldgSlantParm()
    bldg_slant_parm.define_int_range(slant_value_range[0],slant_value_range[1],slant_value_range[2])
    bldg_slant_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_slant_parm)
    
if bend == True:
    bldg_bend_parm = pyliburo.gmlparmpalette.BldgBendParm()
    bldg_bend_parm.define_int_range(bend_value_range[0],bend_value_range[1],bend_value_range[2])
    bldg_bend_parm.define_flr2flr_height(layer_height)
    parameterise.add_parm(bldg_bend_parm)
    
parameterise.define_nparameters()
nparms = parameterise.nparameters
print nparms


print "#==================================="
print "OPTIMISING ... ...", design_citygml_filepath
print "#==================================="

resume = False
ngeneration = 10
init_population = 25
mutation_rate = 0.1
crossover_rate  = 0.8 

#generate the design variant directory
dv_dir = os.path.join(pef_dir, "design_variant")
if not os.path.exists(dv_dir):
    os.makedirs(dv_dir)

xml_dir = os.path.join(pef_dir, "xml")
if not os.path.exists(xml_dir):
    os.makedirs(xml_dir)
    
live_file = os.path.join(xml_dir, "live.xml")
open(live_file, "w").close()
dead_file =   os.path.join(xml_dir, "dead.xml")
open(dead_file, "w").close()

#================================================================================
#OPTIMISATION ALGORITHM FUNCTIONS
#================================================================================
def generate_gene_dict_list(ngenes):
    '''
    4 types of genes 
    float_range
    float_choice
    int_range
    int_choice
    '''
    dict_list = []
    for _ in range(ngenes):
        gene_dict = {}
        gene_dict["type"] = "float_range"
        gene_dict["range"] = (0.0,1.0)
        dict_list.append(gene_dict)
    return dict_list
    
def generate_score_dict_list():
    nsh_score = {"name":"nshffai", "minmax": "max"}
    pv_score = {"name":"pvefai", "minmax": "max"}
    dict_list = [nsh_score, pv_score]
    return dict_list
    
#================================================================================
#EVALUATION FUNCTIONS
#================================================================================
def eval_solar(citygml_filepath, weatherfilepath, dv_dir, ind_id):
    nshffai2_dae_filepath = os.path.join(dv_dir, str(ind_id) + "dv_nshffai.dae")
    pv_dae_filepath = os.path.join(dv_dir, str(ind_id) + "dv_pv.dae")
    
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    
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
                                                   minval = 58, maxval = 1000)
    
    res_dict = evaluations.pvefai(roof_irrad_threshold, facade_irrad_threshold,weatherfilepath,xdim,ydim)
    pvefai = round(res_dict["afi"][0],2)
    print "PV ENVELOPE TO FLOOR AREA INDEX :", pvefai
    
    d_str = "PVEFAI: " + str(pvefai) + "\n" + "Plot Ratio: " + str(far)
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], "kWh/m2", pv_dae_filepath, 
                                                   description_str = d_str, minval = 180, maxval = roof_irrad_threshold)

    return nshffai, pvefai 

#================================================================================
#OPTIMISE THE DESIGN
#================================================================================
gene_dict_list = generate_gene_dict_list(nparms)
score_dict_list = generate_score_dict_list()

if resume == False:
    population = pyliburo.runopt.initialise_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
if resume == True:
    population = pyliburo.runopt.resume_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
    
for gencnt in range(ngeneration):
    indlist = population.individuals
    time3 = time.clock()
    print "CURRENT GEN", gencnt
    for ind in indlist:
        #==================================================
        #GENERATE DESIGN VARIANT
        #=================================================
        ind_id = ind.id
        parameters = ind.genotype.values
        dv_citygml = os.path.join(dv_dir, str(ind_id) + ".gml")
        parameterise.generate_design_variant(parameters, dv_citygml)
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        nshffai, pvefai = eval_solar(dv_citygml, weatherfilepath, dv_dir, ind_id)
        ind.set_score(0,nshffai)
        ind.set_score(1,pvefai)
        
    #==================================================
    #NSGA FEEDBACK 
    #=================================================
    print "FEEDBACK ... ..."
    pyliburo.runopt.feedback_nsga2(population)
    time4 = time.clock() 
    print "TIME TAKEN PER GENERATION", (time4-time3)/60.0
    
print "DONE"
time5 = time.clock() 
print "TOTAL TIME TAKEN", (time5-time1)/60.0