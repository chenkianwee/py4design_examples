import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile
from laspy.file import File
import numpy as np

#===========================================================================================
#INPUTS
#===========================================================================================
tree_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_bdry2\\bdry_grid_10by10.shp"
terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrain.brep"
grid_size = 100 #m2 the area of a grid
#specify the pt cloud directory
pt_cloud_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las"
pt_resolution = 5 #pts/m2

#specify the directory to store the results which includes
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d"

#specify if you want to view the result interactively
viewer = False
#===========================================================================================
#THE RESULT FILES
#===========================================================================================
tree_brep_filepath = os.path.join(result_directory, "brep", "tree.brep")
tree_brep_filepath2 = os.path.join(result_directory, "brep", "tree_hull.brep")
#===========================================================================================
#FUNCTION
#===========================================================================================
def read_sf(sf_filepath):
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

#===========================================================================================
#READ THE SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading the shpfile***************"
shpatt_list = read_sf(tree_shp_file)
#===========================================================================================
#READ TERRAIN
#===========================================================================================
terrain = py3dmodel.utility.read_brep(terrain_filepath)
terrain_shell = py3dmodel.fetch.topo2topotype(terrain)
txmin, tymin, tzmin, txmax, tymax, tzmax = py3dmodel.calculate.get_bounding_box(terrain_shell)
bdry_face_terrain = make_bdry_face2d([txmin, tymin, tzmin, txmax, tymax, tzmax])
#===========================================================================================
#READ THE PT CLOUDS & IDENTIFY WHICH TO USE 
#===========================================================================================
print "*******Reading the point clouds***************"
lasfile_list = []
las_bdry_list = []
list_dir = os.listdir(pt_cloud_dir)
for dirx in list_dir:
    las_folder = os.path.join(pt_cloud_dir, dirx)
    folder_dirs = os.listdir(las_folder)
    lasfilename = find_las_file(folder_dirs)
    las_filepath = os.path.join(pt_cloud_dir, dirx, lasfilename)
    las_bdry, lasfile = get_las_file_bdry(las_filepath)
    bdry_face_pts = make_bdry_face2d(las_bdry)
    intersect = py3dmodel.construct.boolean_common(bdry_face_terrain, bdry_face_pts)
    int_face_list = py3dmodel.fetch.topo_explorer(intersect, "face")
    if int_face_list:
        #py3dmodel.utility.visualise([[bdry_face_bldg],[bdry_face_pts], int_face_list], ["WHITE", "RED", "BLUE"])
        las_bdry_list.append(las_bdry)
        lasfile_list.append(lasfile)
        
#===========================================================================================
#EXTRUDE & PLACE THE BUILDING
#==========================================================================================
print "*******Extrude the vegetation***************"
npts = grid_size * pt_resolution
veg_list = []
veg_pt_list = []
t_shp = len(shpatt_list)
scnt = 0
for shpatt in shpatt_list:
    grid = shpatt.shape
    area = py3dmodel.calculate.face_area(grid)
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(grid)
    print scnt+1, "/", t_shp
    for las in lasfile_list:
        pyptlist = calc_pt_in_bdry2d(las,[xmin, ymin, zmin, xmax, ymax, zmax])
        #MOVE THE FOOTPRINT TO THE LOWEST POINT
        grid_moved, elev, lowest_grid, highest_elev = find_terrain(grid, terrain_shell, tzmin, tzmax)
        if grid_moved !=None:
            #FILTER AWAY THE BARE EARTH AND CALC THE BOUNDING BOX
            f_pyptlist = filter_pyptlist_z(pyptlist, highest_elev)
            if f_pyptlist:
                vlist = py3dmodel.construct.make_occvertex_list(f_pyptlist)
                
                cmpd = py3dmodel.construct.make_compound(vlist)
                if area < grid_size:
                    g_extrude = py3dmodel.construct.extrude(lowest_grid, [0,0,1], (tzmax-tzmin)+10)
                    common = py3dmodel.construct.boolean_common(g_extrude, cmpd)
                else:
                    common = cmpd
                if not py3dmodel.fetch.is_compound_null(common):
                    xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = py3dmodel.calculate.get_bounding_box(common)
                    if zmax1-elev >= 3:
                        if len(f_pyptlist) > npts*0.3:
                            vlist2 = py3dmodel.fetch.topo_explorer(common, "vertex")
                            veg_pt_list.extend(vlist2)
                            t_height = zmax1-elev
                            tx = xmax1-xmin1
                            ty = ymax1-ymin1
                            #DRAW THE STICK
                            trunk_height = 0.6*t_height
                            g_midpt = py3dmodel.calculate.face_midpt(grid)
                            g_midpt = [g_midpt[0], g_midpt[1], elev]
                            m_midpt = py3dmodel.modify.move_pt(g_midpt, [0,0,1], trunk_height)
                            e = py3dmodel.construct.make_edge(g_midpt, m_midpt)
                            #DRAW THE CANOPY
                            cx = int(tx/2)
                            cy = int(ty/2)
                            tree_list = [e]
                            if cx !=0:
                                c1 = py3dmodel.construct.make_polygon_circle(m_midpt, [0,1,0], cx, division = 3)
                                c1 = py3dmodel.modify.uniform_scale(c1, 1, 1, (0.4*t_height)/(cx*2), m_midpt)
                                tree_list.append(c1)
                            
                            if cy !=0:
                                c2 = py3dmodel.construct.make_polygon_circle(m_midpt, [1,0,0], cy, division = 3)
                                c2 = py3dmodel.modify.uniform_scale(c2, 1, 1, (0.4*t_height)/(cy*2), m_midpt)
                                tree_list.append(c2)
                                
                            tree_cmpd = py3dmodel.construct.make_compound(tree_list)
                            #py3dmodel.utility.visualise([[tree_cmpd]], ["BLACK"])
                            veg_list.append(tree_cmpd)
    scnt+=1

cmpd = py3dmodel.construct.make_compound(veg_list)
pt_cmpd = py3dmodel.construct.make_compound(veg_pt_list)
py3dmodel.utility.write_brep(pt_cmpd, tree_brep_filepath)
py3dmodel.utility.write_brep(cmpd, tree_brep_filepath2)
time2 = time.clock()
total_time = time2-time1
print "*******Total Time Take:", total_time/60, "mins***************"

if viewer == True:
    py3dmodel.utility.visualise([[pt_cmpd], [terrain_shell]], ["GREEN", "WHITE"])