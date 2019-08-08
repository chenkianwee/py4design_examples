import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile

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
#specify the terrain directory
terrain_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrains"
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

def make_bdry_face2d(mn_mx_list):
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face
    

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
        
def boolean_x_w_ylist(xface, y_occtopos, mv_down = -10, extrude = 20, common = True):
    #move the grid and extrude it capture the boolean faces
    mv_grid = py3dmodel.modify.move([0,0,0], [0,0,mv_down], xface)
    mv_grid = py3dmodel.fetch.topo2topotype(mv_grid)
    gextrude = py3dmodel.construct.extrude(mv_grid, [0,0,1], extrude)
    
    if common ==True:
        common_list = []
        for i in y_occtopos:
            #py3dmodel.utility.visualise([[gextrude], [i]], ["WHITE", "RED"])
            common = py3dmodel.construct.boolean_common(gextrude, i)
            if not py3dmodel.fetch.is_compound_null(common):
                common_faces = py3dmodel.fetch.topo_explorer(common, "face")
                common_list.extend(common_faces)
        return common_list
    
    else:
        diff_list = []
        for i in y_occtopos:
            #py3dmodel.utility.visualise([[gextrude], [i]], ["WHITE", "RED"])
            diff = py3dmodel.construct.boolean_difference(i, gextrude)
            if not py3dmodel.fetch.is_compound_null(diff):
                diff_faces = py3dmodel.fetch.topo_explorer(diff, "face")
                diff_list.extend(diff_faces)
        return diff_list
    
def triangulate_terrain(terrain_vlist):
    occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(terrain_vlist)
    pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
    tri = py3dmodel.construct.delaunay3d(pyptlist)
    shell = py3dmodel.construct.sew_faces(tri)[0]
    return shell

#===========================================================================================
#READ THE  SHAPEFILE
#===========================================================================================
time1 = time.clock()
display_list = []
print "*******Reading Grid File***************"
grid_shpatt_list = read_sf_poly(grid_shpfile)

#read all the terrains
print "*******Getting All the Terrains***************"
terrain_list = get_all_terrain(terrain_dir)

tzmin = 11
tzmax = 107
trange = tzmax-tzmin
ngrids = len(grid_shpatt_list)
uid_list2 = []
gcnt=0
for g in grid_shpatt_list:
    print "*******Processing Folder", gcnt+1, "of", ngrids, "***************"
    grid = g.shape
    uid = g.get_value("id")
    
    uid_list2.append(uid)
    print "********Folders Processed*************"
    print uid_list2
    
    uid_list = []
    
    if uid in uid_list:
        pass
    
    else:
        #identify the terrain
        id_ts = identify_terrain(grid, terrain_list)
        
        vlist = []
        for id_t in id_ts:
            verts = py3dmodel.fetch.topo_explorer(id_t, "vertex")
            vlist.extend(verts)
        
        shell = triangulate_terrain(vlist)
        common_list = boolean_x_w_ylist(grid, [shell], mv_down = tzmin-10, extrude = trange + 20)
        shell_list = py3dmodel.construct.sew_faces(common_list)
        nshells = len(shell_list)
        print nshells
        
        if nshells == 1:
            shell = shell_list[0]
            display_list.append(shell)
            #py3dmodel.utility.visualise([shell_list, [grid]], ["GREEN", "BLUE"])
            print "*******Writing to File" + str(uid), "***************"
            #create folder for each grid and name it after the unique id
            grid_folderpath = os.path.join(result_directory, str(uid))
            if not os.path.isdir(grid_folderpath):
                os.mkdir(grid_folderpath)
                
            terrain_filepath = os.path.join(grid_folderpath, "terrain.brep")
            py3dmodel.utility.write_brep(shell, terrain_filepath)
            
        else:
            print "SOMETHING IS NOT WORKING RIGHT"
        
    time2 = time.clock()
    total_time = time2-time1
    print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
if viewer == True:
    py3dmodel.utility.visualise([display_list])
