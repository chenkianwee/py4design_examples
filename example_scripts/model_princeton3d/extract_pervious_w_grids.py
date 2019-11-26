import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
grid_shpfile = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_grid\\main_campus_grid.shp"
#specify the directory to store the results which includes
shp_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_pervious\\main_campus_pervious.shp"
#specify if you want to view the result interactively
viewer = True
#===========================================================================================
#CONSTANTS
#===========================================================================================
pervious_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\pervious"
imp_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_imps\\main_campus_imps.shp"

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

def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list

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
                if not pyptlist:
                    verts = py3dmodel.fetch.topo_explorer(wire, "vertex")
                    occpts = py3dmodel.modify.occvertex_list_2_occpt_list(verts)
                    pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpts)
                    
                is_anti = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml) 
                
                if is_anti: #means it is a face
                    faces.append(pyptlist)
                else:
                    holes.append(pyptlist)
                
            face = py3dmodel.construct.make_polygon_w_holes(faces[0], holes)
                
        else:
            pyptlist = py3dmodel.fetch.points_frm_wire(wires[0])
            if pyptlist:
                face = py3dmodel.construct.make_polygon(pyptlist)
            else:
                verts = py3dmodel.fetch.topo_explorer(f, "vertex")
                occpts = py3dmodel.modify.occvertex_list_2_occpt_list(verts)
                pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpts)
                face = py3dmodel.construct.make_polygon(pyptlist)
                #py3dmodel.utility.visualise_falsecolour_topo(verts, range(len(verts)), other_occtopo_2dlist = [[face]], other_colour_list = ["WHITE"])
                
        new_faces.append(face)
    return new_faces

def is_all_points_in_grid(grid, pyptlist):
    in_grid = True
    for pypt in pyptlist:
        in_face = py3dmodel.calculate.point_in_face(pypt, grid)
        if not in_face:
            in_grid = False
            break
    return in_grid

def srf_not_in_grid(grid, srf_list):
    notin = []
    for srf in srf_list:
        pyptlist = py3dmodel.fetch.points_frm_occface(srf)
        in_grid = is_all_points_in_grid(grid, pyptlist)
        if not in_grid:
            notin.append(srf)
    return notin        

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
                common_faces = redraw_faces(common_faces)
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
        
#def identify_srfs2(grid, srf_list):
#    identified = []
#    non = []
#    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(grid)
#    for srf in srf_list:
#        midpt = py3dmodel.calculate.face_midpt(srf)        
#        x = midpt[0]
#        y = midpt[1]
#        z = midpt[2]
#        if xmin<=x<=xmax and ymin<=y<=ymax and zmin<=z<=zmax:
#            touching = False
#            pyptlist = py3dmodel.fetch.points_frm_occface(srf)
#            
#            for pypt in pyptlist:
#                in_face = py3dmodel.calculate.point_in_face(pypt, grid)
#                if in_face:
#                    touching = True
#                    break
#                
#            if touching == False:
#                non.append(srf)
#            else:
#                identified.append(srf)
#        else:
#            non.append(srf)
#            
#    return identified, non

def identify_srfs2(grid, srf_list, use_bbox = True):
    identified = []
    non = []
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
        else:
            non.append(srf)
    return identified, non

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

def diff_p_frm_imp(pshps, impshps, uid, uid_list):
    nbp = len(pshps)
    nb_imps = len(id_imps)
    print "NB_PSHPS", nbp, "ID_IMPS", nb_imps
    res_list = pshps
    cnt = 0
    for imp in impshps:
        print "Processing imp", cnt, "/", nb_imps, "Folder", uid, "UID lIST", uid_list
        id_ps, non_ps = identify_srfs2(imp, res_list)
        #print len(id_ps), "ID PERVIOUS"
        diff_list = diff_imps_frm_p(imp, id_ps, cnt, mv_down = -10, extrude = 20)
        res_list = non_ps + diff_list
        print "RES", len(res_list), "NON", len(non_ps), "ID", len(id_ps), "DIFF", len(diff_list)
        cnt+=1
    
    return res_list

def diff_imps_frm_p(imp, id_ps, cnt, mv_down = -10, extrude = 20):
    res_diff_faces = []
    #move the grid and extrude it capture the boolean faces
    faces, holes = separate_face_holes(imp)
    if holes:
        print len(holes), "HOLES"
        for hole in holes:
            id_ps2 = identify_srfs(hole, id_ps)
            common_list = boolean_x_w_ylist(hole, id_ps2, mv_down = -10, extrude = 20, common = True)
            res_diff_faces.extend(common_list)
        
    if len(faces) == 1:
        face = faces[0]
        face = fix_poly_sharing_pt(face)
        mv_grid = py3dmodel.modify.move([0,0,0], [0,0,mv_down], face)
        mv_grid = py3dmodel.fetch.topo2topotype(mv_grid)
        gextrude = py3dmodel.construct.extrude(mv_grid, [0,0,1], extrude)
        for p in id_ps:
            #py3dmodel.utility.visualise([[p2], [gextrude]], ["RED", "WHITE"])
            diff_p = py3dmodel.construct.boolean_difference(p, gextrude)
            p_faces = py3dmodel.fetch.topo_explorer(diff_p, "face")
            if p_faces:
                p_faces = redraw_faces(p_faces)
                res_diff_faces.extend(p_faces)
                
    else:
        print "MORE THAN 1 FACE"
        
    return res_diff_faces


#===========================================================================================
#READ THE  SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading Grid File***************"
grid_shpatt_list = read_sf_poly(grid_shpfile)
print "*******Reading Impervious File***************"
imp_shpatt_list = read_sf_poly(imp_shp_file)
ishp_list = extract_shape_from_shapatt(imp_shpatt_list)
print len(ishp_list)
print "*******Preparing to Find Pervious***************"
ngrids = len(grid_shpatt_list)
plist = []
uid_list2 = []
gcnt=0
for g in grid_shpatt_list:
    print "*******Processing Folder", gcnt+1, "of", ngrids, "***************"
    grid = g.shape
    uid = g.get_value("id")
    
    uid_list2.append(uid)
    print "********Folders Processed*************"
    print uid_list2
    
    uid_list = [162,163,164,143]
    
    if uid in uid_list:
        pass
    else:
        #get pervious folders
        folderpath = os.path.join(pervious_dir, str(uid))
        filepath = os.path.join(folderpath, "pervious10by10m.shp")
        perv_shpatt_list = read_sf_poly(filepath)
        pshps = extract_shape_from_shapatt(perv_shpatt_list)
        
        id_imps = identify_srfs(grid, ishp_list)
        diff_pshps = diff_p_frm_imp(pshps, id_imps, uid, uid_list2)
        plist.extend(diff_pshps)
        #py3dmodel.utility.visualise([plist])
        write_poly_shpfile(plist, shp_filepath)
        
    time2 = time.clock()
    total_time = time2-time1
    print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
write_poly_shpfile(plist, shp_filepath)
if viewer == True:
    py3dmodel.utility.visualise([plist])