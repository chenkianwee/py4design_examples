import os 
import math
import time
import random
import numpy as np
from py4design import py3dmodel
from py4design import pyoptimise

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
mtg_file = os.path.join(parent_path, "example_files","mtg", "tree9.txt" )
'''mtg_file = "C://file2analyse.txt"'''

tree_name = "tree1"
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\" + tree_name + ".txt"
canopy_pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\" + tree_name + "_canopy.pts"
trunk_pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\" + tree_name + "_trunk.pts"
result_dir = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\canopy"

identify_canopy = False

interval_height = 0.25
nclusters = 10
vsize_x = 0.25
vsize_y = 0.25
vsize_z = 0.25
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
    
    
def get_start_end_pt(mtg_row, edge_lines_list):
    start_pt_name = mtg_row[1]
    end_pt = (float(mtg_row[3]), float(mtg_row[4]), float(mtg_row[5]))
    radius = float(mtg_row[6])

    #find the start point row
    srow = find_mtg_pt_row(edge_lines_list, start_pt_name)
    start_pt = (float(srow[3]), float(srow[4]), float(srow[5]))
    return start_pt, end_pt, radius, srow

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

def separate_canopy_into_levels(pyptlist, height, zmin, interval_height):
    interval = int(math.ceil(height/interval_height))
    pypts_interval_dict = {}
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
        
    return pypts_interval_dict

def xyz2ijk(pyptlist, xdim, ydim, zdim, xmin, ymin, zmin, intervalk):
    k_voxel_list = [] #list of dictionary arrange in terms of height

    for _ in range(intervalk):
        k_dict = {}
        k_voxel_list.append(k_dict)
        
    for pypt in pyptlist:
        x = pypt[0]
        y = pypt[1]
        z = pypt[2]
        
        i = int((x-xmin)/xdim) 
        j = int((y-ymin)/ydim)
        k = int((z-zmin)/zdim)
            
        g_index = (i,j,k)
        
        k_dict = k_voxel_list[k]
                    
        if g_index in k_dict:
            k_dict[g_index].append(pypt)
        else:
            k_dict[g_index] = [pypt]
    
    return k_voxel_list
#========================================================================================
    
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
    
dae_canopy = os.path.join(result_dir, "tree_canopy_leaves.dae")
dae_canopy_mhulls = os.path.join(result_dir, "tree_canopy_multiple_hulls.dae")
dae_canopy_hull = os.path.join(result_dir, "tree_canopy_hull.dae")

display_2dlist = []
colour_list = []
#========================================================================================
#READ THE CANOPY PT CLOUD
#========================================================================================
pyptlist, pt_cmpd, centre_pt = read_pts_file(canopy_pts_file)
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)
height = zmax-zmin

pyptlist2, pt_cmpd2, centre_pt2 = read_pts_file(trunk_pts_file, delimiter = ",")

#========================================================================================
print "SEPARATING THE POINTS INTO LEVELS ..."
#========================================================================================
if identify_canopy:
    canopy_dict = separate_canopy_into_levels(pyptlist, height, zmin, interval_height)
    levels =  sorted(canopy_dict.keys())
    npt_list = []
    for level in levels:
        pt_list = canopy_dict[level]
        npts = len(pt_list)
        npt_list.append(npts)
    
    diff_list = []
    for ncnt in range(len(npt_list)):
        if ncnt != len(npt_list)-1:
            diff = npt_list[ncnt] - npt_list[ncnt + 1]
            if diff <0:
                diff = diff*-1
            diff_list.append(diff)
    
    level_index = diff_list.index(max(diff_list))
    levels2 = levels[level_index:]
    canopy_pts = []
    for level2 in levels2:
        pt_list = canopy_dict[level2]
        canopy_pts.extend(pt_list)
else:
    canopy_pts = pyptlist

X = np.array(canopy_pts)
#nclusters = pyoptimise.analyse_xml.elbow_test(X, 10)
cluster_dict = pyoptimise.analyse_xml.kmeans(X, nclusters)

cluster_list = cluster_dict["cluster_list"]

hull_face_list = []
for cluster in cluster_list:
    hull_faces = py3dmodel.construct.convex_hull3d(cluster)
    hull_face_list.extend(hull_faces)
    
py3dmodel.export_collada.write_2_collada(dae_canopy_mhulls, occface_list = hull_face_list)

hull_faces = py3dmodel.construct.convex_hull3d(canopy_pts)

py3dmodel.export_collada.write_2_collada(dae_canopy_hull, occface_list = hull_faces)


#========================================================================================
print "VOXELISE ..."
#========================================================================================
intervali = int(math.ceil((xmax-xmin)/vsize_x))
intervalj = int(math.ceil((ymax-ymin)/vsize_y))
intervalk = int(math.ceil((zmax-zmin)/vsize_z))

xmax2 = xmin + (intervali*vsize_x)
ymax2 = ymin + (intervalj*vsize_y)
bp_pyptlist = [(xmin,ymin,zmin), (xmax2,ymin,zmin), (xmax2,ymax2,zmin), (xmin,ymax2,zmin)]
base_plane = py3dmodel.construct.make_polygon(bp_pyptlist)
base_area = py3dmodel.calculate.face_area(base_plane)
grid_face_list = py3dmodel.construct.grid_face(base_plane, vsize_x, vsize_y)
grid_face_list = py3dmodel.modify.sort_face_by_xy(grid_face_list)

grid_cmpd = py3dmodel.construct.make_compound(grid_face_list)
bp_mid_pt = py3dmodel.calculate.face_midpt(base_plane)

voxel_level_list = xyz2ijk(canopy_pts, vsize_x, vsize_y, vsize_z, xmin, ymin, zmin, intervalk)
hint_min = zmin
full_grid = []
voxel_list = []
leaves = []
for cnt in range(intervalk):
    #move the grid to the respective height
    loc_pt = (bp_mid_pt[0], bp_mid_pt[1], hint_min)
    moved_plane = py3dmodel.modify.move(bp_mid_pt, loc_pt, grid_cmpd)
    flist = py3dmodel.fetch.topo_explorer(moved_plane, "face")
    full_grid.extend(flist)
    
    #retrieve the ijk of each cell for each level
    grid_lvl = voxel_level_list[cnt]
    grid_list = []
    
    glist = []
    for cell in grid_lvl:
        ig =cell[0]
        jg = cell[1]
        g_cnt = ig + jg + ((intervali-1)*jg)
        agrid = flist[g_cnt]
            
        grid_list.append(agrid)
        voxel = py3dmodel.construct.extrude(agrid, (0,0,1),vsize_z)
        voxel_list.append(voxel)
        
        ptlist = grid_lvl[cell]
        npts = len(ptlist)
        if npts >=4:
            ran_num = random.randint(6,9)
            hull_faces = py3dmodel.construct.convex_hull3d(ptlist)
            for cnt in range(len(hull_faces)):
                if cnt%ran_num == 0:
                    leaves.append(hull_faces[cnt])
    
    hint_min = zmin + (vsize_z*(cnt+1))
    
#========================================================================================
#MOVE THE LEAVES TO THE CENTRE POINT
#========================================================================================
l_cmpd = py3dmodel.construct.make_compound(leaves)
l_cmpd = py3dmodel.modify.move(centre_pt2, (0,0,0), l_cmpd)
leaves = py3dmodel.fetch.topo_explorer(l_cmpd, "face")
print "NUMBER OF SURFACES FOR LEAVES", len(leaves)
py3dmodel.export_collada.write_2_collada(dae_canopy, occface_list = leaves)

#========================================================================================
#READ THE MTG FILE AND CONSTRUCT A TUBE MODEL
#========================================================================================
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
    
ext_list = []
for ell in edge_lines_list:
    #check if it is an edge
    if ell[1] !="":
        start_pt, end_pt, radius, srow = get_start_end_pt(ell, edge_lines_list)
        extrude, vol = calc_a_volume(start_pt, end_pt, radius)
        ext_list.append(extrude)
        
#========================================================================================
#MOVE THE TUBE MODEL TO THE POINT CLOUDS
#========================================================================================
ext_cmpd = py3dmodel.construct.make_compound(ext_list)
ext_cmpd = py3dmodel.modify.move((0,0,0), centre_pt2, ext_cmpd)
#========================================================================================
#========================================================================================

display_2dlist.append(leaves)
colour_list.append("GREEN")

display_2dlist.append(ext_list)
colour_list.append("RED")

time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time

py3dmodel.utility.visualise(display_2dlist, colour_list = colour_list)