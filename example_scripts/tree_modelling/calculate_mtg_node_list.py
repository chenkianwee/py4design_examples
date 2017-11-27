import os 
import math
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
mtg_file = os.path.join(parent_path, "example_files","mtg", "tree1.txt" )
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\tree8.txt"
'''mtg_file = "C://file2analyse.gml"'''
d_height = 1
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
        circle = py3dmodel.fetch.topo2topotype(py3dmodel.modify.scale(poly_c, radius, start_pt))
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
        for ell2 in edge_lines_list:
            if start_pt_name == ell2[0]:
                srow = ell2
                break
        
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
height = zmax-zmin

ext_edge = py3dmodel.fetch.topo_explorer(cmpd, "edge")

print "TREE VOLUME(m3):", tree_vol
print "TREE MASS (kg):", tree_vol*690
print "TREE HEIGHT (m):", height
print "CALCULATED SQRT DIAMETER @ 1.5M (m):", calc_dia

display_2dlist.append(common_list)
colour_list.append("RED")
#display_2dlist.append([rec_m])
#colour_list.append("RED")
display_2dlist.append(ext_edge)
colour_list.append("BLACK")
py3dmodel.utility.visualise(display_2dlist, colour_list)