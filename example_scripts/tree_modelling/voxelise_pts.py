import os 
import time
import math
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE PTS
#================================================================================
#specify the pts file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
#pts_file = os.path.join(parent_path, "example_files","pts", "tree9.pts" )
pts_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\tree9.pts"
dae_filepath = "F:\\kianwee_work\\spyder_workspace\\py4design_examples\\example_files\\dae\\results\\tree66.dae"
#kai=1.59
v_size = 0.5
xdim = v_size
ydim = v_size
zdim = 1.0

sampled_res = 0.006
voxel_area = xdim*ydim
#================================================================================
#INSTRUCTION: SPECIFY THE PTS
#================================================================================
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
    
def xy2ij(pyptlist, xdim, ydim, xmin, ymin):
    pdict = {}
    for pypt in pyptlist:
        x = pypt[0]
        y = pypt[1]

        i = int((x-xmin)/xdim) 
        j = int((y-ymin)/ydim)
            
        g_index = (i,j)
                    
        if g_index in pdict:
            pdict[g_index].append(pypt)
        else:
            pdict[g_index] = [pypt]
    
    return pdict

time1 = time.clock()
print "READING POINT CLOUDS ..."
pf = open(pts_file, "r")
lines = pf.readlines()
print "NUMBER OF POINTS:", len(lines)

vertex_list = []
pyptlist = []

print "ANALYSING POINTS & CONVERTING POINTS TO OCC VERTICES..."

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

print "COMPUTING THE BOUNDING BOX FOR THE POINTS..."
pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
cpt = py3dmodel.calculate.get_centre_bbox(pt_cmpd)
xmin0,ymin0,zmin0,xmax0,ymax0,zmax0 = py3dmodel.calculate.get_bounding_box(pt_cmpd)
intervalk = int(math.ceil((zmax0-zmin0)/zdim))
    
nve = (xdim/sampled_res) * (ydim/sampled_res)
        
parea_2dlist = []
area_2dlist = []
nee_2dlist = []

nvoxel_total_2dlist = []
nvoxel_occ_2dlist = []
nvoxel_empty_2dlist = []

nee_2dlist = []
nve_2dlist = []

base_2dlist = []

for _ in range(intervalk):
    parea_2dlist.append([])
    area_2dlist.append([])
    nee_2dlist.append([])
    nvoxel_total_2dlist.append([])
    nvoxel_occ_2dlist.append([])
    nvoxel_empty_2dlist.append([])
    nee_2dlist.append([])
    nve_2dlist.append([])
    base_2dlist.append([])
    
#turn the trees 180 degree in interval of 10 degrees
for i in range(18):
    print "#==============================="
    print "CALCULATING ...", i+1, "/18" 
    print "#==============================="
    rot = (i+1)*10
    pt_cmpd = py3dmodel.modify.rotate(pt_cmpd, cpt, (0,0,1),rot)
    #py3dmodel.utility.visualise([[pt_cmpd]], ["GREEN"])
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)
    
    intervali = int(math.ceil((xmax-xmin)/xdim))
    intervalj = int(math.ceil((ymax-ymin)/ydim))
    intervalk = int(math.ceil((zmax-zmin)/zdim))
    height = zmax - zmin
    print xmax-xmin
    print ymax-ymin
    print "HEIGHT:", height
    print "ZMAX:", zmax
    print "ZMIN:", zmin
    print "INTERVALi:", intervali
    print "INTERVALj:", intervalj
    print "INTERVALk:", intervalk
    
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
    vertex_list_rot = py3dmodel.fetch.topo_explorer(pt_cmpd, "vertex")
    occptlist_rot = py3dmodel.modify.occvertex_list_2_occpt_list(vertex_list_rot)
    pyptlist_rot = py3dmodel.modify.occpt_list_2_pyptlist(occptlist_rot)
    k_voxel_list = xyz2ijk(pyptlist_rot, xdim, ydim, zdim, xmin, ymin, zmin, intervalk)
    
    print "VOXELISING & CALCULATING THE LAI ..."
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
            
            ptlist = grid_lvl[cell]
            pptlist = []
            
            npts = len(ptlist)
            if npts == 1:
                #print "1 POINT"
                parea = sampled_res**2
                area = voxel_area
                ppt = (ptlist[0][0], ptlist[0][1], hint_min)
                pptlist.append(ppt)
                
            elif npts == 2:
                #print "2 POINTS"
                pt1 = ptlist[0]
                pt2 = ptlist[1]
                pt_dist = py3dmodel.calculate.distance_between_2_pts(pt1, pt2)
                
                ppt1 = (pt1[0], pt1[1], hint_min)
                ppt2 = (pt2[0], pt2[1], hint_min)
                pptlist.append(ppt1)
                pptlist.append(ppt2)
                    
                if pt_dist != 0:
                    area = pt_dist
                    #project the points onto the xy plane
                    parea = py3dmodel.calculate.distance_between_2_pts(ppt1, ppt2)
                else:
                    area = voxel_area
                    parea = 0
                    
            elif npts >= 3:
                try:
                    #print "CONVEX HULL"
                    #create convex hull
                    hull_area, volume = py3dmodel.construct.convex_hull3d(ptlist, return_area_volume = True)
                    #ch3d = py3dmodel.construct.convex_hull3d(ptlist)
                    area = hull_area*0.5
                    proj_ptlist = []
                    for pt in ptlist:
                        ppt = (pt[0],pt[1],hint_min)
                        proj_ptlist.append(ppt)
                    ch2d = py3dmodel.construct.convex_hull2d(proj_ptlist)
                    pptlist.extend(proj_ptlist)
                    parea = py3dmodel.calculate.face_area(ch2d)
                except:
                    #if this fails the points is either coplanar or collinear
                    #check if it is collinear or coplanar
                    is_collinear = py3dmodel.calculate.is_collinear(ptlist)
                    is_coplanar = py3dmodel.calculate.is_coplanar(ptlist)
                    if is_collinear:
                        #print "COLLINEAR", "NPTS", npts
                        dist_dict = {}
                        for pt_cnt in range(npts):
                            pt1 = ptlist[pt_cnt]
                            ppt = (ptlist[pt_cnt][0], ptlist[pt_cnt][1], hint_min)
                            pptlist.append(ppt)
                            for pt_cnt2 in range(npts):
                                if pt_cnt2 != pt_cnt:
                                    pt2 = ptlist[pt_cnt2]
                                    pt_dist = py3dmodel.calculate.distance_between_2_pts(pt1, pt2)
                                    dist_dict[(pt1,pt2)] = pt_dist
                                    
                        fitems = dist_dict.items()
                        fitems.sort(key=lambda x: [x[1][0]])
                        area = fitems[-1][1]
                        ptlist2 = fitems[-1][0]
                        pt3 = ptlist2[0]
                        pt4 = ptlist2[1]
                        ppt3 = (pt3[0], pt3[1], hint_min)
                        ppt4 = (pt4[0], pt4[1], hint_min)
                        parea = py3dmodel.calculate.distance_between_2_pts(ppt3, ppt4)
                            
                    elif is_coplanar:
                        print "COPLANAR", "NPTS", npts
                        tri = py3dmodel.construct.delaunay3d(ptlist, tolerance = 1e-08)
                        area = py3dmodel.calculate.face_area(tri[0])
                        proj_ptlist = []
                        for pt in ptlist:
                            ppt = (pt[0],pt[1],hint_min)
                            proj_ptlist.append(ppt)
                        pptlist.extend(proj_ptlist)
                        ptri = py3dmodel.construct.delaunay3d(proj_ptlist, tolerance=1e-10)
                        parea = py3dmodel.calculate.face_area(ptri[0])
            
            #append the area and projected area into a list
            parea_2dlist[cnt].append(parea)
            area_2dlist[cnt].append(area)
            
            #index the project points onto a pixel in the voxel with xdim and ydim equal to the sample scan
            vlist = []
            for ppt in pptlist:
                v = py3dmodel.construct.make_vertex(ppt)
                vlist.append(v)
                
            vcmpd = py3dmodel.construct.make_compound(vlist)
            xminv, yminv, zminv, xmaxv, ymaxv, zmaxv = py3dmodel.calculate.get_bounding_box(agrid)
            #grid_list2 = py3dmodel.construct.grid_face(agrid, sampled_res, sampled_res)
            #py3dmodel.utility.visualise([vlist, grid_list2], ["GREEN", "BLUE"])
            pdict = xy2ij(pptlist, sampled_res, sampled_res, xminv, yminv)
            nee = nve - len(pdict)
            nee_list.append(nee)
            
        hint_min = zmin + (zdim*(cnt+1))
        
        #get the number of empty voxels for the whole level k
        nvoxel_total = len(flist)
        nvoxel_occ = len(grid_list)
        nvoxel_empty = nvoxel_total - nvoxel_occ
        
        nvoxel_total_2dlist[cnt].append(nvoxel_total)
        nvoxel_occ_2dlist[cnt].append(nvoxel_occ)
        nvoxel_empty_2dlist[cnt].append(nvoxel_empty)
        
        nee_total = sum(nee_list)
        nve_total = (nve*len(nee_list))
        
        nee_2dlist[cnt].append(nee_total)
        nve_2dlist[cnt].append(nve_total)
        
        base_2dlist[cnt].append(base_area)
        
    print "NUMBER OF VOXELS:", len(voxel_list)
    print "TOTAL TREE VOL:", xdim*ydim*zdim*len(voxel_list)

    
leaf_area = 0
lai_e = 0
for kcnt in range(intervalk):
    parea_k_list = parea_2dlist[kcnt]
    area_k_list = area_2dlist[kcnt]
    extinction_coef = sum(parea_k_list)/sum(area_k_list)
    print "EXTINCTION COEFFICIENT", extinction_coef
    
    nee_list = nee_2dlist[kcnt]
    nve_list = nve_2dlist[kcnt]
    
    nvoxel_total_list = nvoxel_total_2dlist[kcnt]
    nvoxel_occ_list = nvoxel_occ_2dlist[kcnt]
    nvoxel_empty_list = nvoxel_empty_2dlist[kcnt]
    
    gap_fraction1 = sum(nvoxel_empty_list)/float(sum(nvoxel_total_list))
    gap_fraction2 = ((sum(nee_list)/float(sum(nve_list)))*sum(nvoxel_occ_list))/sum(nvoxel_total_list)
    gap_fraction = gap_fraction1 + gap_fraction2
    print "GAP FRACTION", gap_fraction
    
    
    base_list = base_2dlist[kcnt]
    avg_barea = sum(base_list)/len(base_list)
    lai_k = math.log(gap_fraction)/(extinction_coef*-1)
    lai_e+= lai_k
    leaf_areak = lai_k*avg_barea
    leaf_area += leaf_areak
    print "LAI", lai_k, "LEAF AREA K", leaf_areak
    
print "EFFECTIVE LEAF AREA", leaf_area, "EFFECTIVE LEAF AREA INDEX", lai_e
time2 = time.clock()
total_time = time2-time1
print "TIME TAKEN (mins):", total_time/60.0

py3dmodel.export_collada.write_2_collada(voxel_list, dae_filepath)

display_2dlist = []
colour_list = []

display_2dlist.append([pt_cmpd])
colour_list.append("GREEN")
display_2dlist.append(voxel_list)
colour_list.append("WHITE")
py3dmodel.utility.visualise(display_2dlist, colour_list)
