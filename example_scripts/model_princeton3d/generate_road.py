import os
import time

from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile
#==============================================================
#SPECIFY THE RESULT DIRECTORY
#==============================================================
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context"
filename = "impervious_surface_xx.brep"
#===========================================================================================
#SPECIFY THE GRID AND SURFACE SHP FILE
#===========================================================================================
grid_shpfile = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_context_grid\\princeton_context_grid_10by10km.shp"
srf_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\roads_2015_princeton\\roads_2015_princeton.shp"
#srf_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\others_2015_princeton\\others_2015_princeton.shp"
#==============================================================
#SPECIFY THE TERRAIN DIRECTORY
#==============================================================
terrain_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrains"
#==============================================================
#SPECIFY IF YOU WANT TO SEE THE RESULT AT THE END OF THE SCRIPT
#==============================================================
viewer = True
#===========================================================================================
#FUNCTION
#===========================================================================================
def read_sf_poly(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    rcnt = 0
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occfaces = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            for occface in occfaces:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(occface)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
        rcnt+=1
                
    return shpatt_list
        
def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)
        
def make_bdry_face2d(mn_mx_list):
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face

def get_all_terrain(terrain_dir):
    n_terrains = 420
    t_list = []
    for i in range(n_terrains):
        t_filename = "terrain_10by10km_pt_" + str(i) + ".brep"
        t_filepath = os.path.join(terrain_dir, t_filename)
        terrain = py3dmodel.utility.read_brep(t_filepath)
        t_list.append(terrain)
    return t_list 

def identify_terrain(grid, terrain_list):
    identified = []
    for terrain in terrain_list:
        xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(terrain)
        t_face = make_bdry_face2d([xmin, ymin, zmin, xmax, ymax, zmax])
        common = py3dmodel.construct.boolean_common(t_face, grid)
        if not py3dmodel.fetch.is_compound_null(common):
            identified.append(terrain)
    return identified

def generate_tin(terrain_list):
    vlist = []
    for terrain in terrain_list:
        vs = py3dmodel.fetch.topo_explorer(terrain, "vertex")
        vlist.extend(vs)
    
    occpt_list = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
    pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpt_list)
    tri = py3dmodel.construct.delaunay3d(pyptlist)
    shell_list = py3dmodel.construct.sew_faces(tri)
    shell = shell_list[0]
    return shell

def identify_roads(grid, road_list):
    identified = []
    for road in road_list:
        xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(road)
        r_face = make_bdry_face2d([xmin, ymin, zmin, xmax, ymax, zmax])
        common = py3dmodel.construct.boolean_common(r_face, grid)
        if not py3dmodel.fetch.is_compound_null(common):
            identified.append(road)
    return identified

def separate_face_holes(occface):
    wire_list =  py3dmodel.fetch.topo_explorer(occface,"wire")
    hole_list = []
    face_list = []
    #clockwise = hole
    #anticlockwise = face
    
    face_nrml = py3dmodel.calculate.face_normal(occface)
    
    for wire in wire_list:
        #first check if there are holes and which wire are holes
        pyptlist = py3dmodel.fetch.points_frm_wire(wire)
        is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, face_nrml)
        #create face from the wires
        wire_face = py3dmodel.construct.make_face_frm_wire(wire)
        
        if not is_anticlockwise:
            hole_list.append(wire_face)
        else:
            face_list.append(wire_face)
    
    return face_list, hole_list  

def boolean_x_w_ylist(xface, y_occtopos, mv_down = -10, extrude = 20, common = True):
    #move the grid and extrude it capture the boolean faces
    mv_grid = py3dmodel.modify.move([0,0,0], [0,0,mv_down], xface)
    mv_grid = py3dmodel.fetch.topo2topotype(mv_grid)
    gextrude = py3dmodel.construct.extrude(mv_grid, [0,0,1], extrude)
    
    if common ==True:
        common_list = []
        for i in y_occtopos:
            #py3dmodel.utility.visualise([[gextrude], [i]], ["WHITE", "RED"])
            common = py3dmodel.construct.boolean_common(gextrude, i)
            if not py3dmodel.fetch.is_compound_null(common):
                common_faces = py3dmodel.fetch.topo_explorer(common, "face")
                common_list.extend(common_faces)
        return common_list
    
    else:
        diff_list = []
        for i in y_occtopos:
            #py3dmodel.utility.visualise([[gextrude], [i]], ["WHITE", "RED"])
            diff = py3dmodel.construct.boolean_difference(i, gextrude)
            if not py3dmodel.fetch.is_compound_null(diff):
                diff_faces = py3dmodel.fetch.topo_explorer(diff, "face")
                diff_list.extend(diff_faces)
        return diff_list

def project_road2terrain(road_faces, road_holes, terrain_shell, tzmin, tzmax):
    face_list = []
    for r in road_faces:
        #extrude_r = py3dmodel.construct.extrude(r, [0,0,1], 30)
        #py3dmodel.utility.visualise([[extrude_r],[terrain_shell]])
        faces = boolean_x_w_ylist(r, [terrain_shell], mv_down = tzmin-10, extrude = tzmax+10)
        face_list.extend(faces)
    
    face_cmpd = py3dmodel.construct.make_compound(face_list)
    #py3dmodel.utility.visualise([[face_cmpd],[terrain_shell]])
    
    for h in road_holes:
        hole_faces = boolean_x_w_ylist(h, [face_cmpd], mv_down = tzmin-10, extrude = tzmax+10, common = False)
        face_cmpd = py3dmodel.construct.make_compound(hole_faces)
    
    #py3dmodel.utility.visualise([[face_cmpd]], ["RED"])
    return face_cmpd 

def redraw_faces(face_list):
    nf_list = []
    for f in face_list:
        vlist = py3dmodel.fetch.topo_explorer(f, "vertex")
        optlist = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
        pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(optlist)
        pyptlist = py3dmodel.modify.rmv_duplicated_pts(pyptlist)
        poly = py3dmodel.construct.make_polygon(pyptlist)
        poly_cmpd = py3dmodel.fetch.topo2topotype(py3dmodel.modify.fix_shape(poly))
        polys = py3dmodel.fetch.topo_explorer(poly_cmpd, "face")
        nf_list.extend(polys)
    return nf_list
   
#===========================================================================================
#READ THE SHAPEFILE
#===========================================================================================
time1 = time.clock()

print "*******Reading Grid File***************"
grid_shpatt_list = read_sf_poly(grid_shpfile)

print "*******Getting All the Terrains***************"
terrain_list = get_all_terrain(terrain_dir)

print "*******Reading Surface File***************"
srf_list = read_sf_poly(srf_shp_file)
rshp_list = []
for r in srf_list:
    rshp = r.shape
#    rid = r.get_value("unique_id")
#    if rid == 26123:    
#        py3dmodel.utility.visualise([[rshp]])
    rshp_list.append(rshp)
    
print len(rshp_list)

uid_list = []
display_list = []
print "*******Preparing to Generate Surfaces***************"
for g in grid_shpatt_list:
    grid = g.shape
    uid = g.get_value("id")
    uid_list.append(uid)
    print uid_list
    uid_list2 = [27, 26, 25, 24, 31, 30, 29, 28, 3, 2, 7, 6, 5, 4, 11, 10, 9]
    if uid in uid_list2:
        pass
    else:
        print "*******Reading and Generating Terrains***************"
        id_ts = identify_terrain(grid, terrain_list)
        terrain_shell = generate_tin(id_ts)
        txmin,tymin,tzmin, txmax,tymax,tzmax = py3dmodel.calculate.get_bounding_box(terrain_shell)
        terrain_faces = boolean_x_w_ylist(grid, [terrain_shell], mv_down = tzmin-10, extrude = tzmax+10)
        terrain_shell = py3dmodel.construct.sew_faces(terrain_faces)[0]
        print "*******Reading and Generating Surfaces***************"
        id_rs = identify_roads(grid, rshp_list)
        r_list = []
        nr = len(id_rs)
        rcnt = 0
        for r in id_rs:
            print "*******Generating Folder", uid, "Surface", rcnt+1, "/", nr, "***************"
            #if uid == 10 and rcnt+1 != 65:
            faces, holes = separate_face_holes(r)
            faces = redraw_faces(faces)
            holes = redraw_faces(holes)
            
            #print len(faces), len(holes)
            #py3dmodel.utility.visualise([faces, holes], ["RED", "GREEN"])
            if faces:
                road_face_cmpd = project_road2terrain(faces, holes, terrain_shell, tzmin, tzmax)
                r_list.append(road_face_cmpd)
                #py3dmodel.utility.visualise([[road_face_cmpd], [terrain_shell]], ["RED", "GREEN"])
                
            rcnt+=1
        
        if r_list:
            print "*******Writing to File" + str(uid), "***************"
            #create folder for each grid and name it after the unique id
            grid_folderpath = os.path.join(result_directory, str(uid))
            if not os.path.isdir(grid_folderpath):
                os.mkdir(grid_folderpath)
                
            road_filepath = os.path.join(grid_folderpath, filename)
            r_cmpd = py3dmodel.construct.make_compound(r_list)
            display_list.append(r_cmpd)
            py3dmodel.utility.write_brep(r_cmpd, road_filepath)
            
        time2 = time.clock()
        total_time = time2-time1
        print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"

py3dmodel.utility.visualise([display_list], ["WHITE"])     
