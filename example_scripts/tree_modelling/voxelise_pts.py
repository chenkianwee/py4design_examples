import os 
import time
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
#pts_file = os.path.join(parent_path, "example_files","pts", "tree9.pts" )
pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree8\\tree8.pts"
dae_filepath = "F:\\kianwee_work\\spyder_workspace\\py4design_examples\\example_files\\dae\\results\\tree8.dae"
v_size = 0.15

xdim = v_size
ydim = v_size
zdim = v_size

reduction_dist = v_size/2.0
#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
def xyz2ijk(pyptlist, xdim, ydim, zdim):
    activated_grid = []
    act_grid_dict = {}
    voxel_dict = {}
    k_list = []
    for pypt in pyptlist:
        x = pypt[0]
        y = pypt[1]
        z = pypt[2]
        
        i = int(round((x/xdim)))
        j = int(round(y/ydim))
        k = int(round(z/zdim))
            
        g_index = (i,j,k)
        
        if g_index in voxel_dict:
            voxel_dict[g_index].append(pypt)
        else:
            voxel_dict[g_index] = [pypt]
            
        if g_index not in activated_grid:        
            activated_grid.append(g_index)
            if g_index[2] in act_grid_dict:
                act_grid_dict[g_index[2]].append((g_index[0], g_index[1]))
            else:
                k_list.append(g_index[2])
                act_grid_dict[g_index[2]] = [(g_index[0], g_index[1])]
    
    return act_grid_dict, k_list, voxel_dict
    

    
        
time1 = time.clock()
print "READING POINT CLOUDS ..."
pf = open(pts_file, "r")
lines = pf.readlines()
#lines = lines[0:1000]
print "NUMBER OF POINTS:", len(lines)

vertex_list = []
pyptlist = []

print "ANALYSING POINTS ..."

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

print "CONVERTING POINTS TO OCC VERTICES FOR COMPUTATION ..."
pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)
    
imin = int(round(xmin/xdim))
jmin = int(round(ymin/ydim))

imax = int(round(xmax/xdim))
jmax = int(round(ymax/ydim))

intervali = int(imax-imin)
intervalj =  int(jmax-jmin)

height = zmax - zmin

print "INDEXING ALL THE POINTS ..."
grid_dict, k_list, voxel_dict = xyz2ijk(pyptlist, xdim, ydim, zdim)
k_list = sorted(k_list)
intervalk = len(k_list)

print "HEIGHT:", height
print "ZMAX:", zmax
print "ZMIN:", zmin
print "INTERVALi:", intervali
print "INTERVALj:", intervalj
print "INTERVALk:", intervalk

print "GRIDDING BOUNDING PLANE ..."
#create the bounding plane and grid it 
xmax2 = xmin + (intervali*xdim)
ymax2 = ymin + (intervalj*ydim)
bp_pyptlist = [(xmin,ymin,zmin), (xmax2,ymin,zmin), (xmax2,ymax2,zmin), (xmin,ymax2,zmin)]
base_plane = py3dmodel.construct.make_polygon(bp_pyptlist)
grid_face_list = py3dmodel.construct.grid_face(base_plane, xdim, ydim)
grid_face_list = py3dmodel.modify.sort_face_by_xy(grid_face_list)
grid_cmpd = py3dmodel.construct.make_compound(grid_face_list)
bp_mid_pt = py3dmodel.calculate.face_midpt(base_plane)


#separate the pts into level intervals and move the bounding plane to each level
print "VOXELISING ..."
#create a list with all the intervals
pypts_interval_dict = {}
zmin_intheight = zmin + zdim
hint_min = zmin
#agrids_list = []
voxel_list = []
for cnt in range(intervalk):
    #move the grid to the respective height
    hint_max = zmin + (zdim*(cnt+1))
    loc_pt = (bp_mid_pt[0], bp_mid_pt[1], hint_min)
    moved_plane = py3dmodel.modify.move(bp_mid_pt, loc_pt, grid_cmpd)
    flist = py3dmodel.fetch.topo_explorer(moved_plane, "face")
    #py3dmodel.utility.visualise_falsecolour_topo(flist, range(len(flist)))
    #retrieve the grid to be activated
    k_key = k_list[cnt]
    act_grids = grid_dict[k_key]
    agrids = []
    for ag in act_grids:
        ig =ag[0]-imin-1
        jg = ag[1]-jmin-1
        g_cnt = jg+ig + ((intervali-1)*jg)
        agrid = flist[g_cnt]
        voxel = py3dmodel.construct.extrude(agrid, (0,0,1),zdim)
        voxel_list.append(voxel)
        #agrids_list.append(agrid)
        
    hint_min = hint_max
    
print "NUMBER OF VOXELS:", len(voxel_list)
print "TOTAL TREE VOL:", xdim*ydim*zdim*len(voxel_list)
time2 = time.clock()
total_time = time2-time1
print "TIME TAKEN (mins):", total_time/60.0

py3dmodel.export_collada.write_2_collada(voxel_list, dae_filepath)
display_2dlist = []
colour_list = []

display_2dlist.append(vertex_list)
colour_list.append("GREEN")
display_2dlist.append(voxel_list)
colour_list.append("WHITE")
py3dmodel.utility.visualise(display_2dlist, colour_list)
