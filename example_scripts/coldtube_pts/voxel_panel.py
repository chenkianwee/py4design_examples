import math
from py4design import py3dmodel
#===========================================================================
#INPUTS
#===========================================================================
pts_file = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\pts\\coldtube_panel7.pts"

xdim = .05
ydim = .05
zdim = .05
#===========================================================================
#===========================================================================
def xyz2ijk(pyptdict_list, xdim, ydim, zdim, xmin, ymin, zmin, intervalk):
    k_voxel_list = [] #list of dictionary arrange in terms of height

    for _ in range(intervalk):
        k_dict = {}
        k_voxel_list.append(k_dict)
        
    for pyptdict in pyptdict_list:
        x = pyptdict["pypt"][0]
        y = pyptdict["pypt"][1]
        z = pyptdict["pypt"][2]
        
        i = int((x-xmin)/xdim) 
        j = int((y-ymin)/ydim)
        k = int((z-zmin)/zdim)
            
        g_index = (i,j,k)
        
        k_dict = k_voxel_list[k]
                    
        if g_index in k_dict:
            k_dict[g_index].append(pyptdict)
        else:
            k_dict[g_index] = [pyptdict]
    
    return k_voxel_list

def is_capillary_mat_pt(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    if 80 < r < 160:
        if 90 < g < 170:
            if 130 < b < 200:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
def is_capillary_voxel(ptdicts):
    cap_pt_list = []
    for ptdict in ptdicts:
        rgb = ptdict["rgb"]
        is_cap_pt = is_capillary_mat_pt(rgb)
        if is_cap_pt:
            cap_pt_list.append(ptdict)
    
    cap_ratio = float(len(cap_pt_list))/float(len(ptdicts))
    if cap_ratio > 0.5:
        return True
    else:
        return False
    
def write2pts(pyptlist, ptfilepath, colour_list = None, normal_list = None):
    ptlist_str = ""
    for pcnt in range(len(pyptlist)):
        pt_str = ""
        
        pypt = pyptlist[pcnt]
        pt_str = str(pypt[0])+","+ str(pypt[1])+","+str(pypt[2])
        
        if colour_list != None:
            rgb = colour_list[pcnt]
            pt_str = pt_str + ","+str(rgb[0])+","+ str(rgb[1])+","+str(rgb[2])
        
        if normal_list != None:
            nrml = normal_list[pcnt]
            pt_str = pt_str + ","+str(nrml[0])+","+ str(nrml[1])+","+str(nrml[2])
        
        pt_str = pt_str + "\n"
        ptlist_str = ptlist_str + pt_str
        
    f = open(ptfilepath, "w")
    f.write(ptlist_str)
    f.close()
    
#===========================================================================
#===========================================================================
pyptdict_list = []

vertex_list = []
vertex_list2 = []

print "READING POINT CLOUDS OF ..."
pf = open(pts_file, "r")
lines = pf.readlines()
print "NUMBER OF POINTS:", len(lines)
    
print "ANALYSING POINTS & CONVERTING POINTS TO OCC VERTICES..."
for l in lines:
    pt_dict = {}
    l = l.replace("\n","")
    l_list = l.split(",")
    
    x = float(l_list[0])
    y = float(l_list[1])
    z = float(l_list[2])

    pypt = (x,y,z)
    pt_dict["pypt"] = pypt
    occ_vertex = py3dmodel.construct.make_vertex(pypt)
    
    r = int(l_list[3])
    g = int(l_list[4])
    b = int(l_list[5])
    
    rgb = (r,g,b)
    pt_dict["rgb"] = rgb
    
    nx = float(l_list[6])
    ny = float(l_list[7])
    nz = float(l_list[8])
    
    n = (nx, ny, nz)
    pt_dict["normal"] = n
    
    pyptdict_list.append(pt_dict)
    vertex_list.append(occ_vertex)
    
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
k_voxel_list = xyz2ijk(pyptdict_list, xdim, ydim, zdim, xmin, ymin, zmin, intervalk)

print "VOXELISING..."
zmin_intheight = zmin + zdim
hint_min = zmin
voxel_list = []
voxel_list2 = []
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
    
    glist = []
    for cell in grid_lvl:
        ig =cell[0]
        jg = cell[1]
        g_cnt = ig + jg + ((intervali-1)*jg)
        agrid = flist[g_cnt]
            
        grid_list.append(agrid)
        
        voxel = py3dmodel.construct.extrude(agrid, (0,0,1),zdim)
        
        
        ptdicts = grid_lvl[cell]
        is_cap_voxel = is_capillary_voxel(ptdicts)
        if is_cap_voxel:
            voxel_list.append(voxel)
        else:
            voxel_list2.append(voxel)

    hint_min = zmin + (zdim*(cnt+1))
                

py3dmodel.utility.visualise([voxel_list, voxel_list2], ["RED", "WHITE"])