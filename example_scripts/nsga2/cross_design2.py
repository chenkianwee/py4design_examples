import os
import time
import math
from py4design import py3dmodel

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
#SWEEP PARAMETERS
#=================================================================================

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
        
def generate_flr_plate(site_coverage, site_xdim, site_ydim, corridor_width):
    site_poly = py3dmodel.construct.make_rectangle(site_xdim, site_ydim)
    site_poly2 = py3dmodel.construct.make_offset(site_poly, corridor_width*-1)
    corridor_poly = py3dmodel.construct.boolean_difference(site_poly, site_poly2)
    
    site_coverage = site_coverage*0.01
    site_area = py3dmodel.calculate.face_area(site_poly)
    open_area = site_area*(1-site_coverage)
    open_area_div = open_area/4
    sq_dim = math.sqrt(open_area_div)
    min_width = 9
    
    bldg_width = site_xdim - (corridor_width*2)
    #bldg_length = site_ydim - (corridor_width*2)
    
    bldg_width2 = bldg_width-(sq_dim*2)
    #bldg_length2 = bldg_length-(sq_dim*2)
    
    if bldg_width2 < min_width:
        n_sq_dim = (bldg_width-9)/2
        n_sq_dim2 = open_area_div/n_sq_dim
        sq_poly = py3dmodel.construct.make_rectangle(n_sq_dim*2, n_sq_dim2*2)
    else:
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
    
def generate_design_variant(site_coverage, n_storeys, site_xdim, site_ydim, corridor_width):
    flrplates = []
    sc_calc_list = []
    
    flrplate_poly, site_coverage_calc = generate_flr_plate(site_coverage, site_xdim,
                                                           site_ydim, corridor_width)
    cnt = 0
    for storey in range(n_storeys):
        flrplate_poly2 = py3dmodel.modify.move((0,0,0), (0,0,cnt*3),flrplate_poly)
        flrplate_poly2 = py3dmodel.fetch.topo_explorer(flrplate_poly2, "face")[0]
        flrplates.append(flrplate_poly2)
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

#=================================================================================
#MAIN SCRIPT
#=================================================================================
print "SWEEPING ... ..."
time1 = time.clock()
sc_list = range(site_coverage_range[0], site_coverage_range[1], site_coverage_range[2])

for sc in sc_list:
    print sc
    flrplates, sc_calc_list = generate_design_variant(sc, n_storeys, site_xdim, 
                                                      site_ydim, corridor_width)
    #print len(flrplates)
    #py3dmodel.utility.visualise([flrplates])
    dv_dae = os.path.join(result_directory, "variant", "dae", str(sc) + ".dae")
    #==================================================
    #EVAL DESIGN VARIANT
    #==================================================
    ventday = eval_ventday(flrplates)
    plot_ratio, gfa = eval_plot_ratio(flrplates, site_area)
    
    description_string = "design variant" + str(sc) + "\n"+ \
                        "perimeter/flr_area:" + str(round(ventday,3)) + "\n"+ \
                        "plot_ratio:" + str(round(plot_ratio,2)) + "\n"
    
    py3dmodel.export_collada.write_2_collada(dv_dae, occface_list = flrplates, 
                                             text_string = description_string)
    
    print "Perimeter/Area:", round(ventday,3), "Plot Ratio:", round(plot_ratio,2)
    
print "DONE"
time3 = time.clock() 
print "TIME TAKEN", (time3-time1)/60.0