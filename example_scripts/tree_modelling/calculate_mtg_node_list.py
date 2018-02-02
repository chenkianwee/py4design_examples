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
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\tree8.txt"
#pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree29\\tree29.pts"
#dae_pts = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\tree9_trunk.dae"
#ext_dae = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\tree9_volume.dae"
'''mtg_file = "C://file2analyse.txt"'''
d_height = 1
time1 = time.time()
#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
def make_polygon_circle(centre_pypt, pydir, radius, division = 10):
    if radius <1:
        ref_c = py3dmodel.construct.make_circle(centre_pypt, pydir, 1)
        lb, ub = py3dmodel.fetch.edge_domain(ref_c)
        domain = ub - lb
        interval = domain/float(division)
        pt_list = []
        for i in range(division):
            parm = i*interval
            pt = py3dmodel.calculate.edgeparameter2pt(parm, ref_c)
            pt_list.append(pt)
            
        poly_c = py3dmodel.construct.make_polygon(pt_list)
        circle = py3dmodel.fetch.topo2topotype(py3dmodel.modify.scale(poly_c, radius, centre_pypt))
        return circle
    else:
        circle = py3dmodel.construct.make_circle(centre_pypt, pydir, radius)
        lb, ub = py3dmodel.fetch.edge_domain(circle)
        domain = ub - lb
        interval = domain/float(division)
        pt_list = []
        for i in range(division):
            parm = i*interval
            pt = py3dmodel.calculate.edgeparameter2pt(parm, circle)
            pt_list.append(pt)
            
        poly_c = py3dmodel.construct.make_polygon(pt_list)
        return poly_c
    
def make_edge_from_point(pypt, height):
    #extrude the point upwards to create an edge
    m_pypt = py3dmodel.modify.move_pt(pypt, (0,0,1), height)
    edge  = py3dmodel.construct.make_edge(pypt,m_pypt)
    return edge
    
def find_mtg_pt_row(edge_lines_list, pt_name):
    for ell in edge_lines_list:
        if pt_name == ell[0]:
            srow = ell
            break
    return srow

def find_mtg_parent_pt_row(edge_lines_list, parent_pt_name):
    row = []
    for ell in edge_lines_list:
        if parent_pt_name == ell[1]:
            row.append(ell)
    return row
# =============================================================================
# #read the original point file
# pf = open(pts_file, "r")
# lines = pf.readlines()
# pt_edge_list = []
# vertex_list = []
# for l in lines:
#     l = l.replace("\n","")
#     l_list = l.split(",")
#     
#     x = float(l_list[0])
#     y = float(l_list[1])
#     z = float(l_list[2])
#    
#     pypt = (x,y,z)
#     pt_edge_list.append(make_edge_from_point(pypt, 0.001))
#     occ_vertex = py3dmodel.construct.make_vertex(pypt)
#     vertex_list.append(occ_vertex)          
# 
# pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
# cpt = py3dmodel.calculate.get_centre_bbox(pt_cmpd)
# =============================================================================
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
edge_list = []
vol_list = []
common_list = []
diameter_list = []

for ell in  edge_lines_list:
    #check if it is an edge
    if ell[1] !="":
        radius = float(ell[6])
        start_pt_name = ell[1]
        end_pt_name = ell[0]
        srow = find_mtg_pt_row(edge_lines_list, start_pt_name)
        erow = find_mtg_parent_pt_row(edge_lines_list, end_pt_name)
        #print "current", ell
        #print "startpt", start_pt_name, srow
        #print "end_pt", end_pt_name, erow
#        for ell2 in edge_lines_list:
#            if start_pt_name == ell2[0]:
#                srow = ell2
#                break
        
        start_pt = (float(srow[3]), float(srow[4]), float(srow[5]))
        end_pt = (float(ell[3]), float(ell[4]), float(ell[5]))
        if start_pt != end_pt:
            edge = py3dmodel.construct.make_edge(start_pt, end_pt)
            edge_list.append(edge)
            vector = py3dmodel.construct.make_vector(start_pt, end_pt)
            n_vec = py3dmodel.modify.normalise_vec(vector)
    
            if radius > 1e-06:
                bottom_pipe = make_polygon_circle(start_pt, n_vec, radius)
                dist = py3dmodel.calculate.distance_between_2_pts(start_pt, end_pt)
                extrude = py3dmodel.construct.extrude(bottom_pipe, n_vec, dist)
                #if diameter == -1:
                common = py3dmodel.construct.boolean_common(extrude, rec_m)
                if not py3dmodel.fetch.is_compound_null(common):
                    diameter = radius*2
                    diameter_list.append(diameter)
                    
                    common_list.append(extrude)
                
        vol = math.pi*radius*radius*dist
        vol_list.append(vol)
        ext_list.append(extrude)

if len(diameter_list)>1:
    print "The plane cuts more than one pipe at 1.5m, please verify with the 3d windows, which diameter to take"
    dia_sq_list = []
    for d in diameter_list:
        print "DIAMETER @ 1.5M (m):", d
        dia_sq_list.append(d*d)
    
    dia_sq_sum = sum(dia_sq_list)
    calc_dia = math.sqrt(dia_sq_sum)
else:
    calc_dia = diameter_list[0]
    

tree_vol = sum(vol_list)
cmpd = py3dmodel.construct.make_compound(ext_list)
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(cmpd)
cpt2 = py3dmodel.calculate.get_centre_bbox(cmpd)
height = zmax-zmin
#cmpd = py3dmodel.modify.move(cpt2, cpt, cmpd)
ext_edge = py3dmodel.fetch.topo_explorer(cmpd, "edge")

print "TREE VOLUME(m3):", tree_vol
print "TREE MASS (kg):", tree_vol*690
print "TREE HEIGHT (m):", height
print "CALCULATED SQRT DIAMETER @ 1.5M (m):", calc_dia

display_2dlist.append(common_list)
colour_list.append("RED")

#display_2dlist.append(vertex_list)
#colour_list.append("GREEN")

#display_2dlist.append([rec_m])
#colour_list.append("RED")
display_2dlist.append(ext_edge)
colour_list.append("BLACK")

#py3dmodel.export_collada.write_2_collada(ext_list[0:1], dae_pts, occedge_list = pt_edge_list )
#py3dmodel.export_collada.write_2_collada(ext_list, ext_dae )
time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
py3dmodel.utility.visualise(display_2dlist, colour_list)