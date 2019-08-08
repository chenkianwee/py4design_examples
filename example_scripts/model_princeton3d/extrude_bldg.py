import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile
from laspy.file import File
import numpy as np

#===========================================================================================
#INPUTS
#===========================================================================================
grid_shpfile = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_context_grid\\princeton_context_grid_10by10km.shp"
#specify the directory to store the results which includes
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context"
#specify if you want to view the result interactively
viewer = True
#===========================================================================================
#CONSTANTS
#===========================================================================================
bldg_footprint_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\buildings_2015_princeton\\buildings_2015_princeton.shp"
bldg_centrept_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\buildings_centrept_2015_princeton\\buildings_centrept_2015_princeton.shp"
#specify the terrain directory
terrain_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrains"
#specify the pt cloud directory
pt_cloud_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las"
#===========================================================================================
#FUNCTION
#===========================================================================================
def read_sf_poly(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occfaces = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            for occface in occfaces:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(occface)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list
        
def read_sf_pt(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pts = shp2citygml.get_geometry(rec)
        if pts:
            for pt in pts:
                pypt = (pt[0], pt[1], 0)
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(pypt)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)
        
def get_sf_bdry(shpatt_list):
    occface_list = []
    for shpatt in shpatt_list:
        occface = shpatt.shape
        occface_list.append(occface)
    cmpd = py3dmodel.construct.make_compound(occface_list)
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(cmpd)
    return xmin, ymin, zmin, xmax, ymax, zmax

def find_las_file(folder_dirs):
    lasfile = ""
    for dirx in folder_dirs:
        split_dir = dirx.split(".")
        if len(split_dir) > 1:
            filetype = split_dir[1]
            if filetype == "las":
              lasfile = dirx
    return lasfile

def get_las_file_bdry(las_filepath):
    lasfile = File(las_filepath, mode='r')
    mx = lasfile.header.max
    mn = lasfile.header.min
    #lasfile.close()
    mn.extend(mx)
    return mn, lasfile

def make_bdry_face2d(mn_mx_list):
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face
    
def calc_pt_in_bdry2d(lasfile, mn_mx_list):
    pyptlist = []
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    xvalid = np.logical_and(lasfile.x >= xmin, lasfile.x <= xmax)
    yvalid = np.logical_and(lasfile.y >= ymin , lasfile.y <= ymax )
    valid_indices = np.where(np.logical_and(xvalid, yvalid))
    coords = np.vstack((lasfile.x, lasfile.y, lasfile.z)).transpose()
    valid_pts = np.take(coords, valid_indices, axis = 0)[0]
 
    for pt in valid_pts:    
        x =  pt[0]
        y =  pt[1]
        z =  pt[2]
        pypt =[x,y,z]
        pyptlist.append(pypt)
        
    return pyptlist

def move_footprint2elev(footprint, terrain_pt, tzmin, tzmax):
    m_footprint = py3dmodel.modify.move([0,0,0], [0,0,tzmin-10], footprint)
    m_footprint = py3dmodel.fetch.topo2topotype(m_footprint)
    try:
        extrude = py3dmodel.construct.extrude(m_footprint,[0,0,1], tzmax+10)
        common = py3dmodel.construct.boolean_common(extrude, terrain_pt)
        cxmin, cymin, czmin, cxmax, cymax, czmax = py3dmodel.calculate.get_bounding_box(common)
        
    except:
        vlist = py3dmodel.fetch.topo_explorer(terrain_pt, "vertex")
        occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
        pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
        centrept = py3dmodel.calculate.face_midpt(footprint)
        dist_list = []
        for pypt in pyptlist:
            min_dist = py3dmodel.calculate.distance_between_2_pts(pypt, centrept)
            dist_list.append(min_dist)
            
        czmin = min(dist_list)
        
    m_footprint2 = py3dmodel.modify.move([0,0,0], [0,0,czmin], footprint)
    m_footprint2 = py3dmodel.fetch.topo2topotype(m_footprint2)
    return m_footprint2, czmin, m_footprint
        

def find_bldgs_in_grid(grid, centrept_list, bldg_dict):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(grid)
    bldg_ftprint_list = []
    uid_list = []
    for c in centrept_list:
        pypt = c.shape
        x = pypt[0]
        y = pypt[1]
        if xmin <= x <= xmax and ymin <= y <= ymax:
            uid = c.get_value("unique_id")
            uid_list.append(uid)
            bldg_footprint = bldg_dict[uid]
            bldg_ftprint_list.append(bldg_footprint)
    return bldg_ftprint_list, uid_list
    
def shpatt2dict_uniqueid(shpatt_list):
    d = {}
    for s in shpatt_list:
        shape = s.shape
        uid = s.get_value("unique_id")
        d[uid] = shape
    return d

def identify_lasfile2use(bdry_face, pt_cloud_dir):
    #===========================================================================================
    #READ THE PT CLOUDS & IDENTIFY WHICH TO USE 
    #===========================================================================================
    lasfile_list = []
    list_dir = os.listdir(pt_cloud_dir)
    for dirx in list_dir:
        las_folder = os.path.join(pt_cloud_dir, dirx)
        folder_dirs = os.listdir(las_folder)
        lasfilename = find_las_file(folder_dirs)
        las_filepath = os.path.join(pt_cloud_dir, dirx, lasfilename)
        las_bdry, lasfile = get_las_file_bdry(las_filepath)
        
        bdry_face_pts = make_bdry_face2d(las_bdry)
        intersect = py3dmodel.construct.boolean_common(bdry_face, bdry_face_pts)
        int_face_list = py3dmodel.fetch.topo_explorer(intersect, "face")
        if int_face_list:
            #py3dmodel.utility.visualise([[bdry_face_bldg],[bdry_face_pts], int_face_list], ["WHITE", "RED", "BLUE"])
            lasfile_list.append(lasfile)
        else:
            lasfile.close()
            
    return lasfile_list

def extrude_bldg(ftprint, terrain, lasfile_list, tzmin, tzmax):
    #py3dmodel.utility.visualise([[ftprint], [terrain]], ["WHITE", "GREEN"])
    ftprint_moved, elev, lowest_ftprint = move_footprint2elev(ftprint, terrain, tzmin, tzmax)
    
    #loop through the pts and find the roof points
    ftprint_centroid = py3dmodel.calculate.face_midpt(ftprint)
    ftprint_large = py3dmodel.modify.scale(ftprint, 1.1, ftprint_centroid)
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(ftprint_large)

    pyptlist = []
    for las in lasfile_list:
        #FIND THE POINTS WITHIN THE BOUNDARY OF THE BOUNDING BOX
        laspts = calc_pt_in_bdry2d(las,[xmin, ymin, zmin, xmax, ymax, zmax])
        if laspts:
            pyptlist.extend(laspts)
    
    npts = len(pyptlist)
    if npts > 10:
        #THE PARAMETERS FOR DIVIDING THE POINTS INTO DIFFERENT HEIGHT LEVELS
        interval = 0.2
        pt_ratio = 0.3
        hdiff = 5
        ground_buffer = 2.5
        
        lowest_ftprint = remove_hole(lowest_ftprint)
        face_pts = py3dmodel.fetch.points_frm_occface(lowest_ftprint)
        face_area = py3dmodel.calculate.face_area(lowest_ftprint)
        face_complex = len(face_pts)
        #print "face complexity", face_complex, "area", face_area
        #==========================================================================================
        #IF THE FACE IS NOT COMPLEX OR ELSE THE SCRIPT DOES NOT DO THE BOOLEAN INTERSECT OPERATION
        #==========================================================================================
        if face_complex <= 50 and face_area <= 2500:
            #THE FACE IS NOT COMPLEX
            extrude = py3dmodel.construct.extrude(lowest_ftprint, (0,0,1), (tzmax-tzmin)+10)
            #py3dmodel.utility.visualise([[extrude],[cmpd]], ["WHITE","BLUE"])
            #FIND THE POINTS SPECIFICALLY WITHIN THE FOOTPRINT
            vlist = py3dmodel.construct.make_occvertex_list(pyptlist)
            cmpd = py3dmodel.construct.make_compound(vlist)
            common = py3dmodel.construct.boolean_common(extrude, cmpd)
            
            #py3dmodel.utility.visualise([[ftprint_moved],[common]], ["WHITE","BLUE"])
        else:
            #THE FACE IS COMPLEX
            common = process_complex_face(lowest_ftprint, pyptlist, tzmin, tzmax)            
        
        is_null = py3dmodel.fetch.is_compound_null(common)
        
        if not is_null:
            xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = py3dmodel.calculate.get_bounding_box(common)
            vlist2 = py3dmodel.fetch.topo_explorer(common, "vertex")
            occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(vlist2)
            pyptlist2 = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
            zmin1 = elev + ground_buffer #exclude the ground
            
            #py3dmodel.utility.visualise([[ftprint_moved],[common]], ["WHITE","BLUE"])
            
            pt_lvl_dict = separate_pts_into_lvl(pyptlist2, zmax1, zmin1, height_division = interval)
            if pt_lvl_dict:
                densest_height = identify_bldg_height(pt_lvl_dict, pt_ratio = pt_ratio, height_diff = hdiff)
                bldg = py3dmodel.construct.extrude(ftprint_moved, (0,0,1), (densest_height-elev) + interval)
                
                #print "BLDG HEIGHT", densest_height
                return bldg, common
            else:
                return None, None
        else:
            return None, None
    else:
        return None, None
            
def remove_hole(occface):
    wire_list = py3dmodel.fetch.topo_explorer(occface, "wire")
    nwires = len(wire_list)
    if nwires > 1:
        face_nrml = py3dmodel.calculate.face_normal(occface)
        wire_face = None
        for wire in wire_list:
            #first check if there are holes and which wire are holes
            pyptlist = py3dmodel.fetch.points_frm_wire(wire)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, face_nrml)
            #create face from the wires
            if is_anticlockwise:
                wire_face = py3dmodel.construct.make_face_frm_wire(wire)
    
        return wire_face
    else:
        return occface
            
def process_complex_face(complex_face, pyptlist, tzmin, tzmax):
    #first divide up the complex face
    pyptlist2 = pyptlist[:]
    grids = py3dmodel.construct.grid_face(complex_face, 50,50)    
    res_vlist = []
    cnt = 0
    for g in grids:
        res_pts, pyptlist2 = find_pts_in_bdry(g, pyptlist2)
        if res_pts:
            res_vs = py3dmodel.construct.make_occvertex_list(res_pts)
            res_vlist.extend(res_vs)
        cnt+=1
        
    res_cmpd = py3dmodel.construct.make_compound(res_vlist)
    #py3dmodel.utility.visualise([[res_cmpd]], ["BLACK"])
    return res_cmpd
    
def find_pts_in_bdry(grid, pyptlist):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(grid)
    find_pts = []
    left_pts = []
    for pypt in pyptlist:
        x = pypt[0]
        y = pypt[1]
        if xmin <= x <= xmax and ymin <= y <= ymax:
            find_pts.append(pypt)
        else:
            left_pts.append(pypt)
    return find_pts, left_pts

def get_all_terrain(terrain_dir):
    n_terrains = 420
    t_list = []
    for i in range(n_terrains):
        t_filename = "terrain_10by10km_pt_" + str(i) + ".brep"
        t_filepath = os.path.join(terrain_dir, t_filename)
        terrain = py3dmodel.utility.read_brep(t_filepath)
        t_list.append(terrain)
    return t_list

def identify_terrain(grid, terrain_list):
    identified = []
    for terrain in terrain_list:
        xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(terrain)
        t_face = make_bdry_face2d([xmin, ymin, zmin, xmax, ymax, zmax])
        common = py3dmodel.construct.boolean_common(t_face, grid)
        if not py3dmodel.fetch.is_compound_null(common):
            identified.append(terrain)
        
    return identified

def identify_bldg_height(pt_lvl_dict, pt_ratio = 0.5, height_diff = 5):
    keys = pt_lvl_dict.keys()
    npt_list = []
    for key in keys:
        pt_list = pt_lvl_dict[key]
        npts = len(pt_list)
        
        npt_list.append(npts)
        
    mx = max(npt_list)
    dcnt_list = []
    dcnt = 0
    for d in npt_list:
        r = float(d)/float(mx)
        if round(r,1) >= pt_ratio:
            dcnt_list.append(dcnt)
        dcnt+=1
    
    h_list = []
    for c in dcnt_list:
        h = keys[c]
        h_list.append(h)
        
    s_h_list = sorted(h_list, reverse=True)
    diffh_list = []
    hcnt = 0
    for h in s_h_list:
        if hcnt != len(s_h_list)-1:
            nxth = s_h_list[hcnt+1]
            diffh = h-nxth
            diffh_list.append(diffh)
        hcnt+=1
    
    chosen_index = 0
    dhcnt = 0
    for dh in diffh_list:
        if round(dh,2) <= round(height_diff,2):
            if dhcnt < len(diffh_list)-4:
                dh1 = round(diffh_list[dhcnt+1],2)
                dh2 = round(diffh_list[dhcnt+2],2)
                dh3 = round(diffh_list[dhcnt+3],2)
                if dh1 <= height_diff and dh2 <= height_diff and dh3 <= height_diff:
                    chosen_index = dhcnt
                    break
            else:
                chosen_index = dhcnt
                break
        dhcnt+=1
    
    densest_height = s_h_list[chosen_index]
    return densest_height
        
def separate_pts_into_lvl(pyptlist, zmax, zmin, height_division = 0.2):
    import math
    height = zmax-zmin
    interval = int(math.ceil(height/height_division))
    #create a list with all the intervals
    pypts_interval_dict = {}
    #separate the pts into level intervals
    zmin_intheight = zmin + height_division
    imin = zmin
    for cnt in range(interval):
        imax = zmin_intheight + (height_division*cnt)
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
        
def close_lasfiles(lasfile_list):
    for lfile in lasfile_list:
        lfile.close()
        
#===========================================================================================
#READ THE  SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading Grid File***************"
grid_shpatt_list = read_sf_poly(grid_shpfile)
print "*******Reading Centre Point File***************"
bcentrept_list = read_sf_pt(bldg_centrept_shp_file)
print "*******Reading Building File***************"
bldg_list = read_sf_poly(bldg_footprint_shp_file)
bldg_dict = shpatt2dict_uniqueid(bldg_list)

#read all the terrains
print "*******Getting All the Terrains***************"
terrain_list = get_all_terrain(terrain_dir)
print "*******Preparing to Extrude Building***************"
tzmin = 11
tzmax = 107
ngrids = len(grid_shpatt_list)
bldg_cmpd_list = []
uid_list2 = []
gcnt=0
for g in grid_shpatt_list:
    print "*******Processing Folder", gcnt+1, "of", ngrids, "***************"
    grid = g.shape
    uid = g.get_value("id")
    
    uid_list2.append(uid)
    print "********Folders Processed*************"
    print uid_list2
    
    uid_list = [27, 26, 25, 24, 31, 30, 29, 28, 3, 2, 7, 6, 5, 4, 11, 10, 9, 8, 15, 14, 13, 12, 241, 240, 247, 246, 
                245, 244, 251, 250, 249, 248, 255, 254, 253, 252, 227, 226, 225, 224, 231, 230, 229, 228, 235, 234,
                233, 232, 239, 238, 237, 236, 215, 214, 213, 212, 219, 218, 217, 216, 223, 222, 195, 194, 193, 192, 
                197, 196, 203, 202, 201, 200, 206, 205, 204, 179, 178, 183, 182, 181, 180, 191, 190, 161, 160, 171, 
                170, 169, 168, 175, 174, 173, 172, 147, 146, 151, 150, 149, 148, 153, 152, 159, 158, 157, 156, 131, 
                130, 129, 128, 135, 134, 139, 138, 137, 136, 371, 370, 369, 368, 373, 372, 379, 378, 377, 376, 383, 
                382, 381, 380, 355, 354, 359, 358, 357, 356, 363, 362, 361, 360, 367, 366, 365, 364, 337, 336, 343, 
                342]
    
    if uid in uid_list:
        pass
    
    else:
        #get the footprints in the grid
        bldg_footprints, buid_list = find_bldgs_in_grid(grid, bcentrept_list, bldg_dict)
        #get the corresponding pt clouds
        lasfile_list = identify_lasfile2use(grid, pt_cloud_dir)
        id_ts = identify_terrain(grid, terrain_list)
        nt = len(id_ts)
        
        
        nb = len(bldg_footprints)
        bldg_list = []
        bldg_pt_list = []
        bcnt = 0
        print "*******Extrude Building***************"
        for bf in bldg_footprints:
            buid = buid_list[bcnt]
            if nt > 1:
                id_t_list = identify_terrain(bf, id_ts)
                id_t = py3dmodel.construct.make_compound(id_t_list)
            else:
                id_t = id_ts[0]
                
            #if uid == 341 and bcnt+1 == 1:
            #if uid == 95 and buid == 3480:
            print "*******Extruding Folder", uid, "Building", bcnt+1, "/", nb, "***************"
            extruded_bldg, bldg_pts = extrude_bldg(bf, id_t, lasfile_list, tzmin, tzmax)
            if extruded_bldg:
                #py3dmodel.utility.visualise([[extruded_bldg], [bldg_pts]], ["WHITE", "BLUE"])
                bldg_list.append(extruded_bldg)
                bldg_pt_list.append(bldg_pts)
            else:
                print "***********building ", bcnt+1, "cannot be extruded"
                #py3dmodel.utility.visualise([[extruded_bldg],[bldg_pts]], ["WHITE","BLUE"])
                                
            bcnt +=1
    
        close_lasfiles(lasfile_list)
        
        if bldg_list:
            print "*******Writing to File" + str(uid), "***************"
            #create folder for each grid and name it after the unique id
            grid_folderpath = os.path.join(result_directory, str(uid))
            if not os.path.isdir(grid_folderpath):
                os.mkdir(grid_folderpath)
            bldg_filepath = os.path.join(grid_folderpath, "bldg.brep")
            bldg_pt_filepath = os.path.join(grid_folderpath, "bldg_pt.brep")
            terrain_filepath = os.path.join(grid_folderpath, "terrain.brep")
        
            cmpd = py3dmodel.construct.make_compound(bldg_list)
            bldg_cmpd_list.append(cmpd)
            py3dmodel.utility.write_brep(cmpd, bldg_filepath)
            
            pt_cmpd = py3dmodel.construct.make_compound(bldg_pt_list)
            py3dmodel.utility.write_brep(pt_cmpd, bldg_pt_filepath)
            
            t_cmpd = py3dmodel.construct.make_compound(id_ts)
            py3dmodel.utility.write_brep(t_cmpd, terrain_filepath)
    
    time2 = time.clock()
    total_time = time2-time1
    print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
if viewer == True:
    py3dmodel.utility.visualise([bldg_cmpd_list])