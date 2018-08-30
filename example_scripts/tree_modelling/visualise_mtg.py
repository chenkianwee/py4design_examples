import os 
import time

from py4design import py3dmodel
#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
#mtg_file = os.path.join(parent_path, "example_files","mtg", "tree9.txt" )

tree_name = "tree1"
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\mtg\\" + tree_name + ".txt"
trunk_pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\" + tree_name+"_trunk.pts"
result_dir = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\visualise_mtg"
'''mtg_file = "C://file2analyse.txt"'''
print "PROCESSING ...", tree_name

max_branch_order = 10
radius_thres = 0.00001

#================================================================================
#HARD CODED PARAMETERS
#================================================================================ 
circle_division = 10
#================================================================================
#FUNCTIONS 
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

def get_start_end_pt(mtg_row, edge_lines_list):
    start_pt_name = mtg_row[1]
    end_pt = (float(mtg_row[3]), float(mtg_row[4]), float(mtg_row[5]))
    radius = float(mtg_row[6])

    #find the start point row
    srow = find_mtg_pt_row(edge_lines_list, start_pt_name)
    start_pt = (float(srow[3]), float(srow[4]), float(srow[5]))
    return start_pt, end_pt, radius, srow

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
    
def extrude_branch(start_pt, end_pt, radius, cap = False):
    if start_pt != end_pt:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        #return bottom_pipe

        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec1, radius, division = circle_division)
        extrude = py3dmodel.construct.make_loft([bottom_pipe,top_pipe])
        loft_face_list = py3dmodel.fetch.topo_explorer(extrude, "face")
        loft_face_list.append(top_pipe)
        if cap == True:
            loft_face_list.append(bottom_pipe)
            extrude = py3dmodel.construct.sew_faces(loft_face_list)
            if len(extrude) >1:
                print "something went wrong at the construction of branches"
            solid = py3dmodel.construct.make_solid(extrude[0])
            solid = py3dmodel.modify.fix_close_solid(solid)
            return solid
        else:
            extrude = py3dmodel.construct.sew_faces(loft_face_list)
            if len(extrude) >1:
                print "something went wrong at the construction of branches"
            return extrude[0]

    else:
        return None
    
def trace_2_root(mtg_row, edge_lines_list):
    lineage_list = []
    branching_order = 0
    curr_row = mtg_row
    start_pt_name = curr_row[1]
    while start_pt_name != "":
        parent_row = find_mtg_pt_row(edge_lines_list, start_pt_name)
        sibling_rows = find_mtg_row_of_parent_pt(edge_lines_list, parent_row[0])
        chosen_row = choose_next_branch(sibling_rows)
        if chosen_row != curr_row: branching_order +=1
        lineage_list.append(parent_row)
        curr_row = parent_row
        start_pt_name = curr_row[1]
        
    return branching_order
    
def construct_cylinder_frm_mtg_row(mtg_row, edge_lines_list, max_branch_order):
    branch_dict = {}
    branching_order = trace_2_root(mtg_row, edge_lines_list)
    if branching_order <= max_branch_order:
        end_pt_name = mtg_row[0]
        start_pt_name = mtg_row[1]
        start_pt, end_pt, radius, srow = get_start_end_pt(mtg_row, edge_lines_list)
        ext_b = extrude_branch(start_pt, end_pt, radius, cap=True)
        
        #find the parent branch     
        branch_dict["end_pt_name"] = end_pt_name
        branch_dict["parent"] = start_pt_name
        branch_dict["geometry"] = ext_b
        branch_dict["start_pt"] = start_pt
        branch_dict["end_pt"] = end_pt
        branch_dict["radius"] = radius
        branch_dict["order"] = branching_order
        
        return branch_dict

def rmv_degenerate_faces(occcmpd):
    occface_list = py3dmodel.fetch.topo_explorer(occcmpd, "face")
    new_face_list = []
    for face in occface_list:
        pts = py3dmodel.fetch.points_frm_occface(face)
        npts = len(pts)
        face_area = py3dmodel.calculate.face_area(face)
        if npts >= 3 or face_area > 1e-012:
            new_face_list.append(face)
            
    return new_face_list

def read_pts_file(pts_file, delimiter = ","):
    pf = open(pts_file, "r")
    lines = pf.readlines()
    vertex_list = []
    pyptlist = []
    x_list = []
    y_list = []
    z_list = []
    for l in lines:
        l = l.replace("\n","")
        l_list = l.split(delimiter)
        x = float(l_list[0])
        x_list.append(x)
        y = float(l_list[1])
        y_list.append(y)
        z = float(l_list[2])
        z_list.append(z)
        pypt = (x,y,z)
        occ_vertex = py3dmodel.construct.make_vertex(pypt)
        vertex_list.append(occ_vertex)
        pyptlist.append(pypt)
    
    npts = len(x_list)
    x_mean = sum(x_list)/npts
    y_mean = sum(y_list)/npts
    z_mean = sum(z_list)/npts
    
    centre_pt = (x_mean, y_mean, z_mean)
    pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
    return pyptlist, pt_cmpd, centre_pt

#========================================================================================
#FUNCTIONS 
#========================================================================================
time1 = time.time()
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
    
print "#========================="
print "READING THE MTG FILE ..." 
print "#========================="
display_2dlist = []
colour_list = []
mf = open(mtg_file, "r")
lines = mf.readlines()
edge_lines = lines[3:]
edge_lines_list = []
for el in edge_lines:
    el = el.replace("\n","")
    el_list = el.split("\t")
    edge_lines_list.append(el_list)
    
print "#=========================================="
print "CONSTRUCTING THE BRANCHING DICTIONARY ..." 
print "#=========================================="
#a list of dictionaries that documents the tree architecture
branch_dict_list = []
edge_list = []
for ell in edge_lines_list:
    #check if it is an edge
    if ell[1] !="":
        branch_dict = construct_cylinder_frm_mtg_row(ell, edge_lines_list, max_branch_order)
        if branch_dict:
            branch_dict_list.append(branch_dict)

print "#==================================="
print "CONSTRUCTING THE BRANCH SOLIDS ..." 
print "#==================================="
    
geom_list = []
text_list = []
edge_list = []

for branch_dict in branch_dict_list:
    order = branch_dict["order"]
    radius = branch_dict["radius"]
    if order <= max_branch_order and radius >= radius_thres:
        end_pt_name = branch_dict["end_pt_name"]
        geom = branch_dict["geometry"]
        vlist = py3dmodel.fetch.topo_explorer(geom, "vertex")
        occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
        pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
        centre_pt = py3dmodel.calculate.points_mean(pyptlist)
        text_3d = py3dmodel.construct.make_brep_text(end_pt_name, 0.05)
        m_text_3d = py3dmodel.modify.move((0,0,0), centre_pt, text_3d)
        m_text_edges = py3dmodel.fetch.topo_explorer(m_text_3d, "edge")
        geom_list.append(geom)
        text_list.append(m_text_3d)
        edge_list.extend(m_text_edges)
        
print "#========================="
print "READING THE PTS FILE ..." 
print "#========================="
pyptlist2, pt_cmpd2, centre_pt2 = read_pts_file(trunk_pts_file, delimiter = ",")

print "#==================================="
print "WRITE TO FILE ..." 
print "#==================================="
geom_cmpd = py3dmodel.construct.make_compound(geom_list)
geom_cmpd = py3dmodel.modify.move((0,0,0), centre_pt2, geom_cmpd)

txt_cmpd = py3dmodel.construct.make_compound(text_list)
txt_cmpd = py3dmodel.modify.move((0,0,0), centre_pt2, txt_cmpd)

stl_file = os.path.join(result_dir, "visualise_tree.stl")
py3dmodel.utility.write_2_stl(geom_cmpd, stl_file)

dae_filepath = os.path.join(result_dir, "edge_with_rad.dae")
py3dmodel.export_collada.write_2_collada(dae_filepath, occface_list = geom_list)

stl_file2 = os.path.join(result_dir, "visualise_tree_txt.stl")
py3dmodel.utility.write_2_stl(txt_cmpd, stl_file2)
       
#========================================================================================================
#visualise
#========================================================================================================
display_2dlist.append(geom_list)
colour_list.append("BLUE")

display_2dlist.append(edge_list)
colour_list.append("BLACK")

time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
#py3dmodel.utility.visualise(display_2dlist, colour_list)