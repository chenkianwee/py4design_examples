import time
import pyliburo
import random
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
citygml_filepath = "F:\\kianwee_work\\case_study\\auto_parm_example\\citygml\\5x5ptblks2.gml"

'''citygml_filepath = "C://file2analyse.gml"
result_citygml_filepath = "C://result.gml'''

#================================================================================
#INSTRUCTION: ADVANCE OPTIMISATION PARAMETERS
#================================================================================
resume = True
ngeneration = 20
init_population = 25
mutation_rate = 0.01
crossover_rate  = 0.8 
live_file =  "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\live.xml"
dead_file =   "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\dead.xml"

time1 = time.clock() 
#================================================================================
#EVALUATION FUNCTIONS
#================================================================================
def eval_solar(citygml_filepath):
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    xdim = 9
    ydim = 9
    weatherfilepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_files\\weatherfile\\SGP_Singapore.486980_IWEC.epw"
    '''
    irrad threshold (kwh/m2)
    '''
    irrad_threshold = (50*4549)/1000.0#kw/m2
    res_dict  = evaluations.nshffai(irrad_threshold,weatherfilepath,xdim,ydim)
    return res_dict["ai"]

def eval_fai(citygml_filepath):
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    wind_dir = (1,1,0)
    res_dict = evaluations.fai(wind_dir)
    return res_dict["average"]
    
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
    nsh_score = {"name":"shgfai", "minmax": "max"}
    dfai_score = {"name":"fai", "minmax": "min"}
    dict_list = [nsh_score, dfai_score]
    return dict_list
    
print "PARAMETERISING ... ..."
#================================================================================
#PARAMETERISE THE FILE
#================================================================================
#define the parameters
bldg_height_parm = pyliburo.gmlparmpalette.BldgFlrAreaHeightParm()
bldg_height_parm.define_int_range(3,10,1)

#bldg_height_parm = pyliburo.gmlparmpalette.BldgHeightParm()
#bldg_height_parm.define_int_range(30,90,3)

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
        dv_citygml = "F:\\kianwee_work\\case_study\\auto_parm_example\\design_variants\\" + str(ind_id) + ".gml"
        parameters = ind.genotype.values
        parameterise.generate_design_variant(parameters, dv_citygml)
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        nshfai = eval_solar(dv_citygml)
        fai =  eval_fai(dv_citygml)
        print 'NSHFAI', nshfai, "FAI", fai
        ind.set_score(0,nshfai)
        ind.set_score(1,fai)
        
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