import os
import time
from py4design import py3dmodel, shapeattributes, urbangeom, pyoptimise
import collada
from collada import polylist, triangleset
#=================================================================================
#IO
#=================================================================================
result_directory = "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_1"
core_dae = os.path.join(result_directory, "3dmodel", "dae", "core.dae")
site_dae = os.path.join(result_directory, "3dmodel", "dae", "site.dae")
ward_dae = os.path.join(result_directory, "3dmodel", "dae", "ward.dae")
green_dae = os.path.join(result_directory, "3dmodel", "dae", "green.dae")

#=================================================================================
#PARMAETERS
#=================================================================================
parms = [5,6,7,8]

#=================================================================================
#OPTIMSATION PARAMETERS
#=================================================================================
resume = False
ngeneration = 1
init_population = 1
mutation_rate = 0.01
crossover_rate  = 0.8 

live_file = os.path.join(result_directory, "xml", "live.xml")
dead_file = os.path.join(result_directory, "xml", "dead.xml")
#=================================================================================
#FUNCTION
#=================================================================================
def read_collada(dae_file):
    faces = []
    mesh = collada.Collada(dae_file)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist:     
            spyptlist = []
            if primlist:
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        sorted_pyptlist = sorted(pyptlist)
                        
                        if sorted_pyptlist not in spyptlist:
                            spyptlist.append(sorted_pyptlist)
                            occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                            if not py3dmodel.fetch.is_face_null(occpolygon):
                                npts = len(py3dmodel.fetch.points_frm_occface(occpolygon))
                                if npts >=3:
                                    faces.append(occpolygon)
                                            
    cmpd = py3dmodel.construct.make_compound(faces)
    #ref_pt = py3dmodel.calculate.get_centre_bbox(cmpd)
    cmpd = py3dmodel.modify.scale(cmpd,unit, (0,0,0))
    return cmpd

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
    view_edges = []
    for f in facades:
        grids = py3dmodel.construct.grid_face(f, 1, 10)
        pydir = py3dmodel.calculate.face_normal(f)
        total_grids.extend(grids)
        for g in grids:
            is_blocked, edge_list = is_face_blocked(g, pydir, o_face_list)
            if is_blocked:
                bad_faces.append(g)
                view_edges.extend(edge_list)
            else:
                good_faces.append(g)
    
    #py3dmodel.utility.visualise([good_faces, bad_faces, o_solid_list ], ["GREEN", "RED", "WHITE"])
    view_score = len(good_faces)/float(len(total_grids))
    shpatt.set_key_value("view_score", view_score)
    shpatt.set_key_value("good_faces", good_faces)
    shpatt.set_key_value("bad_faces", bad_faces)
    shpatt.set_key_value("view_edges", view_edges)
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
            if mpt!=interpt:
                edge = py3dmodel.construct.make_edge(mpt, interpt)
                edge_list.append(edge)
            blocked = True
            break
        
    return blocked, edge_list

def eval_built_score(shpatt_list):
    builts = []
    for shpatt in shpatt_list:
        if shpatt.dictionary["type"] == "ward":
            face = shpatt.shape
            builts.append(face)
            
    total = len(builts)
    return total

def find_four_pts(core_poly):
    vert_dist = 7.2
    hor_dist = 1.2
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(core_poly)
    vert_dist = ymax-ymin
    vert_dist_half = vert_dist/2.0
    
    midpt = py3dmodel.calculate.face_midpt(core_poly)
    mve_midpt_d = py3dmodel.modify.move_pt(midpt, (0,-1,0), vert_dist_half)
    mve_midpt1 = py3dmodel.modify.move_pt(mve_midpt_d, (-1,0,0), hor_dist)
    mve_midpt2 = py3dmodel.modify.move_pt(mve_midpt_d, (1,0,0), hor_dist)
    
    mve_midpt_t = py3dmodel.modify.move_pt(midpt, (0,1,0), vert_dist_half)
    mve_midpt3 = py3dmodel.modify.move_pt(mve_midpt_t, (-1,0,0), hor_dist)
    mve_midpt4 = py3dmodel.modify.move_pt(mve_midpt_t, (1,0,0), hor_dist)
    
    return [mve_midpt1, mve_midpt2, mve_midpt3, mve_midpt4]
    
def load_options():
    gface_index = [None,None,[1],[0],[1],[0],[1],[0],[0],[2],[1],
                   None,[0],None,[0],[2],[0],[0],[0,3],[0,2]]
    
    shapeatt_list = []
    for option in range(20):
        shpatt = shapeattributes.ShapeAttributes()
        filename = "option" + str(option) + ".dae"
        filepath = os.path.join(result_directory, "3dmodel", "dae","options", filename)
        cmpd = read_collada(filepath)
        mpt = py3dmodel.calculate.get_centre_bbox(cmpd)
        shpatt.set_shape(cmpd)
        shpatt.set_key_value("mpt", mpt)
        shpatt.set_key_value("gface_index", gface_index[option])
        shapeatt_list.append(shpatt)
#        faces = py3dmodel.fetch.topo_explorer(cmpd, "face")
#        txts = []
#        fcnt =0
#        for face in faces:
#            txt_cnt = py3dmodel.construct.make_brep_text(str(fcnt), 1)
#            midpt = py3dmodel.calculate.face_midpt(face)
#            txt_cnt = py3dmodel.modify.move((0,0,0), midpt, txt_cnt)
#            txts.append(txt_cnt)
#            fcnt +=1
#        py3dmodel.utility.visualise([faces, txts],["WHITE", "BLACK"])
    return shapeatt_list
    
def gen_design_variant(parms, core_poly):
    pos_pts = find_four_pts(core_poly)
    green_cmpd = read_collada(green_dae)
    green_poly = py3dmodel.fetch.topo_explorer(green_cmpd, "face")[0]
    green_shp = shapeattributes.ShapeAttributes()
    green_shp.set_shape(green_poly)
    green_shp.set_key_value("type", "green")
    
    ward_cmpd = read_collada(ward_dae)
    ward_poly = py3dmodel.fetch.topo_explorer(ward_cmpd, "face")[0]
    ward_shp = shapeattributes.ShapeAttributes()
    ward_shp.set_shape(ward_poly)
    ward_shp.set_key_value("type", "ward")
    
    shapeatt_list = load_options()
    variant_att = [green_shp, ward_shp]
    #py3dmodel.utility.visualise([[core_poly, green_poly, ward_poly]])
    pcnt =0
    for parm in parms:
        #choose the combi
        shapeatt_list_left = shapeatt_list[0:19]
        shapeatt_list_right = shapeatt_list_left[:]
        shapeatt_list_right[10] = shapeatt_list[19]
        if pcnt == 0:
            shapeatt = shapeatt_list_left[parm]
            opt_cmpd = shapeatt.shape
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(opt_cmpd)
            orig_pt = (xmax,ymax,zmin)
            opt_cmpd = py3dmodel.modify.move(orig_pt, pos_pts[pcnt], opt_cmpd)

        if pcnt == 1:
            shapeatt = shapeatt_list_right[parm]
            opt_cmpd = shapeatt.shape
            mpt = shapeatt.get_value("mpt")
            opt_cmpd = py3dmodel.modify.rotate(opt_cmpd,mpt, (0,1,0),180)
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(opt_cmpd)
            orig_pt = (xmin,ymax,zmin)
            opt_cmpd = py3dmodel.modify.move(orig_pt, pos_pts[pcnt], opt_cmpd)

        if pcnt == 2:
            shapeatt = shapeatt_list_left[parm]
            opt_cmpd = shapeatt.shape
            mpt = shapeatt.get_value("mpt")
            opt_cmpd = py3dmodel.modify.rotate(opt_cmpd,mpt, (1,0,0),180)
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(opt_cmpd)
            orig_pt = (xmax,ymin,zmin)
            opt_cmpd = py3dmodel.modify.move(orig_pt, pos_pts[pcnt], opt_cmpd)
            #py3dmodel.utility.visualise([[opt_cmpd], [core_poly]])

        if pcnt == 3:
            shapeatt = shapeatt_list_right[parm]
            opt_cmpd = shapeatt.shape
            mpt = shapeatt.get_value("mpt")
            opt_cmpd = py3dmodel.modify.rotate(opt_cmpd,mpt, (0,1,0),180)
            mpt =py3dmodel.calculate.get_centre_bbox(opt_cmpd)
            opt_cmpd = py3dmodel.modify.rotate(opt_cmpd,mpt, (1,0,0),180)
            
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(opt_cmpd)
            orig_pt = (xmin,ymin,zmin)
            opt_cmpd = py3dmodel.modify.move(orig_pt, pos_pts[pcnt], opt_cmpd)
            
            
        gface_index = shapeatt.get_value("gface_index")
        faces = py3dmodel.fetch.topo_explorer(opt_cmpd, "face")
        faces_ward = []
        faces_green = []
        if gface_index != None:
            index_list = range(len(faces))
            w_index_list = list(set(index_list) - set(gface_index))
            for index in gface_index:
                faces_green.append(faces[index])
                
            for index in w_index_list:
                faces_ward.append(faces[index])
        else:
            faces_ward = faces[:]
                
        for wf in faces_ward:
            ward_att = shapeattributes.ShapeAttributes()
            ward_att.set_shape(wf)
            ward_att.set_key_value("type", "ward")
            variant_att.append(ward_att)
        for gf in faces_green:
            g_att = shapeattributes.ShapeAttributes()
            g_att.set_shape(gf)
            g_att.set_key_value("type", "green")
            variant_att.append(g_att)
            
        pcnt+=1
    
    return variant_att

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
    
    for gcnt in range(4):
        gene_dict = {}
        gene_dict["type"] = "int_range"
        gene_dict["range"] = [0,18,1]
            
        dict_list.append(gene_dict)
        
    return dict_list

def generate_score_dict_list():
    score1 = {"name":"view", "minmax": "max"}
    score2 = {"name":"built", "minmax": "max"}
    dict_list = [score1, score2]
    return dict_list
    
#=================================================================================
#MAIN SCRIPT
#=================================================================================
print "OPTIMISING ... ..."
time1 = time.clock()

core_cmpd = read_collada(core_dae)
core_poly = py3dmodel.fetch.topo_explorer(core_cmpd, "face")[0]
core_solid = py3dmodel.construct.extrude(core_poly, (0,0,1), 3)

site_cmpd = read_collada(site_dae)
site_poly = py3dmodel.fetch.topo_explorer(site_cmpd, "face")[0]

gene_dict_list = generate_gene_dict_list()
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
        variant_att = gen_design_variant(parms, core_poly)

        #==================================================
        #EVAL DESIGN VARIANT
        #==================================================
        view_score, shpatts = eval_view(variant_att, core_poly, site_poly)
        built_score = eval_built_score(variant_att)
        
        description_string = "design variant" + str(ind_id) + "\n"+ \
                            "view_score:" + str(round(view_score,3)) + "\n"+ \
                            "built_score:" + str(built_score) + "\n"
        
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
                view_edges = shp.get_value("view_edges")
                view_edge_list.extend(view_edges)
            else:
                other_face_list.append(face)
        
        other_face_list.append(core_solid)
        py3dmodel.export_collada.write_2_collada_falsecolour(face_list,vscore_list, "view", dv_dae,
                                                             description_str = description_string, 
                                                             minval = 0.0, maxval = 1.0, 
                                                             other_occface_list = other_face_list + good_face_list+bad_face_list,
                                                             other_occedge_list = view_edge_list)
        
        print "VIEW:", round(view_score,2), "BUILT:", built_score
        
        ind.set_score(0,view_score)
        ind.set_score(1,built_score)
    
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


##py3dmodel.utility.visualise([[core_poly], circles])
#
#shp_list = []
#
#
#
#avg_view_score, shp_list2 = eval_view(variant_att, core_poly, site_poly)
#
#face_list = []
#other_face_list = []
#vscore_list = []
#good_face_list = []
#bad_face_list = []
#view_edge_list = []
#w_cnt = 0
#for shp in shp_list2:
#    face = shp.shape
#    if shp.dictionary["type"] == "ward":
#        vscore = shp.dictionary["view_score"]
#        vscore_list.append(vscore)
#        face_list.append(face)
#        good_faces = shp.get_value("good_faces")
#        good_face_list.extend(good_faces)
#        bad_faces = shp.get_value("bad_faces")
#        bad_face_list.extend(bad_faces)
#        view_edges = shp.get_value("view_edges")
#        view_edge_list.extend(view_edges)
#        w_cnt+=1
#    else:
#        other_face_list.append(face)
#        
#
#print avg_view_score, w_cnt
#
#py3dmodel.utility.visualise([face_list, other_face_list, view_edge_list, bad_face_list, good_face_list], 
#                            ["WHITE", "GREEN", "BLACK", "RED", "BLUE"])
