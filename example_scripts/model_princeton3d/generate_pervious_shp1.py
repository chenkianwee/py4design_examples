import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
#specify the grid files
grid_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_context_grid\\princeton_context_grid_10by10km.shp"

#specify the directory to store the results which includes
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\pervious"
filename = "pervious10by10m.shp"

grid_sizex = 5
grid_sizey = 5

#specify if you want to rmv the other impervious surfaces other than road and building
include_other_surfaces = False
#===========================================================================================
#THE REQUIRED SHP FILES
#===========================================================================================
#specify the impervious files
imp_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\others_2015_princeton\\others_2015_princeton.shp"
bldg_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\buildings_2015_princeton\\buildings_2015_princeton.shp"
bldg_centrept_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\buildings_centrept_2015_princeton\\buildings_centrept_2015_princeton.shp"
road_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\roads_2015_princeton\\roads_2015_princeton.shp"
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

def read_sf_pt(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pts = shp2citygml.get_geometry(rec)
        if pts:
            for pt in pts:
                pypt = (pt[0], pt[1], 0)
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(pypt)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)

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
    
def make_bdry_face2d(mn_mx_list):
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face

def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list
    
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

def diff_road_frm_grid(grid, road_srf_list):
    road_faces = []
    road_holes = []
    cnt = 0
    for r in road_srf_list:
        r = py3dmodel.modify.fix_face(r)
        faces, holes = separate_face_holes(r)
        road_faces.extend(faces)
        road_holes.extend(holes)
        cnt+=1
    face_list = diff_srfs_frm_grid(grid, road_faces)
    #py3dmodel.utility.visualise([road_holes, [grid]], ["RED", "BLUE"])
    face_list.extend(road_holes)
    
    return face_list 

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
        
def find_non_intersect_grid(grids, srf_list, uid, check_intersect = False):
    non_intersect = []
    ngrids = len(grids)
    gcnt = 0
    for grid in grids:
        print "*******Folder", uid, "Processing Grid", gcnt+1, "/", ngrids, "***************" 
        ided = identify_srfs(grid, srf_list, use_bbox = False)
        if ided:
            if check_intersect == False:
                diff_faces = diff_srfs_frm_grid(grid, ided)
            else:
                fix_list = []
                for srf in ided:
                    fixed = fix_poly_sharing_pt(srf)
                    fix_list.append(fixed)
                    
                diff_faces = diff_srfs_frm_grid(grid, fix_list)
#                if gcnt+1 == 36:
#                    #py3dmodel.utility.visualise([ided])
#                    pts = py3dmodel.fetch.points_frm_occface(fix_list[0])
#                    vlist = py3dmodel.construct.make_occvertex_list(pts)
#                    clist = []
#                    for c in range(len(vlist)):
#                        clist.append(c)
#
#                    py3dmodel.utility.visualise([fix_list, vlist], ["RED", "BLUE"])
            non_intersect.extend(diff_faces)
        else:
            non_intersect.append(grid)
        
        gcnt +=1
        
    return non_intersect

def find_duplicate_points(pyptlist):
    pyptlist2 = []
    ind_list = []
    cnt = 0
    for pypt in pyptlist:
        if pypt not in pyptlist2:
            pyptlist2.append(pypt)
        else:
            ind_list.append(cnt)
        cnt+=1
        
    return ind_list
        
def fix_poly_sharing_pt(occface):
    wires = py3dmodel.fetch.topo_explorer(occface, "wire")
    nwire = len(wires)
    if nwire >1:
        face_list = []
        hole_list = []
        face_nrml = py3dmodel.calculate.face_normal(occface)
        for wire in wires:
            #first check if there are holes and which wire are holes
            pyptlist = py3dmodel.fetch.points_frm_wire(wire)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, face_nrml)
            if not is_anticlockwise:
                hole_list.append(pyptlist)
            else:
                face_list.append(pyptlist)
                
        nf = len(face_list)
        if nf == 1:
            pyptlist2 = face_list[0]
            index_list = find_duplicate_points(pyptlist2)
            if index_list:
                pyptlist3 = pyptlist2[:]
                for index in index_list:
                    nxt = index+1
                    vec = py3dmodel.construct.make_vector(pyptlist3[index], pyptlist3[nxt])
                    pyvec = py3dmodel.modify.gpvec_2_pyvec(vec)
                    new_pt = py3dmodel.modify.move_pt(pyptlist3[index], pyvec, 0.05)                
                    pyptlist3.insert(index, new_pt)
                    del pyptlist3[nxt]
                
                fixed_face = py3dmodel.construct.make_polygon_w_holes(pyptlist3, hole_list)         
                return fixed_face
            else:
                return occface
        else:
            print "********** More than 1 face detected, Please double check geometry **********"
        
    else:
        pyptlist = py3dmodel.fetch.points_frm_occface(occface)
        index_list = find_duplicate_points(pyptlist)
        if index_list:
            index = index_list[0]
            nxt = index+1
            vec = py3dmodel.construct.make_vector(pyptlist[index], pyptlist[nxt])
            pyvec = py3dmodel.modify.gpvec_2_pyvec(vec)
            new_pt = py3dmodel.modify.move_pt(pyptlist[index], pyvec, 0.05)
            pyptlist.insert(index, new_pt)
            del pyptlist[index+1]
            fixed_face = py3dmodel.construct.make_polygon(pyptlist)
            return fixed_face
        else:
            return occface
        
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

def shpatt2dict_uniqueid(shpatt_list):
    d = {}
    for s in shpatt_list:
        shape = s.shape
        uid = s.get_value("unique_id")
        d[uid] = shape
    return d

def boolean_common_roads_grid(road, grid):
    road_faces, road_holes = separate_face_holes(road)

    road_faces = identify_srfs(grid, road_faces, use_bbox = True)
    road_holes = identify_srfs(grid, road_holes, use_bbox = True)

    face_list = boolean_x_w_ylist(grid, road_faces)
    face_cmpd = py3dmodel.construct.make_compound(face_list)
    #py3dmodel.utility.visualise([[face_cmpd],[terrain_shell]])
    
    for h in road_holes:
        hole_faces = boolean_x_w_ylist(h, [face_cmpd], common = False)
        face_cmpd = py3dmodel.construct.make_compound(hole_faces)

    #py3dmodel.utility.visualise([[face_cmpd]], ["RED"])
    return face_cmpd 

#===========================================================================================
#READ THE SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading the grid file***************"
grid_att_list = read_sf_poly(grid_shp_file)

if include_other_surfaces == True:
    print "*******Reading the imp file***************"
    imp_att_list = read_sf_poly(imp_shp_file)
    ishp_list = extract_shape_from_shapatt(imp_att_list)

print "*******Reading the road file***************"
road_att_list = read_sf_poly(road_shp_file)
rshp_list = extract_shape_from_shapatt(road_att_list)
print "*******Reading the bldg file***************"
bcentrept_list = read_sf_pt(bldg_centrept_shp_file)
bldg_att_list = read_sf_poly(bldg_shp_file)
bldg_dict = shpatt2dict_uniqueid(bldg_att_list)

#===========================================================================================
#DIFFERENCE THE IMPERVIOUS SURFACES
#===========================================================================================
print "*******Looping through the file***************"
uid_list2 = []
for gatt in grid_att_list:
    grid = gatt.shape
    uid = gatt.get_value("id")
    print "********Folders Processed*************"
    uid_list2.append(uid)
    print uid_list2
    uid_list = []
    if uid in uid_list:
        pass
    else:
        print "*******Identifying Buildings***************"
        gmidpt = py3dmodel.calculate.face_midpt(grid)
        big_grid = py3dmodel.modify.scale(grid, 1.5, gmidpt)
        big_grid = py3dmodel.fetch.topo_explorer(big_grid, "face")[0]
        bldg_footprints, buid_list = find_bldgs_in_grid(big_grid, bcentrept_list, bldg_dict)
        bldg_footprints = identify_srfs(grid, bldg_footprints)
        
        print "*******Identifying Roads***************"
        id_roads = identify_srfs(grid, rshp_list)

        r_list = []
        for r in id_roads:
            road_face_cmpd = boolean_common_roads_grid(r, grid)
            road_faces = py3dmodel.fetch.topo_explorer(road_face_cmpd, "face")
            r_list.extend(road_faces)
            
        print "*******Generating Folder", uid, "***************"
        print "*******Difference Road from Grid", uid, "***************"
        
        grids1 = diff_road_frm_grid(grid, r_list)
        #py3dmodel.utility.visualise([grids1, r_list], ["BLUE", "BLACK"])

        print "*******Difference Building from Grid", uid, "***************"
        #grid the grid
        grids2 = []
        for g1 in grids1:
            g2 = py3dmodel.construct.grid_face(g1, grid_sizex, grid_sizey)
            grids2.extend(g2)

        #py3dmodel.utility.visualise([grids2], ["RED"])
        #get the footprints, roads and surfaces in the grid
        non_intersect = find_non_intersect_grid(grids2, bldg_footprints, uid, check_intersect = True)
        
        if include_other_surfaces == True:
            id_srfs = identify_srfs(grid, ishp_list)
            non_intersect = find_non_intersect_grid(non_intersect, id_srfs, uid, check_intersect = True)
        
        #cpmd = py3dmodel.construct.make_compound(non_intersect)
        #cpmd = py3dmodel.modify.move([0,0,0], [0,0,10], cpmd)
        #py3dmodel.utility.visualise([[cpmd], bldg_footprints, id_roads], ["RED", "GREEN", "BLACK"])
        
    print "*******Writing Folder", uid, "***************"
    grid_folderpath = os.path.join(result_directory, str(uid))
    if not os.path.isdir(grid_folderpath):
        os.mkdir(grid_folderpath)
            
    res_filepath = os.path.join(grid_folderpath, filename)
    write_poly_shpfile(non_intersect, res_filepath)
    time2 = time.clock()
    total_time = time2-time1
    print "*******Total Time Take:", total_time/60, "mins***************"
