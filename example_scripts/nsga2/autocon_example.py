from pyliburo import py3dmodel
from pyliburo import gml3dmodel
from pyliburo import py2radiance
from pyliburo import utility3d
from pyliburo import buildingformeval
from pyliburo import runopt
import time

#setup the parametric model
def generate_design_variant(ftprint_pt1, ftprint_pt2, ftprint_pt3, ftprint_pt4, courtyard_size, wwr, shade_strategy):
    #constraints
    npts_grid_edge = 5
    #procedure
    #first generate the grid
    grid_occface = py3dmodel.construct.make_rectangle(80, 60)
    occedge_list = py3dmodel.fetch.geom_explorer(grid_occface, "edge")
    
    edge_pt_list = []
    pts_grid_edge_list = [ftprint_pt1, ftprint_pt2, ftprint_pt3, ftprint_pt4 ]
    #subdivide the edge into equal distance points
    edge_cnt = 0
    for occedge in occedge_list:
        lbound, ubound = py3dmodel.fetch.edge_domain(occedge)
        domain_range = ubound-lbound
        interval = domain_range/float(npts_grid_edge-1)
        i = pts_grid_edge_list[edge_cnt]
        u = lbound+(i*interval)
        edge_pt = py3dmodel.calculate.edgeparameter2pt(u, occedge)
        edge_pt_list.append(edge_pt)
        edge_cnt += 1
        
    ftprint = py3dmodel.construct.make_polygon(edge_pt_list)
    ftprint =  py3dmodel.modify.reverse_face(ftprint)
    #generate the courtyard
    ftprint_midpt = find_footprint_midpt(ftprint)
    courtyard = py3dmodel.modify.uniform_scale(ftprint,courtyard_size, courtyard_size, courtyard_size, ftprint_midpt)
    #fullfill the floor area requirement, far of 3.5
    flr_area_requirement = 16800
   
    ftprint_area = py3dmodel.calculate.face_area(ftprint)
    
    flr_area = ftprint_area
    flr2flr_height = 4.0
    wall_list = []
    flr_list = []
    roof_list = []
    win_list = []
    bldg_shade_list = []
    
    fcnt = 0
    while flr_area < flr_area_requirement:
        loc_pt = py3dmodel.modify.move_pt(ftprint_midpt, (0,0,1), flr2flr_height*fcnt)
        
        nxt_flr = py3dmodel.modify.move(ftprint_midpt,loc_pt, ftprint)
        nxt_flr = py3dmodel.fetch.shape2shapetype(nxt_flr)
        
        nxt_courtyard = py3dmodel.modify.move(ftprint_midpt,loc_pt, courtyard)
        nxt_courtyard = py3dmodel.fetch.shape2shapetype(nxt_courtyard)
        
        flr_courtyard = py3dmodel.construct.boolean_difference(nxt_flr, nxt_courtyard)
        flr_courtyard = py3dmodel.fetch.geom_explorer(flr_courtyard, "face")[0]
        flr_list.append(flr_courtyard)
        
        extruded_flr = py3dmodel.construct.extrude(nxt_flr, (0,0,1), flr2flr_height)
        external_wall_list, up_list, down_list = gml3dmodel.identify_building_surfaces(extruded_flr)
        
        extruded_courtyard = py3dmodel.construct.extrude(nxt_courtyard, (0,0,1), flr2flr_height)
        courtyard_wall_list, up_list, down_list = gml3dmodel.identify_building_surfaces(extruded_courtyard)
        
        for external_wall in external_wall_list:
            ew_midpt = py3dmodel.calculate.face_midpt(external_wall)
            external_win = py3dmodel.modify.uniform_scale(external_wall, 0.98, 0.98, wwr/0.98, ew_midpt)
            external_win = py3dmodel.fetch.shape2shapetype(external_win)
            win_list.append(external_win)
            tri_external_wall = triangulate_wall_with_hole(external_wall, external_win)
            wall_list.extend(tri_external_wall)
            #create the shade
            if shade_strategy !=0:
                shade_list = create_win_shades(external_win)
                bldg_shade_list.extend(shade_list)
                
        for courtyard_wall in courtyard_wall_list:
            courtyard_wall = py3dmodel.modify.reverse_face(courtyard_wall)
            cw_midpt = py3dmodel.calculate.face_midpt(courtyard_wall)
            courtyard_win = py3dmodel.modify.uniform_scale(courtyard_wall, 0.98, 0.98, wwr/0.98, cw_midpt)
            courtyard_win = py3dmodel.fetch.shape2shapetype(courtyard_win)
            win_list.append(courtyard_win)
            tri_courtyard_wall = triangulate_wall_with_hole(courtyard_wall, courtyard_win)
            wall_list.extend(tri_courtyard_wall)
            #create the shade
            if shade_strategy ==2:
                shade_list = create_win_shades(courtyard_win)
                bldg_shade_list.extend(shade_list)
            
        if fcnt!=0:
            nxt_flr_area = py3dmodel.calculate.face_area(flr_courtyard)
            flr_area = flr_area + nxt_flr_area
        fcnt+=1
    
    nflrs = len(flr_list)
    loc_pt = py3dmodel.modify.move_pt(ftprint_midpt, (0,0,1), nflrs*flr2flr_height)   
    roof = py3dmodel.modify.move(ftprint_midpt, loc_pt, flr_list[0])
    roof =  py3dmodel.fetch.shape2shapetype(roof)
    roof = py3dmodel.modify.reverse_face(roof)
    roof_list.append(roof)
    
    return wall_list, flr_list, roof_list, win_list, bldg_shade_list
    
def triangulate_wall_with_hole(wall, window):
    wall_occface = py3dmodel.construct.boolean_difference(wall,window)
    wall_occface = py3dmodel.fetch.geom_explorer(wall_occface, "face")[0]
    new_tri_occface_list = triangulate_face(wall_occface)
    return new_tri_occface_list

def triangulate_face(occface):
    tri_occface_list = py3dmodel.construct.simple_mesh(occface)
    fnrml = py3dmodel.calculate.face_normal(occface)
    new_tri_occface_list = []
    for tri_face in tri_occface_list:
        tri_nrml = py3dmodel.calculate.face_normal(tri_face)
        tri_nrml = (round(tri_nrml[0],2), round(tri_nrml[1],2), round(tri_nrml[2],2))
        if tri_nrml != fnrml:
            reversed_face = py3dmodel.modify.reverse_face(tri_face)
            new_tri_occface_list.append(reversed_face)
        else:
            new_tri_occface_list.append(tri_face)
            
    return new_tri_occface_list
    
def create_win_shades(win):
    nrml = py3dmodel.calculate.face_normal(win)
    shade_extrude = py3dmodel.construct.extrude(win,nrml,1)
    vert_list, shade_list, down_list = gml3dmodel.identify_building_surfaces(shade_extrude)
    return shade_list
                
def find_footprint_midpt(occface):
    edge_list= py3dmodel.fetch.geom_explorer(occface,"edge")
    midpt_list = []
    for edge in edge_list:
        lbound, ubound = py3dmodel.fetch.edge_domain(edge)
        domain_range = ubound-lbound
        midpt = lbound + (domain_range/2.0)
        edge_midpt = py3dmodel.calculate.edgeparameter2pt(midpt, edge)
        midpt_list.append(edge_midpt)
        
    #draw intersection edges
    edge1 = py3dmodel.construct.make_edge(midpt_list[0], midpt_list[2])
    edge2 = py3dmodel.construct.make_edge(midpt_list[1], midpt_list[3])
    midpt_list = py3dmodel.calculate.intersect_edge_with_edge(edge1, edge2)
    return midpt_list[0]
    
def eval_daylight(wall_list, flr_list, roof_list, win_list, bldg_shade_list, win_srfmat_parm, dae_filepath):
    rad_base_filepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo\\py2radiance\\base.rad"
    rad_folderpath = "F:\\design_variants\\rad_data"
    daysim_folderpath = "F:\\design_variants\\daysim_data"
    epwweatherfile = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_files\\weatherfile\\SGP_Singapore.486980_IWEC.epw"
    
    rad = py2radiance.Rad(rad_base_filepath, rad_folderpath)
    opaque_srfmat = "light_painted_concrete"
    if win_srfmat_parm == 0:
        win_srfmat = "single_clr_6mm_uvalue_5.25_sc0.9_glass"
    if win_srfmat_parm == 1:
        win_srfmat = "bca_dblglz_uncoated_glass"
    if win_srfmat_parm == 2:
        win_srfmat = "bca_dblglz_reflective_lowe_glass"
        
    total_sensor_srf_list = []
    total_sensor_pt_list = []
    total_sensor_dir_list = []
    
    mid_level = int(len(flr_list)/2)
    chosen_flr = flr_list[mid_level]
    reversed_flr = py3dmodel.modify.reverse_face(chosen_flr)
    flr_midpt = py3dmodel.calculate.face_midpt(reversed_flr)
    loc_pt = py3dmodel.modify.move_pt(flr_midpt, (0,0,1), 0.8)
    moved_flr = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(flr_midpt, loc_pt, reversed_flr))
    #offset_flr = py3dmodel.construct.make_offset(moved_flr, 0.5)
    sensor_surfaces, sensor_pts, sensor_dirs = gml3dmodel.generate_sensor_surfaces(moved_flr,2,2)
    total_sensor_srf_list.extend(sensor_surfaces)
    total_sensor_pt_list.extend(sensor_pts)
    total_sensor_dir_list.extend(sensor_dirs)
    rad.set_sensor_points(total_sensor_pt_list, total_sensor_dir_list)
    rad.create_sensor_input_file()
    
    #triangulate the roof and floor
    rf_list = flr_list + roof_list
    tri_rf_list = []
    for rf in rf_list:
        tri_face = triangulate_face(rf)
        tri_rf_list.extend(tri_face)
    
    #create the scene for radiance
    opaque_srf_list = wall_list + bldg_shade_list + tri_rf_list
    srf_cnt = 0
    for opaque_srf in opaque_srf_list:
        pypolygon = py3dmodel.fetch.pyptlist_frm_occface(opaque_srf)
        srfname = "opaque" + str(srf_cnt)
        py2radiance.RadSurface(srfname, pypolygon, opaque_srfmat, rad)
        #reverse the opaque srf
        reversed_opaque = py3dmodel.modify.reverse_face(opaque_srf)
        r_pypolygon = py3dmodel.fetch.pyptlist_frm_occface(reversed_opaque)
        r_srfname = "opaque_reverse" + str(srf_cnt)
        py2radiance.RadSurface(r_srfname, r_pypolygon, opaque_srfmat, rad)
        srf_cnt +=1
        
    win_cnt = 0
    for win in win_list:
        pypolygon = py3dmodel.fetch.pyptlist_frm_occface(win)
        srfname = "win" + str(win_cnt)
        py2radiance.RadSurface(srfname, pypolygon, win_srfmat, rad)
        #reverse the opaque srf
        reversed_win = py3dmodel.modify.reverse_face(win)
        r_pypolygon = py3dmodel.fetch.pyptlist_frm_occface(reversed_win)
        r_srfname = "win_reverse" + str(win_cnt)
        py2radiance.RadSurface(r_srfname, r_pypolygon, win_srfmat, rad)
        win_cnt +=1
    rad.create_rad_input_file()
    
    #execute radiance 
    time_range = str(0) + " " + str(24)
    date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
    rad.execute_cumulative_oconv(time_range, date, epwweatherfile, output = "illuminance")
    #execute cumulative_rtrace
    rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
    #retrieve the results
    illum_ress = rad.eval_cumulative_rad(output = "illuminance")  
    rad.initialise_daysim(daysim_folderpath)
    #a 60min weatherfile is generated
    rad.execute_epw2wea(epwweatherfile)
    sunuphrs = rad.sunuphrs
    #ge the mean_illum_ress
    mean_illum_ress = []
    useful_ill_list = []
    for illum in illum_ress:
        mean_illum = illum/float(sunuphrs)
        if 2000>mean_illum >=300:
            useful_ill_list.append(mean_illum)
        mean_illum_ress.append(mean_illum)
    
    cmpd = py3dmodel.construct.make_compound(opaque_srf_list+win_list)
    edges = py3dmodel.fetch.geom_explorer(cmpd, "edge")
    daylight_level = float(len(useful_ill_list))/float(len(mean_illum_ress))
    d_str = "% of floor area > 300lx: " + str(daylight_level)
    utility3d.write_2_collada_falsecolour(total_sensor_srf_list, mean_illum_ress, "lx", 
                                          dae_filepath, description_str = d_str,
                                          minval = 87.5, maxval = 2212.5,
                                          other_occedge_list = edges)
        
    return daylight_level

def eval_cooling_energy(wall_list, flr_list, roof_list, win_list, bldg_shade_list, win_srfmat_parm):
    epwweatherfile = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_files\\weatherfile\\SGP_Singapore.486980_IWEC.epw"
    
    if win_srfmat_parm == 0:
        win_uvalue = 5.2
        win_sc = 0.72
    if win_srfmat_parm == 1:
        win_uvalue = 2.82
        win_sc = 0.81
    if win_srfmat_parm == 2:
        win_uvalue = 1.6
        win_sc = 0.33
    
    shp_attribs_list = []
    for wall in wall_list:
        shp_attribs = buildingformeval.create_opaque_srf_shape_attribute(wall,2.3,"wall" )
        shp_attribs_list.append(shp_attribs)
        
    for roof in roof_list:
        tri_roof_list = triangulate_face(roof)
        for tri_roof in tri_roof_list:
            shp_attribs = buildingformeval.create_opaque_srf_shape_attribute(tri_roof,2.3,"roof" )
            shp_attribs_list.append(shp_attribs)
    
    for window in win_list:
        shp_attribs = buildingformeval.create_glazing_shape_attribute(window,win_uvalue,win_sc,"window")
        shp_attribs_list.append(shp_attribs)
        
    for shade in bldg_shade_list:
        shp_attribs = buildingformeval.create_shading_srf_shape_attribute(shade, "shade")
        shp_attribs_list.append(shp_attribs)
    
    flr_area = 0
    for footprint in flr_list:
        area = py3dmodel.calculate.face_area(footprint)
        flr_area = flr_area + area
        shp_attribs = buildingformeval.create_shading_srf_shape_attribute(footprint, "footprint")
        shp_attribs_list.append(shp_attribs)
        
        
    ettv_dict = buildingformeval.calc_ettv(shp_attribs_list,epwweatherfile)
    system_dict_list = buildingformeval.calc_cooling_energy_consumption(ettv_dict["facade_area"], ettv_dict["roof_area"],
                                                     flr_area, ettv_dict["ettv"], ettv_dict["rttv"])
    chosen_system = buildingformeval.choose_efficient_cooling_system(system_dict_list)[0]
    return chosen_system, ettv_dict, flr_area
#================================================================================
#OPTIMISATION ALGORITHM FUNCTIONS
#================================================================================
def generate_gene_dict_list():
    '''
    4 types of genes 
    float_range
    float_choice
    int_range
    int_choice
    '''
    dict_list = []
    #for choosing the four courners
    for _ in range(4):
        gene_dict = {}
        gene_dict["type"] = "int_range"
        gene_dict["range"] = (0,4,1)
        dict_list.append(gene_dict)
        
    #scaling factor for hte courtyard size
    for _ in range(1):
        gene_dict = {}
        gene_dict["type"] = "float_range"
        gene_dict["range"] = (0.3,0.7,0.1)
        dict_list.append(gene_dict)
        
    #the window wall ratio
    for _ in range(1):
        gene_dict = {}
        gene_dict["type"] = "float_range"
        gene_dict["range"] = (0.3,0.9,0.1)
        dict_list.append(gene_dict)
    
    #the shading strategy
    for _ in range(1):
        gene_dict = {}
        gene_dict["type"] = "int_range"
        gene_dict["range"] = (0,3,1)
        dict_list.append(gene_dict)
        
    #the window materials
    for _ in range(1):
        gene_dict = {}
        gene_dict["type"] = "int_range"
        gene_dict["range"] = (0,3,1)
        dict_list.append(gene_dict)
        
    return dict_list
    
def generate_score_dict_list():
    score1 = {"name":"cooling_energy", "minmax": "min"}
    score2 = {"name":"daylight", "minmax": "max"}
    dict_list = [score1, score2]
    return dict_list
#================================================================================================================
#main script
#================================================================================================================
time1 = time.clock()

#================================================================================
#INSTRUCTION: ADVANCE OPTIMISATION PARAMETERS
#================================================================================
resume = True
ngeneration = 7
init_population = 100
mutation_rate = 0.01
crossover_rate  = 0.8 
live_file =  "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\live.xml"
dead_file =   "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\dead.xml"

print "OPTIMISING ... ..."
gene_dict_list = generate_gene_dict_list()
score_dict_list = generate_score_dict_list()

if resume == False:
    population = runopt.initialise_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
if resume == True:
    population = runopt.resume_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
              live_file,dead_file )
    
for gencnt in range(ngeneration):
    indlist = population.individuals
    print "CURRENT GEN", gencnt
    for ind in indlist:
        #==================================================
        #GENERATE DESIGN VARIANT
        #=================================================
        ind_id = ind.id
        dv_dae = "F:\\design_variants\\" + str(ind_id) + ".dae"
        dv_dae_daylight = "F:\\design_variants\\daylight\\" + str(ind_id) + "daylight.dae"
        parms = ind.genotype.values
        pt1 = parms[0]
        pt2 = parms[1]
        pt3 = parms[2]
        pt4 = parms[3]
        courtyard_size = parms[4]
        wwr = parms[5]
        shade_strategy = parms[6]
        win_mat = parms[7]
        
        wall_list, flr_list, roof_list, win_list, bldg_shade_list = generate_design_variant(pt1, pt2, pt3, pt4,
                                                                                            courtyard_size, wwr, 
                                                                                            shade_strategy) 
                                                                                            
        
        
        all_srf_list =  wall_list + bldg_shade_list
        
        for roof in roof_list:
            tri_roof_list = triangulate_face(roof)
            all_srf_list.extend(tri_roof_list)
            
        for floor in flr_list:
            tri_floor_list = triangulate_face(floor)
            all_srf_list.extend(tri_floor_list)
            
        cmpd1 = py3dmodel.construct.make_compound(all_srf_list)
        
        if win_mat == 0:
            win_colour = (0,1,1)
        if win_mat == 1:
            win_colour = (0,0.5,1)
        if win_mat == 2:
            win_colour = (0,0,1)
            
        cmpd2 = py3dmodel.construct.make_compound(win_list)
        cmpd_list = [cmpd1, cmpd2]
        rgb_colour_list = [(1,1,1), win_colour]
        
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        system_dict, ettv_dict, flr_area = eval_cooling_energy(wall_list, flr_list, roof_list, win_list, bldg_shade_list, win_mat)
        daylight = eval_daylight(wall_list, flr_list, roof_list, win_list, bldg_shade_list,win_mat, dv_dae_daylight)
        cooling_energy = system_dict["energy_consumed_yr_m2"]
        
        description_string = "test"

        ettv = ettv_dict["ettv"]
        roof_area = ettv_dict["roof_area"]
        facade_area = ettv_dict["facade_area"]
        envelope_area = roof_area + facade_area
        shape_factor = envelope_area/flr_area
        
        sensible_load = system_dict["sensible_load"]
        cooling_system = system_dict["cooling_system"]
        
        description_string = "design variant" + str(ind_id) + "\n"+ \
                            "Cooling Energy (kWh/m2/yr):" + str(round(cooling_energy,2)) + "\n"+ \
                            "Daylight (% <300 >2000):" + str(round(daylight,2)) + "\n" + \
                            "footprint_pt1:" + str(pt1) + "\n" + \
                            "footprint_pt2:" + str(pt2) + "\n" + \
                            "footprint_pt3:" + str(pt3) + "\n" + \
                            "footprint_pt4:" + str(pt4) + "\n" + \
                            "courtyard_size:" + str(courtyard_size) + "\n" + \
                            "wwr:" + str(wwr) + "\n" + \
                            "shade_strategy:" + str(shade_strategy) + "\n" + \
                            "win_mat:" + str(win_mat) + "\n" + \
                            "Cooling System:" + cooling_system + "\n" + \
                            "Sensible Load (W):" + str(round(sensible_load,2)) + "\n" + \
                            "ettv:" + str(round(ettv,2)) + "\n" + \
                            "flr_area:" + str(round(flr_area,2)) + "\n" + \
                            "shape_factor:" + str(round(shape_factor,2)) + "\n"
                            
        if cooling_system == 'Radiant Panels & DVUs':
            supply_temperature = system_dict["supply_temperature_for_panels"]
            panel_srf_area = system_dict["required_panel_area"]
            ndvus = system_dict["required_dvus"] 
        else:
            supply_temperature = 0
            panel_srf_area = 0
            ndvus = 0
            
        description_string2 = "supply_temperature:" + str(supply_temperature) + "\n" + \
                                "panel_srf_area:" + str(round(panel_srf_area,2)) + "\n" + \
                                "ndvus:" + str(ndvus) + "\n"
        description_string = description_string + description_string2

        
        utility3d.write_2_collada_text_string(cmpd_list, description_string, dv_dae, face_rgb_colour_list=rgb_colour_list)
        print 'COOLING ENERGY', cooling_energy , "DAYLIGHT", daylight
        ind.set_score(0,cooling_energy)
        ind.set_score(1,daylight)
        derivedparams = [ettv, shape_factor, sensible_load, flr_area, cooling_system,
                         supply_temperature, panel_srf_area, ndvus]
        ind.add_derivedparams(derivedparams)
        
    #==================================================
    #NSGA FEEDBACK 
    #=================================================
    print "FEEDBACK ... ..."
    runopt.feedback_nsga2(population)
    time2 = time.clock() 
    print "TIME TAKEN", (time2-time1)/60.0
    
print "DONE"
time3 = time.clock() 
print "TIME TAKEN", (time3-time1)/60.0

#glazing materials
#0 =  sgl clear glass, vt 0.9, 1 = dbl glaze no coat, vt 0.79, 
#2 = dbl glaze reflective lowe vt 0.6, 3 = frit glass low e vt 0.38
#opaque wall is concrete 


