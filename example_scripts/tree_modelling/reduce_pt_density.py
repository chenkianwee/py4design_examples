import os 
import math
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
pts_file = os.path.join(parent_path, "example_files","pts", "tree9.pts" )
#pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\tree8.txt"
interval_height = 0.5
reduction_dist = 0.2
#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
pf = open(pts_file, "r")
lines = pf.readlines()
#lines = lines[0:10000]
vertex_list = []
pyptlist = []
for l in lines:
    l = l.replace("\n","")
    l_list = l.split(",")
    x = float(l_list[0])
    y = float(l_list[1])
    z = float(l_list[2])
    pypt = (x,y,z)
    occ_vertex = py3dmodel.construct.make_vertex(pypt)
    vertex_list.append(occ_vertex)
    pyptlist.append(pypt)

pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
xmin,ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)
height = zmax - zmin
interval = int(math.ceil(height/interval_height))
print "HEIGHT:", height
print "ZMAX:", zmax
print "ZMIN:", zmin
print "INTERVAL:", interval

#create a list with all the intervals
pypts_interval_dict = {}
#separate the pts into level intervals
print "SEPARATING THE POINTS INTO LEVELS ..."
zmin_intheight = zmin + interval_height
imin = zmin
interval_height_list = []
for cnt in range(interval):
    imax = zmin_intheight + (interval_height*cnt)
    interval_height_list.append(imin)
    #print imin, imax
    for p in pyptlist:
        z = p[2]
        if imin <= z < imax:
            if imin in pypts_interval_dict:
                pypts_interval_dict[imin].append(p)
            else:
                pypts_interval_dict[imin] = [p]
    imin = imax

#triangulate the points into faces
print "TRIANGULATING ..."
face_list = []
vol_list = []
extrude_list = []
reduced_pts = []
tcnt = 0
for k in interval_height_list:
    k_ptlist = pypts_interval_dict[k]
    #reduce the pt list
    k_ptlist1 = py3dmodel.modify.rmv_duplicated_pts_by_distance(k_ptlist, distance = reduction_dist)
    if len(k_ptlist1) < 3:
         k_ptlist1 = py3dmodel.modify.rmv_duplicated_pts_by_distance(k_ptlist, distance = reduction_dist - 0.1)
         
    #print "kptlist The number of points are reduced from", len(k_ptlist), "to", len(k_ptlist1)
    #flatten the point
    fpt_list = []
    for pt in k_ptlist1:
        fpt = (pt[0], pt[1],k)
        fpt_list.append(fpt)
        v = py3dmodel.construct.make_vertex(pt)
        reduced_pts.append(v)
        
    occface_list = py3dmodel.construct.delaunay3d(fpt_list)
    occface = py3dmodel.construct.merge_faces(occface_list)
    print "TRIANGULATING ...", tcnt+1, "/", interval
    extrude = py3dmodel.construct.extrude(occface[0], (0,0,1), interval_height)
    vol = py3dmodel.calculate.solid_volume(extrude)
    vol_list.append(vol)
    extrude_list.append(extrude)
    face_list.extend(occface)
    tcnt+=1
    
#loft = py3dmodel.construct.make_loft(face_list)
print "TOTAL TREE VOL:", sum(vol_list)
display_2dlist = []
colour_list = []
display_2dlist.append(vertex_list)
colour_list.append("GREEN")
display_2dlist.append(reduced_pts)
colour_list.append("RED")
display_2dlist.append(extrude_list)
colour_list.append("WHITE")
py3dmodel.utility.visualise(display_2dlist, colour_list)