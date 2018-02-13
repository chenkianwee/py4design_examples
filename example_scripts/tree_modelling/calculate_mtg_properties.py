import os 
import math
import time
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
mtg_file = os.path.join(parent_path, "example_files","mtg", "tree9.txt" )
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\tree9.txt"
ext_dae = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\tree9_volume.dae"
'''mtg_file = "C://file2analyse.txt"'''
d_height = 1.5
wood_density = 690 #kg/m3
angle_threshold = 60
rad_extension_factor = 0.2
circle_division = 10
time1 = time.time()
#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================    
def find_mtg_pt_row(edge_lines_list, pt_name):
    for ell in edge_lines_list:
        if pt_name == ell[0]:
            srow = ell
            break
    return srow

def find_mtg_row_of_parent_pt(edge_lines_list, parent_pt_name):
    row = []
    for ell in edge_lines_list:
        if parent_pt_name == ell[1]:
            row.append(ell)
    return row

def choose_next_branch(erows):
    if erows:
        rads = []
    
        for erow in erows:
            rads.append(float(erow[6]))
            if erow[2] == "<":
                chosen_erow = erow
                return chosen_erow
            
        max_rad = max(rads)
        max_index = rads.index(max_rad)
        chosen_erow = erows[max_index]
        return chosen_erow
    else:
        return []
    
def extrude_branch(start_pt, end_pt, radius):
    if start_pt != end_pt:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec1, radius, division = circle_division)
        extrude = py3dmodel.construct.make_loft([bottom_pipe,top_pipe])
        loft_face_list = py3dmodel.fetch.topo_explorer(extrude, "face")
        loft_face_list.append(top_pipe)
        extrude = py3dmodel.construct.sew_faces(loft_face_list)
        return extrude[0]
    else:
        return None
    
def loft_with_consc_branches(start_pt, end_pt, end_pt2, radius, radius2, cap = False):
    if start_pt != end_pt and end_pt != end_pt2:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        vec2 = py3dmodel.construct.make_vector(end_pt, end_pt2)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        pyvec2 = py3dmodel.modify.normalise_vec(vec2)
    
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec2, radius2, division = circle_division)
        loft = py3dmodel.construct.make_loft([bottom_pipe,top_pipe], rule_face=False)
        face_list = py3dmodel.fetch.topo_explorer(loft, "face")
        loft = py3dmodel.construct.sew_faces(face_list)[0]
        loft = py3dmodel.modify.fix_shell_orientation(loft)
        if cap == True:
            face_list.append(bottom_pipe)
            face_list.append(top_pipe)
            loft = py3dmodel.construct.sew_faces(face_list)[0]
            
            loft = py3dmodel.construct.make_solid(loft)
            loft = py3dmodel.modify.fix_close_solid(loft)
        #py3dmodel.utility.visualise([[loft]])  
        return loft
    else:
        return None
    
def calc_a_volume(start_pt, end_pt, radius):
    dist = py3dmodel.calculate.distance_between_2_pts(start_pt, end_pt)
    extrude = extrude_branch_vol(start_pt, end_pt, radius)
    vol = math.pi*radius*radius*dist
    return extrude, vol


def extrude_branch_vol(start_pt, end_pt, radius):
    if start_pt != end_pt:
        vector = py3dmodel.construct.make_vector(start_pt, end_pt)
        n_vec = py3dmodel.modify.normalise_vec(vector)
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, n_vec, radius, division = circle_division)
        dist = py3dmodel.calculate.distance_between_2_pts(start_pt, end_pt)
        extrude = py3dmodel.construct.extrude(bottom_pipe, n_vec, dist)
        return extrude
    else:
        return None

def calc_diameter(ext_branch, dia_rec, radius):
    common = py3dmodel.construct.boolean_common(ext_branch, dia_rec)
    if not py3dmodel.fetch.is_compound_null(common):
        diameter = radius*2
        return diameter
    else:
        return None
    
def get_start_end_pt(mtg_row, edge_lines_list):
    start_pt_name = mtg_row[1]
    end_pt = (float(mtg_row[3]), float(mtg_row[4]), float(mtg_row[5]))
    radius = float(mtg_row[6])

    #find the start point row
    srow = find_mtg_pt_row(edge_lines_list, start_pt_name)
    start_pt = (float(srow[3]), float(srow[4]), float(srow[5]))
    return start_pt, end_pt, radius, srow
    
def construct_cylinder_frm_mtg_row(mtg_row, edge_lines_list):
    branch_dict = {}
    end_pt_name = mtg_row[0]
    start_pt_name = mtg_row[1]
    start_pt, end_pt, radius, srow = get_start_end_pt(mtg_row, edge_lines_list)

    #from the end point find the number of edges connected to this branch
    erows = find_mtg_row_of_parent_pt(edge_lines_list, end_pt_name)
    children_list = []
    for erow in erows:
        children_list.append(erow[0])
    #choose the next row 
    chosen_row = choose_next_branch(erows)
    #measure the angle of bending for the branches
    if chosen_row:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        radius2 = float(chosen_row[6])
        end_pt2 = (float(chosen_row[3]), float(chosen_row[4]), float(chosen_row[5]))
        vec2 = py3dmodel.construct.make_vector(end_pt, end_pt2)
        pyvec2 = py3dmodel.modify.normalise_vec(vec2)
        angle = py3dmodel.calculate.angle_bw_2_vecs(pyvec1, pyvec2)
        if angle < angle_threshold:
            ext_b = loft_with_consc_branches(start_pt, end_pt, end_pt2, radius, radius2, cap = False)
            ext_b1 = loft_with_consc_branches(start_pt, end_pt, end_pt2, radius, radius2, cap = True)
        else:
            new_end_pt = py3dmodel.modify.move_pt(end_pt, pyvec1, radius + (rad_extension_factor*radius))
            ext_b = extrude_branch(start_pt, new_end_pt, radius)
            ext_b1 = extrude_branch_vol(start_pt, new_end_pt, radius)
    else:
        angle = 180
        ext_b = extrude_branch(start_pt, end_pt, radius)
        ext_b1 = extrude_branch_vol(start_pt, end_pt, radius)
    
    #find all the branches that share the same starting point as this branch 
    sibling_list = []
    sibling_rows = find_mtg_row_of_parent_pt(edge_lines_list, start_pt_name)
    for sibling in sibling_rows:
        if sibling[0] != end_pt_name:
            sibling_list.append(sibling[0])
    
    #find the parent branch 
    #start_pt_name0 = srow[1]
    
    branch_dict["end_pt_name"] = end_pt_name
    branch_dict["children"] = children_list
    branch_dict["siblings"] = sibling_list
    branch_dict["parent"] = start_pt_name
    branch_dict["geometry"] = ext_b
    branch_dict["cut_geometry"] = ext_b1
    branch_dict["start_pt"] = start_pt
    branch_dict["end_pt"] = end_pt
    branch_dict["radius"] = radius
    branch_dict["is_split"] = mtg_row[2]
    branch_dict["angle"] = angle
    
    if chosen_row:
        branch_dict["connection"] = chosen_row[0]
    else:
        branch_dict["connection"] = None
    return branch_dict

def angle_btw_vecs(start_pt, end_pt, end_pt2):
    vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
    vec2 = py3dmodel.construct.make_vector(end_pt, end_pt2)
    pyvec1 = py3dmodel.modify.normalise_vec(vec1)
    pyvec2 = py3dmodel.modify.normalise_vec(vec2)
    angle = py3dmodel.calculate.angle_bw_2_vecs(pyvec1, pyvec2)
    return angle

def get_branch_dict(end_pt_name_list, dict_list):
    get_list = []
    for bdict in dict_list:
        end_pt_name = bdict["end_pt_name"]
        if end_pt_name in end_pt_name_list:
            get_list.append(bdict)
            if len(get_list) == len(end_pt_name_list):
                break
    return get_list

def get_cut_geom_from_dict(dict_list):
    get_geom_list = []
    for bdict in dict_list:
        geom = bdict["cut_geometry"]
        get_geom_list.append(geom)
    return get_geom_list

def multiple_bool_diff(geom2cutfrom, cut_geom_list):
    cuted_geom = geom2cutfrom
    for cgeom in cut_geom_list:
        cuted_geom1 = py3dmodel.construct.boolean_difference(cuted_geom, cgeom)
        if cuted_geom1 != cuted_geom:
            cuted_geom = cuted_geom1
        else:
           meshed_cuted_geom = py3dmodel.construct.simple_mesh(cuted_geom)
           meshed_cuted_geom = py3dmodel.construct.sew_faces(meshed_cuted_geom)
           cuted_geom = py3dmodel.construct.boolean_difference(meshed_cuted_geom, cgeom)
           
    return cuted_geom
#========================================================================================
display_2dlist = []
colour_list = []
mf = open(mtg_file, "r")
lines = mf.readlines()
edge_lines = lines[3:]
edge_lines_list = []
minz = float("inf")
for el in edge_lines:
    el = el.replace("\n","")
    el_list = el.split("\t")
    z = float(el_list[5])
    if z<minz:
        minz = z
    edge_lines_list.append(el_list)
    
#print edge_lines_list
#draw the pipe model
#get the diameter of the tree
rec = py3dmodel.construct.make_rectangle(100,100)
rec_m = py3dmodel.modify.move((0,0,0), (0,0,minz+ d_height), rec)
rec_m = py3dmodel.fetch.topo2topotype(rec_m)

ext_list = []
loft_list1 = []
loft_list2 = []
edge_list = []
vol_list = []
common_list = []
diameter_list = []

#a list of dictionaries that documents the tree architecture
branch_dict_list = []

for ell in edge_lines_list:
    #check if it is an edge
    if ell[1] !="":
        branch_dict = construct_cylinder_frm_mtg_row(ell, edge_lines_list)
        ext_b = branch_dict["geometry"] 
        if branch_dict["is_split"] == "<":
            loft_list1.append(ext_b)
        else:
            loft_list2.append(ext_b)
            
        branch_dict_list.append(branch_dict)
        #========================================================================================================
        #calculate the volume of the tree
        #========================================================================================================
        start_pt, end_pt, radius, srow = get_start_end_pt(ell, edge_lines_list)
        extrude, vol = calc_a_volume(start_pt, end_pt, radius)
        diameter = calc_diameter(extrude, rec_m, radius)
        if diameter !=None:
            diameter_list.append(diameter)
            common_list.append(extrude)
    
        vol_list.append(vol)
        ext_list.append(extrude)
        #========================================================================================================
        #========================================================================================================
        
if len(diameter_list)>1:
    print "The plane cuts more than one pipe at 1.5m"
    dia_sq_list = []
    for d in diameter_list:
        dia_sq_list.append(d*d)
    dia_sq_sum = sum(dia_sq_list)
    calc_dia = math.sqrt(dia_sq_sum)
else:
    calc_dia = diameter_list[0]
    
tree_vol = sum(vol_list)
print "TREE VOLUME(m3):", tree_vol
print "TREE MASS (kg):", tree_vol*wood_density
print "CALCULATED SQRT DIAMETER @ 1.5M (m):", calc_dia

bool_geom_list = []
branch_dict_list = branch_dict_list[0:10]

for branch_dict in branch_dict_list:
    end_pt_name = branch_dict["end_pt_name"]
    #print end_pt_name
    connection = branch_dict["connection"]
    bgeom = branch_dict["geometry"]
    parent = branch_dict["parent"]
    siblings = branch_dict["siblings"]
    children = branch_dict["children"]
    parent_dict = get_branch_dict([parent], branch_dict_list)
    sibling_dict_list = get_branch_dict(siblings, branch_dict_list)
    children_dict_list = get_branch_dict(children, branch_dict_list)
    #py3dmodel.utility.visualise([[bgeom]])
    if parent_dict:
        parent_dict = parent_dict[0]
        parent_angle = parent_dict["angle"]
        parent_connection = parent_dict["connection"]
        if parent_angle >= angle_threshold or parent_connection != end_pt_name:
            parent_geom = get_cut_geom_from_dict([parent_dict])
            bgeom = multiple_bool_diff(bgeom, parent_geom)
            #print "PARENT"
            #cmpd = py3dmodel.construct.make_compound(parent_geom)
            #edges = py3dmodel.fetch.topo_explorer(cmpd, "edge")
            #py3dmodel.utility.visualise([[bgeom], edges], ['WHITE', 'RED'])
    
    if sibling_dict_list:
        sibling_geom_list = get_cut_geom_from_dict(sibling_dict_list)
        bgeom = multiple_bool_diff(bgeom, sibling_geom_list)
        #print "SIBLINGS"
        #mpd = py3dmodel.construct.make_compound(sibling_geom_list)
        #edges = py3dmodel.fetch.topo_explorer(cmpd, "edge")
        #py3dmodel.utility.visualise([[bgeom], edges], ['WHITE', 'RED'])
        
    if len(children_dict_list) > 1:
        #remove the children that it is already connected to 
        for child in children_dict_list:
            if child["end_pt_name"] == connection:
                children_dict_list.remove(child)
                break
        
        children_geom_list = get_cut_geom_from_dict(children_dict_list)
        bgeom = multiple_bool_diff(bgeom, children_geom_list)
        #print "CHILDREN"
        #cmpd = py3dmodel.construct.make_compound(children_geom_list)
        #edges = py3dmodel.fetch.topo_explorer(cmpd, "edge")
        #py3dmodel.utility.visualise([[bgeom], edges], ['WHITE', 'RED'])
        
    #py3dmodel.utility.visualise([[bgeom]])
    bool_geom_list.append(bgeom)
    
cmpd = py3dmodel.construct.make_compound(bool_geom_list)
#xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(cmpd)
#cpt2 = py3dmodel.calculate.get_centre_bbox(cmpd)
#height = zmax-zmin
#ext_edge = py3dmodel.fetch.topo_explorer(cmpd, "edge")

##display_2dlist.append(common_list)
##colour_list.append("RED")
#
##display_2dlist.append(edge_list)
##colour_list.append("BLACK")
#
#display_2dlist.append(loft_list1)
#colour_list.append("BLACK")
#
#display_2dlist.append(loft_list2)
#colour_list.append("RED")

display_2dlist.append([cmpd])
colour_list.append("WHITE")
##py3dmodel.export_collada.write_2_collada(ext_list[0:1], dae_pts, occedge_list = pt_edge_list )
##py3dmodel.export_collada.write_2_collada(ext_dae, occedge_list = edge_list )
time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
py3dmodel.utility.visualise(display_2dlist, colour_list)