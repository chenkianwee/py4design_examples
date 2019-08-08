import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile
from laspy.file import File
import numpy as np

#===========================================================================================
#INPUTS
#===========================================================================================
grid_shpfile = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\forrestal_campus_grid\\forrestal_campus_grid.shp"
#specify the directory to store the results which includes
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\forrestal_campus"
res_filename = "tree5by5m.brep"
res_pt_filename = "tree5by5m_pt.brep"

pervious_filename = "pervious5by5m.shp"
grid_size = 5*5
pt_resolution = 5 #pts/m2

#specify if you want to view the result interactively
viewer = False
#===========================================================================================
#CONSTANTS
#===========================================================================================
#specify pervious directory
pervious_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\pervious"
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
        
def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)

def project_road2terrain(road, terrain_shell, tzmin, tzmax):
    m_face = py3dmodel.modify.move([0,0,0], [0,0,tzmin-10], road)
    m_face = py3dmodel.fetch.topo2topotype(m_face)
    extrude = py3dmodel.construct.extrude(m_face,[0,0,1], tzmax+10)
    common = py3dmodel.construct.boolean_common(extrude, terrain_shell)
    #common = py3dmodel.modify.move([0,0,0], [0,0,0.1], common)
    shell_list = py3dmodel.fetch.topo_explorer(common, "shell")
    return shell_list    

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


def calc_pt_in_bdry3d(lasfile, mn_mx_list):
    pyptlist = []
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    zmin = mn_mx_list[2]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    zmax = mn_mx_list[5]
    
    xvalid = np.logical_and(lasfile.x >= xmin, lasfile.x <= xmax)
    yvalid = np.logical_and(lasfile.y >= ymin , lasfile.y <= ymax )
    zvalid = np.logical_and(lasfile.z >= zmin , lasfile.z <= zmax )
    valid_indices = np.where(np.logical_and(xvalid, yvalid, zvalid))
    coords = np.vstack((lasfile.x, lasfile.y, lasfile.z)).transpose()
    valid_pts = np.take(coords, valid_indices, axis = 0)[0]
 
    for pt in valid_pts:    
        x =  pt[0]
        y =  pt[1]
        z =  pt[2]
        pypt =[x,y,z]
        pyptlist.append(pypt)
        
    return pyptlist

def filter_pyptlist_z(pyptlist, zmin):
    filtered = []
    for pypt in pyptlist:
        z = pypt[2]
        if z > zmin:
            filtered.append(pypt)
    return filtered        

def find_terrain(footprint, terrain_shell, tzmin, tzmax):
    m_footprint = py3dmodel.modify.move([0,0,0], [0,0,tzmin-10], footprint)
    m_footprint = py3dmodel.fetch.topo2topotype(m_footprint)
    extrude = py3dmodel.construct.extrude(m_footprint,[0,0,1], tzmax+10)
    common = py3dmodel.construct.boolean_common(extrude, terrain_shell)
    if not py3dmodel.fetch.is_compound_null(common):
        cxmin, cymin, czmin, cxmax, cymax, czmax = py3dmodel.calculate.get_bounding_box(common)
        m_footprint2 = py3dmodel.modify.move([0,0,0], [0,0,czmin], footprint)
        m_footprint2 = py3dmodel.fetch.topo2topotype(m_footprint2)
        return m_footprint2, czmin, m_footprint, czmax
    else:
        return None, None, None, None

def get_all_terrain(terrain_dir):
    n_terrains = 420
    t_list = []
    for i in range(n_terrains):
        t_filename = "terrain_10by10km_pt_" + str(i) + ".brep"
        t_filepath = os.path.join(terrain_dir, t_filename)
        terrain = py3dmodel.utility.read_brep(t_filepath)
        t_list.append(terrain)
    return t_list

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

def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list

def identify_terrain(grid, terrain_list):
    identified = []
    for terrain in terrain_list:
        xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(terrain)
        t_face = make_bdry_face2d([xmin, ymin, zmin, xmax, ymax, zmax])
        common = py3dmodel.construct.boolean_common(t_face, grid)
        if not py3dmodel.fetch.is_compound_null(common):
            identified.append(terrain)
        
    return identified

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

def gen_tree(tree_grid, terrain, lasfile_list, tzmin, tzmax, pts_in_grid, pts_ratio):
    #py3dmodel.utility.visualise([[ftprint], [terrain]], ["WHITE", "GREEN"])
    ftprint_moved, elev, lowest_ftprint = move_footprint2elev(tree_grid, terrain, tzmin, tzmax)
    
    #loop through the pts and find the roof points
    ftprint_centroid = py3dmodel.calculate.face_midpt(tree_grid)
    ftprint_large = py3dmodel.modify.scale(tree_grid, 1.1, ftprint_centroid)
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(ftprint_large)

    pyptlist = []
    for las in lasfile_list:
        #FIND THE POINTS WITHIN THE BOUNDARY OF THE BOUNDING BOX
        laspts = calc_pt_in_bdry2d(las,[xmin, ymin, zmin, xmax, ymax, zmax])
        if laspts:
            pyptlist.extend(laspts)
    
    lowest_ftprint = remove_hole(lowest_ftprint)
    lowest_ftprint2 = py3dmodel.modify.move([0,0,0], [0,0,2.5], lowest_ftprint)
    lowest_ftprint2 = py3dmodel.fetch.topo_explorer(lowest_ftprint2, "face")[0]
    
    extrude = py3dmodel.construct.extrude(lowest_ftprint2, (0,0,1), (tzmax-tzmin)+10)
    
    vlist = py3dmodel.construct.make_occvertex_list(pyptlist)
    cmpd = py3dmodel.construct.make_compound(vlist)
    common = py3dmodel.construct.boolean_common(extrude, cmpd)        
    is_null = py3dmodel.fetch.is_compound_null(common)
    if not is_null:
        xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = py3dmodel.calculate.get_bounding_box(common)
        if zmax1-elev >= 3:
            vlist2 = py3dmodel.fetch.topo_explorer(common, "vertex")
            occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(vlist2)
            pyptlist2 = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
            npts = len(pyptlist2)
            if npts >= pts_in_grid*pts_ratio:
                t_height = zmax1-elev
                tx = xmax1-xmin1
                ty = ymax1-ymin1
                tree_cmpd = model_tree(t_height, tree_grid, elev, tx, ty)
                tree_pts = py3dmodel.construct.make_compound(vlist2)
                return tree_cmpd, tree_pts
            else:
                return None, None
        else:
            return None, None
    else:
        return None, None
    
def model_tree(tree_height, tree_grid, tree_elev, tree_sizex, tree_sizey):
    #DRAW THE STICK
    #trunk_height = 0.6*tree_height
    g_midpt = py3dmodel.calculate.face_midpt(tree_grid)
    g_midpt = [g_midpt[0], g_midpt[1], tree_elev]
    m_midpt = py3dmodel.modify.move_pt(g_midpt, [0,0,1], tree_height)
    e = py3dmodel.construct.make_edge(g_midpt, m_midpt)
    #DRAW THE CANOPY
    cx = int(tree_sizex/2)
    cy = int(tree_sizey/2)
    tree_list = [e]
    if cx !=0:
        c1 = py3dmodel.construct.make_polygon_circle(m_midpt, [0,1,0], cx, division = 3)
        c1 = py3dmodel.modify.uniform_scale(c1, 1, 1, (0.4*tree_height)/(cx*2), m_midpt)
        tree_list.append(c1)
    
    if cy !=0:
        c2 = py3dmodel.construct.make_polygon_circle(m_midpt, [1,0,0], cy, division = 3)
        c2 = py3dmodel.modify.uniform_scale(c2, 1, 1, (0.4*tree_height)/(cy*2), m_midpt)
        tree_list.append(c2)
        
    tree_cmpd = py3dmodel.construct.make_compound(tree_list)
    return tree_cmpd
            
            
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

#===========================================================================================
#READ THE SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading the shpfile***************"
shpatt_list = read_sf_poly(grid_shpfile)
#===========================================================================================
#READ TERRAIN
#===========================================================================================
#read all the terrains
print "*******Getting All the Terrains***************"
terrain_list = get_all_terrain(terrain_dir)

pts_in_grid = grid_size * pt_resolution
pts_ratio = 0.3

tzmin = 11
tzmax = 107

uid_list2 = []
ngrids = len(shpatt_list)

tree_cmpd_list = []

gcnt = 0
for gatt in shpatt_list:
    grid = gatt.shape
    uid = gatt.get_value("id")
    uid_list2.append(uid)
    print "********Folders Processed*************"
    print uid_list2
    
    uid_list = [272, 339, 295]
    
    if uid in uid_list:
        pass
    
    else:
        print "*******Processing Folder", uid, "Folder", gcnt+1, "of", ngrids, "***************"
        #get the corresponding pt clouds
        lasfile_list = identify_lasfile2use(grid, pt_cloud_dir)
        #get the corresponding terrain
        id_ts1 = identify_terrain(grid, terrain_list)
        nt = len(id_ts1)
        #get the corresponding pervious grids
        filepath = os.path.join(pervious_dir, str(uid), pervious_filename)
        patt_list = read_sf_poly(filepath)
        grids = extract_shape_from_shapatt(patt_list)
        ntrees = len(grids)
        
        tree_list = []
        tree_pt_list = []

        print "*******Estimate Trees***************"
        tcnt = 0
        for t in grids:
            print uid_list2
            print "*******Estimating Folder", uid, "Tree", tcnt+1, "/", ntrees, "***************"
            #if uid == 341 and tcnt+1 == 1:
            if nt > 1:
                id_ts2 = identify_terrain(t, id_ts1)
                id_t = py3dmodel.construct.make_compound(id_ts2)
            else:
                id_t = id_ts1[0]
                
            tree_cmpd, tree_pts = gen_tree(t, id_t, lasfile_list, tzmin, tzmax, pts_in_grid, pts_ratio)
            
            if tree_cmpd:
                #py3dmodel.utility.visualise([[tree_cmpd], [tree_pts]], ["GREEN", "BLUE"])
                tree_list.append(tree_cmpd)
                tree_pt_list.append(tree_pts)
            else:
                print "***********Tree ", tcnt+1, "cannot be extruded"
                #py3dmodel.utility.visualise([[extruded_bldg],[bldg_pts]], ["WHITE","BLUE"])
                                
            tcnt +=1
        
        if tree_list:
            print "*******Writing to File" + str(uid), "***************"
            #create folder for each grid and name it after the unique id
            grid_folderpath = os.path.join(result_directory, str(uid))
            if not os.path.isdir(grid_folderpath):
                os.mkdir(grid_folderpath)
            tree_filepath = os.path.join(grid_folderpath, res_filename)
            tree_pt_filepath = os.path.join(grid_folderpath, res_pt_filename)
        
            cmpd = py3dmodel.construct.make_compound(tree_list)
            tree_cmpd_list.append(cmpd)
            py3dmodel.utility.write_brep(cmpd, tree_filepath)
            
            pt_cmpd = py3dmodel.construct.make_compound(tree_pt_list)
            py3dmodel.utility.write_brep(pt_cmpd, tree_pt_filepath)
    
    time2 = time.clock()
    total_time = time2-time1
    print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
print "*********************Processing Complete*************************************"
    
if viewer == True:
    py3dmodel.utility.visualise([tree_cmpd_list], ["GREEN"])