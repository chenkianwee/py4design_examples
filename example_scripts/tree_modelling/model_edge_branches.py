from py4design import py3dmodel

import os 
import time

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
#mtg_file = os.path.join(parent_path, "example_files","mtg", "tree9.txt" )

tree_name = "tree8"
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\" + tree_name + ".txt"
result_dir = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\edge"
'''mtg_file = "C://file2analyse.txt"'''

max_branch_order = 10
time1 = time.time()
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

def construct_edge_frm_mtg_row(mtg_row, edge_lines_list, max_branch_order):
    start_pt, end_pt, radius, srow = get_start_end_pt(mtg_row, edge_lines_list)
    
    branching_order = trace_2_root(mtg_row, edge_lines_list)
    if branching_order <max_branch_order: 
        edge = py3dmodel.construct.make_edge(start_pt, end_pt)
        return edge
    else:
        return None
               
#========================================================================================
#FUNCTIONS 
#========================================================================================
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
    
print "#========================="
print "READING THE MTG FILE ..." 
print "#========================="
display_2dlist = []
colour_list = []
mf = open(mtg_file, "r")
lines = mf.readlines()
branch_lines = lines[3:]
bl_2dlist = []
for bl in branch_lines:
    bl = bl.replace("\n","")
    bl_list = bl.split("\t")
    bl_2dlist.append(bl_list)
    
print "#=========================================="
print "CONSTRUCTING THE BRANCHING EDGE ..." 
print "#=========================================="
#a list of dictionaries that documents the tree architecture
edge_list = []

for bll in bl_2dlist:
    #check if it is an edge
    if bll[1] !="":
        branch_edge = construct_edge_frm_mtg_row(bll, bl_2dlist, max_branch_order)
        if branch_edge !=None:
            edge_list.append(branch_edge)
        
#========================================================================================================
#write and visualise
#========================================================================================================
dae_filepath = os.path.join(result_dir, "edge.dae")
py3dmodel.export_collada.write_2_collada(dae_filepath, occedge_list = edge_list)
display_2dlist.append(edge_list)
colour_list.append("BLUE")

time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
py3dmodel.utility.visualise(display_2dlist, colour_list)