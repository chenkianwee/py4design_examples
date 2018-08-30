import os 
import math
import time
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
#current_path = os.path.dirname(__file__)
#parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
#mtg_file = os.path.join(parent_path, "example_files","mtg", "tree9.txt" )

tree_name = "tree66.txt"
parent_path = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg_new"
mtg_file = os.path.join(parent_path, tree_name )

'''mtg_file = "C://file2analyse.txt"'''
d_height = 1
wood_density = 690 #kg/m3

print "CALCULATING VOL & MASS OF ...", tree_name
#================================================================================
#================================================================================ 
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
    
def calc_a_volume(start_pt, end_pt, radius):
    dist = py3dmodel.calculate.distance_between_2_pts(start_pt, end_pt)
    extrude = extrude_branch_vol(start_pt, end_pt, radius)
    vol = math.pi*radius*radius*dist
    return extrude, vol


def extrude_branch_vol(start_pt, end_pt, radius):
    if start_pt != end_pt:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec1, radius, division = circle_division)

        extrude = py3dmodel.construct.make_loft([bottom_pipe,top_pipe])
        loft_face_list = py3dmodel.fetch.topo_explorer(extrude, "face")
        loft_face_list.append(bottom_pipe)
        loft_face_list.append(top_pipe)
        extrude = py3dmodel.construct.sew_faces(loft_face_list)[0]
        extrude = py3dmodel.construct.make_solid(extrude)
        extrude = py3dmodel.modify.fix_close_solid(extrude)
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
    
#draw the pipe model
#get the diameter of the tree
rec = py3dmodel.construct.make_rectangle(100,100)
rec_m = py3dmodel.modify.move((0,0,0), (0,0,minz+ d_height), rec)
rec_m = py3dmodel.fetch.topo2topotype(rec_m)

ext_list = []
edge_list = []
vol_list = []
common_list = []
diameter_list = []

#a list of dictionaries that documents the tree architecture
branch_dict_list = []

for ell in edge_lines_list:
    #check if it is an edge
    if ell[1] !="":
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
        print "DIAMETER", d
        dia_sq_list.append(d*d)
    dia_sq_sum = sum(dia_sq_list)
    calc_dia = math.sqrt(dia_sq_sum)
else:
    calc_dia = diameter_list[0]
    
tree_vol = sum(vol_list)
print "TREE VOLUME(m3):", tree_vol
print "TREE MASS (kg):", tree_vol*wood_density
print "CALCULATED SQRT DIAMETER @ 1.5M (m):", calc_dia


display_2dlist.append(ext_list)
colour_list.append("WHITE")

time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
#py3dmodel.utility.visualise(display_2dlist, colour_list)