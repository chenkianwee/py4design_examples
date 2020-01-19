import math
import os
import time
from py4design import skyviewfactor
from py4design import py3dmodel

parent_dir = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\pts"
pts_filepath1 = os.path.join(parent_dir, "coldtube_panel2.pts")
pts_filepath2 = os.path.join(parent_dir, "coldtube_panel3.pts")
pts_filepath3 = os.path.join(parent_dir, "coldtube_panel4.pts")
pts_filepath4 = os.path.join(parent_dir, "coldtube_panel6.pts")
pts_filepath5 = os.path.join(parent_dir, "coldtube_panel7.pts")
pts_filepath6 = os.path.join(parent_dir, "coldtube_panel8.pts")

pts_filepath7 = os.path.join(parent_dir, "coldtube_panel9.pts")
pts_filepath8 = os.path.join(parent_dir, "coldtube_panel10.pts")

pts_filepath9 = os.path.join(parent_dir, "coldtube_floor.pts")

ndir = 100

xdim = .05
ydim = .05
zdim = .05

dae_filepath = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\dae\\cap_voxels.dae"
dae_filepath2 = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\dae\\non_voxels.dae"
csv_filepath = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\data\\csv\\view.csv"
#=============================================================================
def gen_dir(ndir):
    unitball = skyviewfactor.tgDirs(ndir)
    dirs = unitball.getDirList()
    xyzs = []
    for dirx in dirs:
        x = dirx.x
        y = dirx.y
        z = dirx.z
        xyz = (x,y,z)
        xyzs.append(xyz)
    return xyzs

def calc_view(pypt, occ_shape, dirs, voxel_dicts, xdim, ydim, zdim, xmin, ymin, zmin, intervalk):
    hits = []
    hit_edges = []
    for dirx in dirs:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(occ_shape, pypt, dirx)
        if interpt:
            ijk = mapxyz2ijk(interpt, xdim, ydim, zdim, xmin, ymin, zmin, intervalk)
            #find which voxel it hits and determine if it hit a capillary
            if ijk in voxel_dicts:
                voxel_dict = voxel_dicts[ijk]
                is_cap = voxel_dict["is_cap"]
                if is_cap:
                    hits.append(dirx)
                    edge = py3dmodel.construct.make_edge(pypt, interpt)
                    hit_edges.append(edge)
            else:
                print("THE POINT DID NOT FIND A VOXEL")
            
    nhits = len(hits)
    view_factor = nhits/float(ndir)
#    print view_factor
    return view_factor, hit_edges

def mapxyz2ijk(pypt, xdim, ydim, zdim, xmin, ymin, zmin, intervalk):
    x = pypt[0]
    y = pypt[1]
    z = pypt[2]
    
    i = int((x-xmin)/xdim) 
    j = int((y-ymin)/ydim)
    k = int((z-zmin)/zdim)
    ijk = (i,j,k)
    return ijk
        
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
            
        ijk = (i,j,k)
        
        k_dict = k_voxel_list[k]
                    
        if ijk in k_dict:
            k_dict[ijk].append(pyptdict)
        else:
            k_dict[ijk] = [pyptdict]
    
    return k_voxel_list

def is_capillary_mat_pt(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    if 80 < r < 160:
        if 90 < g < 170:
            if 90 < b < 200:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
def is_capillary_voxel(avox_pyptdict_list):
    cap_pt_list = []
    for ptdict in avox_pyptdict_list:
        rgb = ptdict["rgb"]
        is_cap_pt = is_capillary_mat_pt(rgb)
        if is_cap_pt:
            cap_pt_list.append(ptdict)
    
    cap_ratio = float(len(cap_pt_list))/float(len(avox_pyptdict_list))
    if cap_ratio > 0.2:
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
    
def read_pts(pts_filepath):
    pyptdict_list = []

    vertex_list = []
    
    pf = open(pts_filepath, "r")
    lines = pf.readlines()
        
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
        pt_dict["vertex"] = occ_vertex
        
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
    return pyptdict_list

def construct_base_plane(pyptdict_list):
    vertex_list = pyptdict_list2vertex_list(pyptdict_list)
    pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
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
    print "N ZVOXELS:", intervalk
    
    print "USING THE BOUNDING BOX TO CONSTRUCT THE BASE PLANE ..."
    #create the bounding plane and grid it 
    xmax2 = xmin + (intervali*xdim)
    ymax2 = ymin + (intervalj*ydim)
    bp_pyptlist = [(xmin,ymin,zmin), (xmax2,ymin,zmin), (xmax2,ymax2,zmin), (xmin,ymax2,zmin)]
    base_plane = py3dmodel.construct.make_polygon(bp_pyptlist)
    grid_face_list = py3dmodel.construct.grid_face(base_plane, xdim, ydim)
    grid_face_list = py3dmodel.modify.sort_face_by_xy(grid_face_list)
    
    grid_cmpd = py3dmodel.construct.make_compound(grid_face_list)
    return grid_cmpd, xmin, ymin, zmin, intervali, intervalk
    
def pyptdict_list2vertex_list(pyptdict_list):
    vertex_list = []
    for pyptdict in pyptdict_list:
        vertex = pyptdict["vertex"]
        vertex_list.append(vertex)
    return vertex_list

def pyptdict_list2pyptlist(pyptdict_list):
    pyptlist = []
    for pyptdict in pyptdict_list:
        pypt = pyptdict["pypt"]
        pyptlist.append(pypt)
    return pyptlist

def construct_voxels(k_voxel_list, base_plane, intervalk, zmin):
    grid3d = []
    voxel_dicts = {}
    bp_mid_pt = py3dmodel.calculate.get_centre_bbox(base_plane)
    
    hint_min = zmin
    for cnt in range(intervalk):
        #move the grid to the respective height
        loc_pt = (bp_mid_pt[0], bp_mid_pt[1], hint_min)
        moved_plane = py3dmodel.modify.move(bp_mid_pt, loc_pt, base_plane)
        flist = py3dmodel.fetch.topo_explorer(moved_plane, "face")
        grid3d.extend(flist)
        
        #retrieve all the voxel at this level
        grid_lvl = k_voxel_list[cnt]
    
        #loop through each cell in this level
        for ijk in grid_lvl:
            voxel_dict = {}
            i =ijk[0]
            j = ijk[1]
            ij = i + j + ((intervali-1)*j)
            
            agrid = flist[ij]
            voxel = py3dmodel.construct.extrude(agrid, (0,0,1),zdim)
            ptdicts = grid_lvl[ijk]
            
            voxel_dict["voxel"] = voxel
            voxel_dict["grid"] = agrid
            voxel_dict["ptdicts"] = ptdicts
            voxel_dict["ijk"] = ijk
            
            is_cap_voxel = is_capillary_voxel(ptdicts)
            if is_cap_voxel:
                voxel_dict["is_cap"] = True
            else:
                voxel_dict["is_cap"] = False
            
            voxel_dicts[ijk] = voxel_dict
        hint_min = zmin + (zdim*(cnt+1))
    return voxel_dicts

def construct_mrt_grid(pyptdict_list, xdim, ydim):
    vertex_list = pyptdict_list2vertex_list(pyptdict_list)
    pyptlist = pyptdict_list2pyptlist(pyptdict_list)
    cmpd = py3dmodel.construct.make_compound(vertex_list)
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(cmpd)
    face = py3dmodel.construct.convex_hull2d(pyptlist)
    midpt = py3dmodel.calculate.face_midpt(face)
    face = py3dmodel.modify.move(midpt, (midpt[0],midpt[1],zmin),face)
    face = py3dmodel.fetch.topo_explorer(face, "face")[0]
    face = py3dmodel.construct.make_offset(face, -0.4)
    grids = py3dmodel.construct.grid_face(face, xdim, ydim)
    return grids

#=============================================================================
time1 = time.time()
print "READING THE PANEL POINTS ... ..."
panel_pyptdict_list2 = read_pts(pts_filepath1)
panel_pyptdict_list3 = read_pts(pts_filepath2)
panel_pyptdict_list4 = read_pts(pts_filepath3)
panel_pyptdict_list6 = read_pts(pts_filepath4)
panel_pyptdict_list7 = read_pts(pts_filepath5)
panel_pyptdict_list8 = read_pts(pts_filepath6)

panel_pyptdict_list9 = read_pts(pts_filepath7)
panel_pyptdict_list10 = read_pts(pts_filepath8)

panel_pyptdict_list = []
panel_pyptdict_list.extend(panel_pyptdict_list2)
panel_pyptdict_list.extend(panel_pyptdict_list3)
panel_pyptdict_list.extend(panel_pyptdict_list4)
panel_pyptdict_list.extend(panel_pyptdict_list6)
panel_pyptdict_list.extend(panel_pyptdict_list7)
panel_pyptdict_list.extend(panel_pyptdict_list8)

panel_pyptdict_list.extend(panel_pyptdict_list9)
panel_pyptdict_list.extend(panel_pyptdict_list10)

print "INDEX THE PANELS PTS ..."
base_plane,xmin,ymin,zmin,intervali,intervalk = construct_base_plane(panel_pyptdict_list)
k_voxel_list = xyz2ijk(panel_pyptdict_list, xdim, ydim, zdim, xmin, ymin, zmin, intervalk)

print "CONSTRUCT THE 3D VOXELS ..."
voxel_dicts = construct_voxels(k_voxel_list, base_plane, intervalk, zmin)

cap_voxel_list = []
non_voxel_list = []
voxel_list = []
for key in voxel_dicts:
    voxel_dict = voxel_dicts[key]
    voxel = voxel_dict["voxel"]
    is_cap = voxel_dict["is_cap"]
    if is_cap:
        cap_voxel_list.append(voxel)
    else:
        non_voxel_list.append(voxel)
    
voxel_list.extend(cap_voxel_list)
voxel_list.extend(non_voxel_list)

colour_list = []
for _ in range(len(cap_voxel_list)):
    colour_list.append([0,0,1])

for _ in range(len(non_voxel_list)):
    colour_list.append([1,1,1])
    
'''
#shrink voxels for calculating view
svoxel_list = []
for voxel in voxel_list:
    v_mid = py3dmodel.calculate.get_centre_bbox(voxel)
    s_voxel = py3dmodel.modify.scale(voxel, 0.95, v_mid)
    svoxel_list.append(s_voxel)
    
print "CONSTRUCT THE FLOOR GRID"
floor_pyptdict_list = read_pts(pts_filepath9)
mrt_grids = construct_mrt_grid(floor_pyptdict_list, 0.5, 0.5)

print "PROJECT RAYS TO CALC THE VIEW FACTOR"
dirs = gen_dir(ndir)
voxel_cmpd = py3dmodel.construct.make_compound(svoxel_list)
view_factor_list = []
hit_edge_list = []
ptlist = []
mrt_pt_list = []
label_list = []
view_factor_str = ""
ngrids = len(mrt_grids)
mcnt = 0
for mrt_grid in mrt_grids:
    gmidpt = py3dmodel.calculate.face_midpt(mrt_grid)
    gmidpt = py3dmodel.modify.move_pt(gmidpt, (0,0,1), 1)
    mrt_pt_list.append(gmidpt)
    view_factor, hit_edges = calc_view(gmidpt, voxel_cmpd, dirs, voxel_dicts,
                                       xdim, ydim, zdim, xmin, ymin, zmin, intervalk)
    
    print "CALC VIEW ... PROGRESS", str(mcnt+1), "/", str(ngrids)
    label = py3dmodel.construct.make_brep_text(str(mcnt), 0.1)
    label = py3dmodel.modify.move((0,0,0), gmidpt, label)
    label_tri = py3dmodel.construct.tessellator(label)
    label_list.extend(label_tri)
    view_factor_str = view_factor_str + str(mcnt) + "," + str(view_factor) + "\n"
    view_factor_list.append(view_factor)
    hit_edge_list.extend(hit_edges)
    mcnt+=1

time2 = time.time()
time_taken = (time2-time1)/60
print "FINISH PROJECTION ...", time_taken

print "WRITING THE VIEW FACTOR CSV"
csv = open(csv_filepath, "w")
csv.write(view_factor_str)
csv.close()

occfaces2write = voxel_list + label_list

py3dmodel.export_collada.write_2_collada_falsecolour(mrt_grids, view_factor_list, 
                                                     "view_factor",dae_filepath,
                                                     other_occface_list = occfaces2write, 
                                                     inverse=True) 

py3dmodel.export_collada.write_2_collada_falsecolour(mrt_grids, view_factor_list, 
                                                     "view_factor",dae_filepath2,
                                                     other_occface_list = occfaces2write, 
                                                     other_occedge_list=hit_edge_list, 
                                                     inverse=True) 
'''
py3dmodel.export_collada.write_2_collada(dae_filepath, occface_list = cap_voxel_list)
py3dmodel.export_collada.write_2_collada(dae_filepath2, occface_list = non_voxel_list)

print "COMPLETE"
#py3dmodel.utility.visualise_falsecolour_topo(mrt_grids, view_factor_list,
#                                             other_occtopo_2dlist = [hit_edge_list,svoxel_list],
#                                             other_colour_list = ["BLACK","WHITE"],
#                                             inverse=True)