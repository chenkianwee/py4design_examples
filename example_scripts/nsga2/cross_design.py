import os
import time
import math
from py4design import py3dmodel, pyoptimise

#=================================================================================
#IO
#=================================================================================
result_directory = "F:\\kianwee_work\\nus\\201804-201810\\farm\\result"

#=================================================================================
#PARAMETERS
#=================================================================================
site_coverage_range = [55, 90, 5]
#=================================================================================
#CONSTRAINTS
#=================================================================================
n_storeys = 10
site_xdim = 43.4
site_ydim = 56.6
site_area = site_xdim*site_ydim
corridor_width = 3

#=================================================================================
#OPTIMSATION PARAMETERS
#=================================================================================
resume = False
ngeneration = 100
init_population = 100
mutation_rate = 0.01
crossover_rate  = 0.8 

live_file = os.path.join(result_directory, "xml", "live.xml")
dead_file = os.path.join(result_directory, "xml", "dead.xml")

#=================================================================================
#FUNCTIONS
#=================================================================================
def generate_random_parameters(site_coverage_range, n_storeys):
    site_coverage_range2 = range(site_coverage_range[0], site_coverage_range[1]+1, site_coverage_range[2])
    
    import random
    parameters = []
    for _ in range(n_storeys):
        sc = random.choice(site_coverage_range2)
        parameters.append(sc)
    
    #print parameters
    return parameters
        
def generate_flr_plate( site_coverage, site_xdim, site_ydim, corridor_width):
    site_poly = py3dmodel.construct.make_rectangle(site_xdim, site_ydim)
    site_poly2 = py3dmodel.construct.make_offset(site_poly, corridor_width*-1)
    corridor_poly = py3dmodel.construct.boolean_difference(site_poly, site_poly2)
    
    site_coverage = site_coverage*0.01
    site_area = py3dmodel.calculate.face_area(site_poly)
    open_area = site_area*(1-site_coverage)
    open_area_div = open_area/4
    sq_dim = math.sqrt(open_area_div)
    
    sq_poly = py3dmodel.construct.make_rectangle(sq_dim*2, sq_dim*2)
    sq_poly_area = py3dmodel.calculate.face_area(sq_poly)
    sq_polys = []
    for _ in range(4):
        scale_factor = open_area_div/(sq_poly_area/4)
        sq_poly2 = py3dmodel.modify.scale(sq_poly, math.sqrt(scale_factor), (0,0,0))
        sq_polys.append(sq_poly2)
        
    site_pyptlist = py3dmodel.fetch.points_frm_occface(site_poly2)
    mv_sq_polys = []
    scnt = 0
    for site_pt in site_pyptlist:
        sq_poly = sq_polys[scnt]
        mv_sq_poly = py3dmodel.modify.move((0,0,0), site_pt, sq_poly)
        site_poly2 = py3dmodel.construct.boolean_difference(site_poly2, mv_sq_poly)
        mv_sq_polys.append(mv_sq_poly)
        scnt +=1
    
    built_area = py3dmodel.calculate.face_area(site_poly2) + py3dmodel.calculate.face_area(corridor_poly)
    site_coverage_calc = built_area/site_area
    site_poly2 = py3dmodel.fetch.topo_explorer(site_poly2, "face")[0]
    return site_poly2, site_coverage_calc
    
def generate_design_variant(parameters, n_storeys, site_xdim, site_ydim, corridor_width):
    flrplates = []
    sc_calc_list = []
    cnt = 0
    for storey in range(n_storeys):
        site_coverage = parameters[cnt]
        flrplate_poly, site_coverage_calc = generate_flr_plate(site_coverage, site_xdim, 
                                                               site_ydim, corridor_width)
        sc_calc_list.append(site_coverage_calc)
        flrplate_poly = py3dmodel.modify.move((0,0,0), (0,0,cnt*3),flrplate_poly)
        flrplate_poly = py3dmodel.fetch.topo_explorer(flrplate_poly, "face")[0]
        flrplates.append(flrplate_poly)
        cnt+=1
        
    return flrplates, sc_calc_list

def eval_ventday(flrplates):
    perimeters = []
    areas = []
    ventdays = []
    for flrplate in flrplates:
        wire = py3dmodel.fetch.wires_frm_face(flrplate)[0]
        perimeter = py3dmodel.calculate.wirelength(wire)
        perimeters.append(perimeter)
        area = py3dmodel.calculate.face_area(flrplate)
        areas.append(area)
        ventday = perimeter/area
        ventdays.append(ventday)
    
    avg_ventday = sum(ventdays)/len(ventdays)
    return avg_ventday

def eval_plot_ratio(flrplates, site_area):
    areas = []
    for flrplate in flrplates:
        area = py3dmodel.calculate.face_area(flrplate)
        areas.append(area)
    
    total_area = sum(areas)
    plot_ratio = total_area/site_area
    return plot_ratio, total_area

#================================================================================
#OPTIMISATION ALGORITHM FUNCTIONS
#================================================================================
def generate_gene_dict_list(site_coverage_range, n_storeys):
    '''
    4 types of genes 
    float_range
    float_choice
    int_range
    int_choice
    '''
    dict_list = []
    #for choosing the four courners
    for _ in range(n_storeys):
        gene_dict = {}
        gene_dict["type"] = "int_range"
        gene_dict["range"] = site_coverage_range
        dict_list.append(gene_dict)
        
    return dict_list

def generate_score_dict_list():
    score1 = {"name":"vent_day", "minmax": "max"}
    score2 = {"name":"plot_ratio", "minmax": "max"}
    dict_list = [score1, score2]
    return dict_list

#=================================================================================
#MAIN SCRIPT
#=================================================================================
print "OPTIMISING ... ..."
time1 = time.clock()

gene_dict_list = generate_gene_dict_list(site_coverage_range, n_storeys)
score_dict_list = generate_score_dict_list()

if resume == False:
    population = pyoptimise.initialise_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
if resume == True:
    population = pyoptimise.resume_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )

for gencnt in range(ngeneration):
    indlist = population.individuals
    print "CURRENT GEN", gencnt
    for ind in indlist:
        #==================================================
        #GENERATE DESIGN VARIANT
        #=================================================
        ind_id = ind.id
        dv_dae = os.path.join(result_directory, "variant", "dae", str(ind_id) + ".dae")
        parms = ind.genotype.values
        flrplates, sc_calc_list = generate_design_variant(parms, n_storeys, site_xdim, site_ydim, corridor_width)
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        ventday = eval_ventday(flrplates)
        plot_ratio, gfa = eval_plot_ratio(flrplates, site_area)
        
        description_string = "design variant" + str(ind_id) + "\n"+ \
                            "perimeter/flr_area:" + str(round(ventday,3)) + "\n"+ \
                            "plot_ratio:" + str(round(plot_ratio,2)) + "\n"
        
        py3dmodel.export_collada.write_2_collada(dv_dae, occface_list = flrplates, 
                                                 text_string = description_string)
        
        print "Perimeter/Area:", round(ventday,3), "Plot Ratio:", round(plot_ratio,2)
        
        ind.set_score(0,ventday)
        ind.set_score(1,plot_ratio)
        derivedparams = [gfa]
        ind.add_derivedparams(derivedparams)
        
    #==================================================
    #NSGA FEEDBACK 
    #=================================================
    print "FEEDBACK ... ..."
    pyoptimise.feedback_nsga2(population)
    time2 = time.clock() 
    print "TIME TAKEN", (time2-time1)/60.0
    
print "DONE"
time3 = time.clock() 
print "TIME TAKEN", (time3-time1)/60.0