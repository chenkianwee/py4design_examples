import math
from py4design import py3dmodel
#===========================================================================
#INPUTS
#===========================================================================
pts_file = "C:\\Users\\chenkianwee\\Desktop\\sfm_tryouts\\coldtube2\\pts\\coldtube_scaled_low_dense.pts"
xdim = .3
ydim = .3
zdim = .3
#===========================================================================
#===========================================================================
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
#===========================================================================
#===========================================================================
    
vertex_list = []
pyptlist = []

print "READING POINT CLOUDS OF ..."
pf = open(pts_file, "r")
lines = pf.readlines()
print "NUMBER OF POINTS:", len(lines)
    
print "ANALYSING POINTS & CONVERTING POINTS TO OCC VERTICES..."
for l in lines:
    l = l.replace("\n","")
    l_list = l.split(",")
    
    x = float(l_list[0])
    y = float(l_list[1])
    z = float(l_list[2])
    #temp = float(l_list[6])
    pypt = (x,y,z)
    
    occ_vertex = py3dmodel.construct.make_vertex(pypt)
    vertex_list.append(occ_vertex)
    pyptlist.append(pypt)          
    
print "COMPUTING THE BOUNDING BOX FOR THE POINTS..."
pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
cpt = py3dmodel.calculate.get_centre_bbox(pt_cmpd)
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)

intervali = int(math.ceil((xmax-xmin)/xdim))
intervalj = int(math.ceil((ymax-ymin)/ydim))
intervalk = int(math.ceil((zmax-zmin)/zdim))
height = zmax - zmin

print "XSIZE:", xmax-xmin
print "YSIZE:", ymax-ymin
print "HEIGHT:", height
print "N XVOXELS:", intervali
print "N YVOXELS:", intervalj
print "N KVOXELS:", intervalk

print "USING THE BOUNDING BOX TO CONSTRUCT THE 3D GRID ..."
#create the bounding plane and grid it 
xmax2 = xmin + (intervali*xdim)
ymax2 = ymin + (intervalj*ydim)
bp_pyptlist = [(xmin,ymin,zmin), (xmax2,ymin,zmin), (xmax2,ymax2,zmin), (xmin,ymax2,zmin)]
base_plane = py3dmodel.construct.make_polygon(bp_pyptlist)
base_area = py3dmodel.calculate.face_area(base_plane)
grid_face_list = py3dmodel.construct.grid_face(base_plane, xdim, ydim)
grid_face_list = py3dmodel.modify.sort_face_by_xy(grid_face_list)

grid_cmpd = py3dmodel.construct.make_compound(grid_face_list)
bp_mid_pt = py3dmodel.calculate.face_midpt(base_plane)

print "INDEXING ALL THE POINTS ..."
vertex_list = py3dmodel.fetch.topo_explorer(pt_cmpd, "vertex")
occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(vertex_list)
pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
        
k_voxel_list = xyz2ijk(pyptlist, xdim, ydim, zdim, xmin, ymin, zmin, intervalk)

print "VOXELISING..."
pypts_interval_dict = {}
zmin_intheight = zmin + zdim
hint_min = zmin
voxel_list = []
full_grid = []
for cnt in range(intervalk):
    #move the grid to the respective height
    loc_pt = (bp_mid_pt[0], bp_mid_pt[1], hint_min)
    moved_plane = py3dmodel.modify.move(bp_mid_pt, loc_pt, grid_cmpd)
    flist = py3dmodel.fetch.topo_explorer(moved_plane, "face")
    full_grid.extend(flist)
    
    #retrieve the ijk of each cell for each level
    grid_lvl = k_voxel_list[cnt]
    grid_list = []
    
    nee_list = []
    
    glist = []
    for cell in grid_lvl:
        ig =cell[0]
        jg = cell[1]
        g_cnt = ig + jg + ((intervali-1)*jg)
        agrid = flist[g_cnt]
            
        grid_list.append(agrid)
        voxel = py3dmodel.construct.extrude(agrid, (0,0,1),zdim)
        voxel_list.append(voxel)
        
        #ptlist = grid_lvl[cell]
        #pptlist = []
    hint_min = zmin + (zdim*(cnt+1))
                
py3dmodel.utility.visualise([voxel_list], ["WHITE"])
py3dmodel.export_collada.write_2_collada("F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\dae\\voxel.dae",
                                         occface_list = voxel_list)