import os
import time
from py4design import py3dmodel, shapeattributes, urbangeom, pyoptimise
import networkx as nx
#=================================================================================
#IO
#=================================================================================
result_directory = "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_test"
#=================================================================================
#CONSTRAINTS
#=================================================================================
#corridor_width = 3
npu = 16
pu_xdim = 6
pu_ydim = 12.5

#n_storeys = 10
site_xdim = 43.4
site_ydim = 56.6
site_area = site_xdim*site_ydim

core_xdim = 18.8
core_ydim = 14.4

grid_xdim = 1
grid_ydim = 1
#=================================================================================
#OPTIMSATION PARAMETERS
#=================================================================================
resume = True
ngeneration = 200
init_population = 50
mutation_rate = 0.01
crossover_rate  = 0.8 

live_file = os.path.join(result_directory, "xml", "live.xml")
dead_file = os.path.join(result_directory, "xml", "dead.xml")

#=================================================================================
#FUNCTIONS
#=================================================================================      
def gen_planning_grid(grid_xdim, grid_ydim, site_xdim, site_ydim, 
                      core_xdim, core_ydim, pu_xdim, pu_ydim):
    site_poly = py3dmodel.construct.make_rectangle(site_xdim, site_ydim)
    core_poly = py3dmodel.construct.make_rectangle(core_xdim, core_ydim)
    max_pudim = max([pu_xdim, pu_ydim])
    offset_site_poly = py3dmodel.construct.make_offset(site_poly, max_pudim/2*-1 )
    grids = py3dmodel.construct.grid_face(offset_site_poly, grid_xdim, grid_ydim)
    new_grids = []
    for g in grids:
        diff = py3dmodel.construct.boolean_difference(g, core_poly)
        is_null = py3dmodel.fetch.is_compound_null(diff)
        if not is_null:
            diff_face = py3dmodel.fetch.topo_explorer(diff, "face")[0]
            new_grids.append(diff_face)
    
    #py3dmodel.utility.visualise([new_grids, [site_poly]])
    return new_grids, site_poly, core_poly, grids
    
def gen_random_parms(npu):
    import random
    parms = []
    random.seed()
    green2ward_def = [0,100,10]
    green2ward_range = range(green2ward_def[0],green2ward_def[1]+1, green2ward_def[2])
    green2ward = random.choice(green2ward_range)*0.01
    parms.append(green2ward)
    
    rot_range = range(0,360,90)
    for i in range(npu*2):
        if i%2 == 0:
            rot = random.choice(rot_range)
            parms.append(rot)
        elif i%2 == 1:
            pos = random.random()
            parms.append(pos)
            
    return parms
    
def gen_flr_plate(parms, planning_grids, site_poly, core_poly, pu_xdim, pu_ydim, npu, route_grids):
    green_parm = parms[0]*0.01
    green_parm = int(round(green_parm*npu))
    
    parms2 = parms[1:]
    pu_poly = py3dmodel.construct.make_rectangle(pu_xdim, pu_ydim)
    pu_midpt = py3dmodel.calculate.face_midpt(pu_poly)
    
    ngrids = len(planning_grids)
    rot_pus = []
    pos_parms = []
    pcnt = 0
    for parm in parms2:
        if pcnt%2 == 0:
            rot_pu_poly = py3dmodel.modify.rotate(pu_poly, pu_midpt, (0,0,1), parm)
            rot_pu_poly = py3dmodel.fetch.topo2topotype(rot_pu_poly)
            rot_pus.append(rot_pu_poly)
        elif pcnt%2 == 1:
            pos_parm = int(round(parm*ngrids))
            pos_parms.append(pos_parm)
        pcnt+=1
    
    g_midpts = []
    for grid in planning_grids:
        midpt = py3dmodel.calculate.face_midpt(grid)
        g_midpts.append(midpt)
        
    posed_polys = rearrange_pos(rot_pus,g_midpts, site_poly, pos_parms, 
                                other_occface =[core_poly] )
    
    corridor_wires = gen_corridor(posed_polys, core_poly, route_grids)
    
    shpatt_list = []
    green_polys = posed_polys[0:green_parm]
    ward_polys = posed_polys[green_parm:]
    for gpoly in green_polys:
        shpatt = shapeattributes.ShapeAttributes()
        shpatt.set_shape(gpoly)
        shpatt.set_key_value("type", "green")
        shpatt_list.append(shpatt)
    
    for wpoly in ward_polys:
        shpatt = shapeattributes.ShapeAttributes()
        shpatt.set_shape(wpoly)
        shpatt.set_key_value("type", "ward")
        shpatt_list.append(shpatt)
    
    for wire in corridor_wires:
        shpatt = shapeattributes.ShapeAttributes()
        shpatt.set_shape(wire)
        shpatt.set_key_value("type", "corridor")
        shpatt_list.append(shpatt)
        
    return shpatt_list
    
    
def gen_corridor(occface_list, core_poly, route_grids):
    occface_list2 = occface_list[:]
    occface_list2.append(core_poly)
    dest_pt = []
    extra_edges = []
    rmv_grids_index = []
    for of2 in occface_list2:
        midpt = py3dmodel.calculate.face_midpt(of2)
        dest_pt.append(midpt)
        gcnt = 0
        for g in route_grids:
            is_inside = py3dmodel.calculate.point_in_face(midpt, g)
            if is_inside:
                pyptlist = py3dmodel.fetch.points_frm_occface(g)
                rmv_grids_index.append(gcnt)
                for pypt in pyptlist:
                    edge = py3dmodel.construct.make_edge(pypt, midpt)
                    extra_edges.append(edge)
                    
                break
            gcnt+=1
            
    total_grid_index = range(len(route_grids))
    remain_grid_index = list(set(total_grid_index) - set(rmv_grids_index))
    pln_edges = []
    for index in remain_grid_index:
        r_face = route_grids[index]
        rmidpt = py3dmodel.calculate.face_midpt(r_face)
        pyptlist = py3dmodel.fetch.points_frm_occface(r_face)
        r_edges = py3dmodel.fetch.topo_explorer(r_face, "edge")
        pln_edges.extend(r_edges)
        for pypt in pyptlist:
            edge = py3dmodel.construct.make_edge(pypt, rmidpt)
            pln_edges.append(edge)
    
    edges4_networkx = pln_edges + extra_edges
    G = make_networkxg(edges4_networkx)
    
    tri_faces = py3dmodel.construct.delaunay3d(dest_pt)
    w_cmpd = py3dmodel.construct.make_compound(tri_faces)
    w_edges = py3dmodel.fetch.topo_explorer(w_cmpd, "edge")
    G2 = make_networkxg(w_edges)
    T = nx.minimum_spanning_tree(G2, weight="distance")
    min_edges = T.edges
    min_wires = []
    for e in min_edges:
        shortest_path =  nx.shortest_path(G, source = e[0], target = e[1], weight = "distance")
        min_wire = py3dmodel.construct.make_wire(shortest_path)
        min_wires.append(min_wire)
    
    w_cmpd2 = py3dmodel.construct.make_compound(min_wires)
    w_edges2 = py3dmodel.fetch.topo_explorer(w_cmpd2, "edge")
    G3 = make_networkxg(w_edges2)
    min_wires2 = []
    combi_list = []
    pcnt = 0
    for pt in dest_pt:
        dest_pt2 = dest_pt[:]
        del dest_pt2[pcnt]
        for pt2 in dest_pt2:
            shortest_path2 =  nx.shortest_path(G3, source = pt, target = pt2, weight = "distance")
            wire = py3dmodel.construct.make_wire(shortest_path2)
            w_length = py3dmodel.calculate.wirelength(wire)
            crow_dist = py3dmodel.calculate.distance_between_2_pts(pt, pt2)
            rdi =  w_length/crow_dist
            if rdi > 2.5:
                if [pt, pt2] not in combi_list and [pt2,pt] not in combi_list:
                    shortest_path3 =  nx.shortest_path(G, source = pt, target = pt2, weight = "distance")
                    wire2 = py3dmodel.construct.make_wire(shortest_path3)
                    min_wires2.append(wire2)
                    min_wires.append(wire2)
                    w_cmpd2 = py3dmodel.construct.make_compound(min_wires)
                    w_edges2 = py3dmodel.fetch.topo_explorer(w_cmpd2, "edge")
                    G3 = make_networkxg(w_edges2)
                    combi_list.append([pt, pt2])
            
        pcnt+=1
        
    
    #py3dmodel.utility.visualise([ min_wires, occface_list2], 
                                #["RED", 'WHITE'])
    return min_wires
                
def make_networkxg(edges4_networkx):
    #create a graph
    G = nx.Graph()
    #add all the edges for the boundary
    for ne in edges4_networkx:
        edge_nodes = py3dmodel.fetch.points_frm_edge(ne)
        if len(edge_nodes) == 2:
            xdmin,xdmax = py3dmodel.fetch.edge_domain(ne)
            length = py3dmodel.calculate.edgelength(xdmin,xdmax,ne)
            node1 = edge_nodes[0]
            node2 = edge_nodes[1]
            G.add_edge(node1,node2, distance = length)
    return G

def rearrange_pos(occface_list, grid_midpts, site_poly, parameters, other_occface = [], 
                  clash_detection = True, boundary_detection = True):

    moved_faces = []
    n_other_occfaces = len(other_occface)
    moved_faces.extend(other_occface)
    npypt_list = len(grid_midpts)
    nfaces = len(occface_list)
    for cnt in range(nfaces):      
        occface = occface_list[cnt]
        pos_parm = parameters[cnt]
        loc_pt = py3dmodel.calculate.face_midpt(occface)
        
        isclash = True
        for clash_cnt in range(npypt_list):
            #print "clash_cnt", clash_cnt
            #map the location point to the grid points
            mpt_index = pos_parm+clash_cnt
            if mpt_index >= npypt_list-1:
                mpt_index = mpt_index-(npypt_list) 
                
            moved_pt = grid_midpts[mpt_index]
            moved_face = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(loc_pt, moved_pt, occface))
            #=======================================================================================
            if clash_detection == True and boundary_detection == False:
                if moved_faces:
                    clash_detected = detect_clash(moved_face, moved_faces)                    
                    if not clash_detected:
                        #means there is no intersection and there is no clash
                        #print "I am not clashing onto anyone!!!"
                        isclash = False
                        break
                
                else:
                    isclash = False
                    break
                
            #=======================================================================================
            elif boundary_detection == True and clash_detection == False:
                is_in_boundary = detect_in_boundary(moved_face, site_poly)
                if is_in_boundary:
                    isclash = False
                    break
            #=======================================================================================
            elif boundary_detection == True and clash_detection == True:
                #need to check if the moved building is within the boundaries of the landuse 
                is_in_boundary = detect_in_boundary(moved_face, site_poly)
                    
                if is_in_boundary:
                    #test if it clashes with the other buildings 
                    if moved_faces:
                        clash_detected = detect_clash(moved_face, moved_faces)                    
                        if not clash_detected:
                            #print "I am not clashing onto anyone!!!"
                            isclash = False
                            break
                    
                    else:
                        isclash = False
                        break
            #=======================================================================================  
            elif clash_detection == False and boundary_detection == False:
                isclash = False
                break
            
        if isclash == True:
            print "unable to position this face"
        
        if isclash == False:
            #print "successfully positioned the building"
            moved_faces.append(moved_face)
            
    if other_occface:
        moved_faces = moved_faces[n_other_occfaces:]
    print "successfully positioned the face"
    return moved_faces

def detect_clash(occface, other_occfaces):
    for of in other_occfaces:
        common_compound = py3dmodel.construct.boolean_common(occface, of)
        is_cmpd_null = py3dmodel.fetch.is_compound_null(common_compound)
        if is_cmpd_null == False:
            return True
    return False
    
def detect_in_boundary(occface, site_occface):
    diff_cmpd = py3dmodel.construct.boolean_difference(occface, site_occface)
    is_cmpd_null = py3dmodel.fetch.is_compound_null(diff_cmpd)
    return is_cmpd_null

def eval_built_score(shpatt_list):
    builts = []
    for shpatt in shpatt_list:
        if shpatt.dictionary["type"] == "ward" or shpatt.dictionary["type"] == "green":
            face = shpatt.shape
            builts.append(face)
            
    total = len(builts)
    return total

def eval_corridor_dist(shpatt_list):
    lengths = []
    for shpatt in shpatt_list:
        if shpatt.dictionary["type"] == "corridor":
            wire = shpatt.shape
            length = py3dmodel.calculate.wirelength(wire)
            lengths.append(length)
            
    total = sum(lengths)
    return total

def eval_view(shpatt_list, core_poly, site_poly):
    ward_shpatts = []
    green_shpatts = []
    for shpatt in shpatt_list:
        if shpatt.dictionary["type"] == "ward":
            ward_shpatts.append(shpatt)
        else:
            green_shpatts.append(shpatt)
            
    view_score_list = []
    wcnt = 0
    for wshp in ward_shpatts:
        ward_shpatts2 = ward_shpatts[:]
        del ward_shpatts2[wcnt]
        view_score = eval_view_p_ward(wshp, ward_shpatts2, core_poly)
        #print view_score
        view_score_list.append(view_score)
        wcnt += 1
    
    avg_view_score = sum(view_score_list)/len(view_score_list)
    return avg_view_score, green_shpatts + ward_shpatts
        
def eval_view_p_ward(shpatt, other_shpatts, core_poly):
    height = 3
    core_solid = py3dmodel.construct.extrude(core_poly, (0,0,1), height)
    cfacades, croofs, cfloors = urbangeom.identify_building_surfaces(core_solid)
    o_face_list = []
    o_face_list.extend(cfacades)
    for oshp in other_shpatts:
        o_occface = oshp.shape
        o_solid = py3dmodel.construct.extrude(o_occface, (0,0,1), height)
        ofacades, oroofs, ofloors = urbangeom.identify_building_surfaces(o_solid)
        o_face_list.extend(ofacades)
    
    occface = shpatt.shape
    solid = py3dmodel.construct.extrude(occface, (0,0,1), height)
    facades, roofs, floors = urbangeom.identify_building_surfaces(solid)   
    total_grids = []
    good_faces = []
    bad_faces = []
    #view_edges = []
    for f in facades:
        grids = py3dmodel.construct.grid_face(f, 1, 10)
        pydir = py3dmodel.calculate.face_normal(f)
        total_grids.extend(grids)
        for g in grids:
            is_blocked, edge_list = is_face_blocked(g, pydir, o_face_list)
            if is_blocked:
                bad_faces.append(g)
                #view_edges.extend(edge_list)
            else:
                good_faces.append(g)
    
    #py3dmodel.utility.visualise([good_faces, bad_faces, o_solid_list ], ["GREEN", "RED", "WHITE"])
    view_score = len(good_faces)/float(len(total_grids))
    shpatt.set_key_value("view_score", view_score)
    shpatt.set_key_value("good_faces", good_faces)
    shpatt.set_key_value("bad_faces", bad_faces)
    #shpatt.set_key_value("view_edges", view_edges)
    return view_score

def is_face_blocked(occface, pydir, other_faces):
    edge_list = []
    mpt = py3dmodel.calculate.face_midpt(occface)
    blocked = False
    for of in other_faces:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(of,mpt, pydir)
        if interpt:
            #it means it cant see the boundary and blocked
            #draw an edge
            #edge = py3dmodel.construct.make_edge(mpt, interpt)
            #edge_list.append(edge)
            blocked = True
            break
        
    return blocked, edge_list

#================================================================================
#OPTIMISATION ALGORITHM FUNCTIONS
#================================================================================
def generate_gene_dict_list(npu):
    '''
    4 types of genes 
    float_range
    float_choice
    int_range
    int_choice
    '''
    green2ward_def = [0,50,10]
    rot_def = [0,360,45]
    pos_def = [0,1]
    dict_list = []
    
    gene_dict1 = {}
    gene_dict1["type"] = "int_range"
    gene_dict1["range"] = green2ward_def
    dict_list.append(gene_dict1)
    
    for gcnt in range(npu*2):
        gene_dict = {}
        if gcnt%2 == 0:
            gene_dict["type"] = "int_range"
            gene_dict["range"] = rot_def
        if gcnt%2 == 1:
            gene_dict["type"] = "float_range"
            gene_dict["range"] = pos_def
            
        dict_list.append(gene_dict)
        
    return dict_list

def generate_score_dict_list():
    score1 = {"name":"view", "minmax": "max"}
    score2 = {"name":"built", "minmax": "max"}
    score3 = {"name":"corridor", "minmax": "min"}
    dict_list = [score1, score2, score3]
    return dict_list

#=================================================================================
#MAIN SCRIPT
#=================================================================================
print "OPTIMISING ... ..."
time1 = time.clock()

pln_grid, site_poly, core_poly, route_grids = gen_planning_grid(grid_xdim, grid_ydim, site_xdim, site_ydim, 
                                                               core_xdim, core_ydim, pu_xdim, pu_ydim)

core_solid = py3dmodel.construct.extrude(core_poly, (0,0,1), 3)
facades, roofs, floors = urbangeom.identify_building_surfaces(core_solid)

gene_dict_list = generate_gene_dict_list(npu)
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
        posed_shpatt_list = gen_flr_plate(parms, pln_grid, site_poly, core_poly, 
                                          pu_xdim, pu_ydim, npu, route_grids)
        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        view_score, shpatts = eval_view(posed_shpatt_list, core_poly, site_poly)
        built_score = eval_built_score(posed_shpatt_list)
        corridor_dist = eval_corridor_dist(posed_shpatt_list)
        
        description_string = "design variant" + str(ind_id) + "\n"+ \
                            "view_score:" + str(round(view_score,3)) + "\n"+ \
                            "built_score:" + str(built_score) + "\n" + \
                            "corridor_score" + str(round(corridor_dist,2)) + "\n"
        
        face_list = []
        other_face_list = []
        vscore_list = []
        good_face_list = []
        bad_face_list = []
        view_edge_list = []
        corridor_edge_list = []
        for shp in shpatts:
            face = shp.shape
            if shp.dictionary["type"] == "ward":
                vscore = shp.dictionary["view_score"]
                vscore_list.append(vscore)
                face_list.append(face)
                good_faces = shp.get_value("good_faces")
                good_face_list.extend(good_faces)
                bad_faces = shp.get_value("bad_faces")
                bad_face_list.extend(bad_faces)
                #view_edges = shp.get_value("view_edges")
                #view_edge_list.extend(view_edges)
            elif shp.dictionary["type"] == "corridor":
                edges = py3dmodel.fetch.topo_explorer(face, "edge")
                corridor_edge_list.extend(edges)
            else:
                other_face_list.append(face)
        
        other_face_list.extend(facades)
        other_face_list.extend(floors)
        py3dmodel.export_collada.write_2_collada_falsecolour(face_list,vscore_list, "view", dv_dae,
                                                             description_str = description_string, 
                                                             minval = 0.0, maxval = 1.0, 
                                                             other_occface_list = other_face_list + good_face_list+bad_face_list,
                                                             other_occedge_list = corridor_edge_list)
        
        print "VIEW:", round(view_score,2), "BUILT:", built_score, "CORRIDOR:", round(corridor_dist,2)
        
        ind.set_score(0,view_score)
        ind.set_score(1,built_score)
        ind.set_score(2,corridor_dist)
    
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