import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
grid_shpfile = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_grid\\main_campus_grid.shp"
#specify the directory to store the results which includes
shp_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_imps\\main_campus_imps.shp"
#specify if you want to view the result interactively
viewer = True
#===========================================================================================
#CONSTANTS
#===========================================================================================
roads_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\others_2015_princeton\\others_2015_princeton.shp"
#===========================================================================================
#FUNCTION
#===========================================================================================
def read_sf_poly(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
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
        
def find_bldgs_in_grid(grid, centrept_list, bldg_dict):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(grid)
    bldg_ftprint_list = []
    uid_list = []
    for c in centrept_list:
        pypt = c.shape
        x = pypt[0]
        y = pypt[1]
        if xmin <= x <= xmax and ymin <= y <= ymax:
            uid = c.get_value("unique_id")
            uid_list.append(uid)
            bldg_footprint = bldg_dict[uid]
            bldg_ftprint_list.append(bldg_footprint)
    return bldg_ftprint_list, uid_list

def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list

def common_road_frm_grid(grid, road_srf_list):
    road_faces = []
    road_holes = []
    cnt = 0
    for r in road_srf_list:
        #r = py3dmodel.modify.fix_face(r)
        faces, holes = separate_face_holes(r)
        #py3dmodel.utility.visualise([faces, holes], ["BLUE", "RED"])
        common_faces = boolean_x_w_ylist(grid, faces, mv_down = -10, extrude = 20, common = True)
        common_holes = boolean_x_w_ylist(grid, holes, mv_down = -10, extrude = 20, common = True)
        #py3dmodel.utility.visualise([[grid], faces], ["WHITE", "RED"])
        road_faces.extend(common_faces)
        road_holes.extend(common_holes)
        cnt+=1

    if len(road_faces) == 1:
        face_list = diff_srfs_frm_grid(road_faces[0], road_holes, mv_down = -10, extrude = 20)
    else:
        print "MORE THAN 1 FACE", len(road_faces)
        face_list = []
        for f in road_faces:
            faces = diff_srfs_frm_grid(f, road_holes, mv_down = -10, extrude = 20)
            face_list.extend(faces)
    
    #py3dmodel.utility.visualise([[grid], face_list], ["WHITE", "RED"])
    return face_list 

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
    
def diff_srfs_frm_grid(grid, srf_list, mv_down = -10, extrude = 20):
    #move the grid and extrude it capture the boolean faces
    for srf in srf_list:
        mv_grid = py3dmodel.modify.move([0,0,0], [0,0,mv_down], srf)
        mv_grid = py3dmodel.fetch.topo2topotype(mv_grid)
        gextrude = py3dmodel.construct.extrude(mv_grid, [0,0,1], extrude)
        #py3dmodel.utility.visualise([[grid], gextrude])
        grid = py3dmodel.construct.boolean_difference(grid, gextrude)
        grid_faces = py3dmodel.fetch.topo_explorer(grid, "face")
        grid_faces = redraw_faces(grid_faces)
        grid = py3dmodel.construct.make_compound(grid_faces)
        #py3dmodel.utility.visualise([[grid]])
        
    diff_faces = py3dmodel.fetch.topo_explorer(grid, "face")
    return diff_faces

def redraw_faces(occface_list):
    new_faces = []
    for f in occface_list:
        f = py3dmodel.modify.fix_face(f)
        wires = py3dmodel.fetch.topo_explorer(f, "wire")
        nwire = len(wires)
        if nwire > 1:
            faces = []
            holes = []
            nrml = py3dmodel.calculate.face_normal(f)
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anti = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml) 
                if is_anti: #means it is a face
                    faces.append(pyptlist)
                else:
                    holes.append(pyptlist)
                    
            face = py3dmodel.construct.make_polygon_w_holes(faces[0], holes)
                
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(f)
            face = py3dmodel.construct.make_polygon(pyptlist)
            
        new_faces.append(face)
    return new_faces

def separate_face_holes(occface):
    wire_list =  py3dmodel.fetch.topo_explorer(occface,"wire")
    nwires = len(wire_list)
    hole_list = []
    face_list = []
    #clockwise = hole
    #anticlockwise = face
    if nwires > 1:
        face_nrml = py3dmodel.calculate.face_normal(occface)
        for wire in wire_list:
            #first check if there are holes and which wire are holes
            pyptlist = py3dmodel.fetch.points_frm_wire(wire)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, face_nrml)
            #create face from the wires
            wire_face = py3dmodel.construct.make_polygon(pyptlist)
            #py3dmodel.utility.visualise([[wire_face]])
            if not is_anticlockwise:
                hole_list.append(wire_face)
            else:
                face_list.append(wire_face)
        
        return face_list, hole_list 
    else:
        face_list.append(occface)
        return face_list, hole_list 
    
def identify_srfs(grid, srf_list, use_bbox = True):
    identified = []
    for srf in srf_list:
        if use_bbox == True:
            pyptlist = py3dmodel.fetch.points_frm_occface(srf)
            r_face = py3dmodel.construct.convex_hull2d(pyptlist)
            #xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(srf)
            #r_face = make_bdry_face2d([xmin, ymin, zmin, xmax, ymax, zmax])
        else:
            r_face = srf
        
        common = py3dmodel.construct.boolean_common(r_face, grid)
        if not py3dmodel.fetch.is_compound_null(common):
            identified.append(srf)
    return identified

def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('index','N',10)
    cnt=0
    for occface in occface_list:
        wires = py3dmodel.fetch.topo_explorer(occface, "wire")
        nwires = len(wires)
        
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(occface)
            poly_shp_list = []
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if is_anticlockwise2:
                        pyptlist.reverse()
                else: #means its a hole not a face
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                
                pyptlist2d = []
                for pypt in pyptlist:
                    x = pypt[0]
                    y = pypt[1]
                    pypt2d = [x,y]
                    pyptlist2d.append(pypt2d)
                poly_shp_list.append(pyptlist2d)
                
            w.poly(poly_shp_list)
            w.record(cnt)
                    
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(occface)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
            if is_anticlockwise:
                pyptlist.reverse()
            pyptlist2d = []
            for pypt in pyptlist:
                x = pypt[0]
                y = pypt[1]
                pypt2d = [x,y]
                pyptlist2d.append(pypt2d)
        
            w.poly([pyptlist2d])
            w.record(cnt)
        cnt+=1
    w.close()
#===========================================================================================
#READ THE  SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading Grid File***************"
grid_shpatt_list = read_sf_poly(grid_shpfile)
print "*******Reading Road File***************"
road_list = read_sf_poly(roads_shp_file)
rshp_list = extract_shape_from_shapatt(road_list)
print len(rshp_list)

ngrids = len(grid_shpatt_list)
road_list2 = []
uid_list2 = []
gcnt=0
for g in grid_shpatt_list:
    print "*******Processing Folder", gcnt+1, "of", ngrids, "***************"
    grid = g.shape
    uid = g.get_value("id")
    
    uid_list2.append(uid)
    print "********Folders Processed*************"
    print uid_list2
    
    uid_list = []
    
    if uid in uid_list:
        pass
    
    else:
        id_roads = identify_srfs(grid, rshp_list)
        print len(id_roads)
        #get the roads in the grid
        roads = common_road_frm_grid(grid, id_roads)
        road_list2.extend(roads)
        #py3dmodel.utility.visualise([roads])
        
    time2 = time.clock()
    total_time = time2-time1
    print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
write_poly_shpfile(road_list2, shp_filepath)
if viewer == True:
    py3dmodel.utility.visualise([road_list2])