import os
import time
import pyliburo
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files", "auto_parm_example","citygml", "5x5ptblks.gml")

'''citygml_filepath = "C://file2analyse.gml"
result_citygml_filepath = "C://result.gml'''

#================================================================================
#INSTRUCTION: ADVANCE OPTIMISATION PARAMETERS
#================================================================================
resume = True
ngeneration = 20
init_population = 100
mutation_rate = 0.01
crossover_rate  = 0.8 
live_file =  os.path.join(parent_path, "example_files","auto_parm_example", "nsga2_xml", "live.xml")
dead_file =  os.path.join(parent_path, "example_files","auto_parm_example", "nsga2_xml", "dead.xml")

time1 = time.clock() 
#================================================================================
#EVALUATION FUNCTIONS
#================================================================================
def eval_solar(citygml_filepath):
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    xdim = 9
    ydim = 9
    weatherfilepath = os.path.join(parent_path, "example_files","weatherfile", "SGP_Singapore.486980_IWEC.epw")
    '''
    illum threshold (lux)
    '''
    illum_threshold = 10000
    avg_dfavi, dfavi_percent, dfai, topo_list, illum_ress = evaluations.dfavi(illum_threshold,weatherfilepath,xdim,ydim)    
    '''
    irrad threshold (kwh/m2)
    '''
    irrad_threshold = (50*4549)/1000.0#kw/m2
    avg_shgfavi, shgfavi_percent, shgfai, topo_list, irrad_ress  = evaluations.shgfavi(irrad_threshold,weatherfilepath,xdim,ydim)
    
    return shgfai, dfai

def eval_density(citygml_filepath):
    read_citygml = pyliburo.pycitygml.Reader()
    read_citygml.load_filepath(citygml_filepath)
    buildings = read_citygml.get_buildings()    
    flr2flr_height = 3.0
    luse_area = 136900.010404
    flr_area_list = []
    for building in buildings:
        bsolid = pyliburo.gml3dmodel.get_building_occsolid(building, read_citygml)
        footprint = pyliburo.gml3dmodel.get_bldg_footprint_frm_bldg_occsolid(bsolid)[0]
        footprint_area = pyliburo.py3dmodel.calculate.face_area(footprint)
        bldg_height = pyliburo.gml3dmodel.calculate_bldg_height(bsolid)
        levels = bldg_height/flr2flr_height
        ttl_flr_area = footprint_area*levels
        flr_area_list.append(ttl_flr_area)
        
    luse_flr_area = sum(flr_area_list)
    far = luse_flr_area/luse_area
    return far
    
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
    shg_score = {"name":"shgfai", "minmax": "min"}
    dfai_score = {"name":"dfai", "minmax": "max"}
    far_score = {"name":"far", "minmax": "max"}
    dict_list = [shg_score, dfai_score, far_score]
    return dict_list
    
print "PARAMETERISING ... ..."
#================================================================================
#PARAMETERISE THE FILE
#================================================================================
#define the parameters
#bldg_height_parm = pyliburo.gmlparmpalette.BldgFlrAreaHeightParm()
#bldg_height_parm.define_int_range(3,10,1)

bldg_height_parm = pyliburo.gmlparmpalette.BldgHeightParm()
bldg_height_parm.define_int_range(30,90,3)

bldg_orientation_parm = pyliburo.gmlparmpalette.BldgOrientationParm()
bldg_orientation_parm.define_int_range(0,350,10)
bldg_orientation_parm.set_clash_detection(True)
bldg_orientation_parm.set_boundary_detection(True)

bldg_pos_parm = pyliburo.gmlparmpalette.BldgPositionParm()
bldg_pos_parm.set_xdim_ydim(10,10)
bldg_pos_parm.set_boundary_detection(True)
bldg_pos_parm.set_clash_detection(True)

#append all the parameters into the parameterise class
parameterise = pyliburo.gmlparameterise.Parameterise(citygml_filepath)
parameterise.add_parm(bldg_height_parm)
parameterise.add_parm(bldg_orientation_parm)
parameterise.add_parm(bldg_pos_parm)
parameterise.define_nparameters()
nparms = parameterise.nparameters
print nparms

print "OPTIMISING ... ..."
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
    print "CURRENT GEN", gencnt
    for ind in indlist:
        #==================================================
        #GENERATE DESIGN VARIANT
        #=================================================
        ind_id = ind.id
        dv_citygml = os.path.join(parent_path, "example_files", "auto_parm_example","design_variants", str(ind_id) + ".gml")
        parameters = ind.genotype.values
        parameterise.generate_design_variant(parameters, dv_citygml)
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        shgfai, dfai = eval_solar(dv_citygml)
        far = eval_density(dv_citygml)
        print 'SHGFAI', shgfai, "DFAI", dfai, "FAR", far
        ind.set_score(0,shgfai)
        ind.set_score(1,dfai)
        ind.set_score(2, far)
        
    #==================================================
    #NSGA FEEDBACK 
    #=================================================
    print "FEEDBACK ... ..."
    pyliburo.runopt.feedback_nsga2(population)
    time2 = time.clock() 
    print "TIME TAKEN", (time2-time1)/60.0
    
print "DONE"
time3 = time.clock() 
print "TIME TAKEN", (time3-time1)/60.0