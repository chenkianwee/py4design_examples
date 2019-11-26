import os 
import time
import shapefile
import numpy as np
import json
from py4design import py2radiance, py3dmodel, shp2citygml, shapeattributes

#===========================================================================================
#INPUTS
#===========================================================================================
main_campus_grid_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_grid\\main_campus_grid.shp"

solar_grid_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_trees\\solar5by5m_filtered.shp"
solar_gridpt_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_trees\\solar5by5m_points.shp"

tree_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_trees\\trees5by5m_merged_filtered.shp"
tpts_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\tree_midpts.json"

bldg_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\bldg.brep"
bpts_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\bpts.json"

terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\terrain.brep"

#create all the relevant folders 
current_path = os.path.dirname(__file__)
base_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart\\base.rad"

#===========================================================================================
#FUNCTIONS
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
                pypt = [pt[0], pt[1], 0]
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
        
def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list 

def avg_daysim_res(res):
    """
    for daysim hourly simulation
    """     
    cumulative_list = []
    #sunuphrs = rad.sunuphrs
    #illum_ress = []
    for sensorpt in res:
        cumulative_sensorpt = sum(sensorpt)
        #avg_illuminance = cumulative_sensorpt
        cumulative_list.append(cumulative_sensorpt)
        #illum_ress.append(avg_illuminance)
        
    return cumulative_list

def write_res2csv(result, sensor_pts, csv_res_filepath):
    nsensors = len(sensor_pts)
    strx = "x,y,z"
    for i in range(8760):
        if i == 8760-1:
            strx = strx + "," + str(i+1) + "\n"
        else:
            strx = strx + "," + str(i+1)
        
    for cnt in range(nsensors):
        hourly = result[cnt] #8760
        sensor_pt = sensor_pts[cnt]
        x = sensor_pt[0]
        y = sensor_pt[1]
        z = sensor_pt[2]
        strx = strx + str(x) + "," + str(y) + "," + str(z)
        hcnt = 0
        for hour in hourly:
            if hcnt == 8760-1:
                strx = strx + "," + str(hour) + "\n"
            else:
                strx = strx + "," + str(hour)
            hcnt+=1
    
    f = open(csv_res_filepath, "w")
    f.write(strx)
    f.close()
    
def flatten_terrains(terrain_list):
    bdry_list = []
    for terrain in terrain_list:
        xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(terrain)
        bdry_face = py3dmodel.construct.make_polygon([[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]])
        bdry_list.append(bdry_face)
    
    return bdry_list

def id_terrain(grid, bdry_list):
    garea = py3dmodel.calculate.face_area(grid)
    cnt_list = []
    cnt = 0
    for bdry in bdry_list:
        common = py3dmodel.construct.boolean_common(grid, bdry)     
        is_null = py3dmodel.fetch.is_compound_null(common)
        if not is_null:
            face_list = py3dmodel.fetch.topo_explorer(common, "face")
            if len(face_list)==1:
                area = py3dmodel.calculate.face_area(face_list[0])
                if area/garea > 0.5:        
                    cnt_list.append(cnt)
            else:
                print "something is weird in id_terrain function"
        cnt+=1
    return cnt_list

def id_terrain2(grid, bdry_list):
    cnt_list = []
    cnt = 0
    for bdry in bdry_list:
        common = py3dmodel.construct.boolean_common(grid, bdry)     
        is_null = py3dmodel.fetch.is_compound_null(common)
        if not is_null:
            face_list = py3dmodel.fetch.topo_explorer(common, "face")
            if len(face_list)==1:
                cnt_list.append(cnt)
            else:
                print "something is weird in id_terrain function"
        cnt+=1
    return cnt_list

def proj_pts_2_terrain(terrain, pyptlist):
    proj_pts = []
    pydir = [0,0,1]
    cnt = 0
    for pypt in pyptlist:
        print cnt
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(terrain, pypt, pydir)
        if interpt:
            interpt2 = [interpt[0], interpt[1], interpt[2]+1]
            proj_pts.append(interpt2)
        cnt+=1
    
    return proj_pts
    
def write_pts2json(pyptlist, json_filepath):
    json_list = []
    for pypt in pyptlist:
        pt_dict = {"point": pypt}
        json_list.append(pt_dict)
    
    f = open(json_filepath, "w")
    json_str = json.dumps(json_list)
    f.write(json_str)
    f.close()
    
def write_indices2json(indices, json_filepath):
    json_list = [{"indices": indices}]
    f = open(json_filepath, "w")
    json_str = json.dumps(json_list)
    f.write(json_str)
    f.close()
    
def read_indices(json_filepath):    
    json_file = open(json_filepath, "r")
    json_data = json.load(json_file)
    indices = json_data[0]["indices"]
    
    return indices 
    
def read_pts(json_filepath):
    json_file = open(json_filepath, "r")
    json_data = json.load(json_file)
    pyptlist = []
    for data in json_data:
        pt = data["point"]
        pyptlist.append(pt)
    
    return pyptlist
    
def get_topo_midpt(topo_list, json_filepath):
    pt_list = []
    for topo in topo_list:
        midpt = py3dmodel.calculate.get_centre_bbox(topo)
        pt_list.append(midpt)
        
    write_pts2json(pt_list, json_filepath)
    
    return pt_list

def get_topo_indices_in_grid(grid, xvalues, yvalues, zvalues=[]):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(grid)
    xvalid = np.logical_and(xvalues >= xmin, xvalues <= xmax)
    yvalid = np.logical_and(yvalues >= ymin, yvalues <= ymax)
    if zvalues != []:
        zvalid = np.logical_and(zvalues >= zmin, zvalues <= zmax)
        pt_indices = np.where(np.logical_and(xvalid, yvalid, zvalid))
    else:
        pt_indices = np.where(np.logical_and(xvalid, yvalid))
    return pt_indices

def zip_pts(pyptlist):
    zipped_pts = zip(*pyptlist)
    xvalues = np.array(zipped_pts[0])
    yvalues = np.array(zipped_pts[1]) 
    zvalues = np.array(zipped_pts[2])
    return xvalues, yvalues, zvalues

def construct_3d_trees(tree_pts, tree_shpatt):
    ntrees = len(tree_pts)
    tree_vols = []
    for cnt in range(ntrees):
        print cnt+1, "/", ntrees
        pt = tree_pts[cnt]
        att = tree_shpatt[cnt].dictionary
        height = att["tree_heigh"]
        tree_x = att["tree_x"]
        tree_y = att["tree_y"]
        rec = py3dmodel.construct.make_rectangle(tree_x, tree_y)
        midpt = py3dmodel.calculate.face_midpt(rec)
        rec = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(midpt, pt, rec))
        box = py3dmodel.construct.extrude(rec, [0,0,1], height)
        tree_vols.append(box)
    
    return tree_vols
    
#===========================================================================================
#MAIN
#===========================================================================================
time1 = time.clock()
display2dlist = []
print  "************* Reading the maingrid *************" 
grid_shpatt = read_sf_poly(main_campus_grid_filepath)
main_grids = extract_shape_from_shapatt(grid_shpatt)[14:]

print  "************* Reading the terrain *************"
terrain_cmpd = py3dmodel.utility.read_brep(terrain_filepath)
terrain_list = py3dmodel.fetch.topo_explorer(terrain_cmpd, "shell")
bdry_faces = flatten_terrains(terrain_list)

print  "************* Reading the bldgs *************"
bldg_cmpd = py3dmodel.utility.read_brep(bldg_filepath)
bldg_list = py3dmodel.fetch.topo_explorer(bldg_cmpd, "solid")
bldg_midpts = read_pts(bpts_filepath)
bxvalues, byvalues, bzvalues = zip_pts(bldg_midpts)

gcnt = 14
for mg in main_grids:
    print "************* Getting all the surrounding Objects*************"
    #get the midpt of the grid and get all the buildings and terrain within a 1km diameter
    midpt = py3dmodel.calculate.face_midpt(mg)
    circle = py3dmodel.construct.make_polygon_circle(midpt, [0,0,1], 500)
    
    #get all the terrains in the circle 
    terrain_cnts = id_terrain2(circle, bdry_faces)
    chosen_terrains = np.take(terrain_list, terrain_cnts)
    terrain_cmpd = py3dmodel.construct.make_compound(chosen_terrains)
    
    print "************* Reading the projected sensor points *************"
    json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\proj_pts4golf_cart\\proj_pts" + str(gcnt) + ".json" 
    proj_pts = read_pts(json_filepath)
    proj_pts = py3dmodel.modify.round_pyptlist(proj_pts, 2)
    sensor_dirs = []
    for _ in range(len(proj_pts)):
        s = [0,0,1]
        sensor_dirs.append(s)
        
    print "************* Reading the surrounding bldg*************"    
    bldg_indices_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\bldg_indices4cart\\bldg_indices" + str(gcnt) + ".json"
    bldg_indices = read_indices(bldg_indices_filepath)
    chosen_bldgs = np.take(bldg_list, bldg_indices)
    bldg_cmpd = py3dmodel.construct.make_compound(chosen_bldgs)
    
    print "************* Reading the 3D tree*************" 
    tree_vol_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\tree_extrude4carts\\tree_extrudes" + str(gcnt) + ".brep"
    tree_vol_cmpd = py3dmodel.utility.read_brep(tree_vol_filepath)
    
#    verts = py3dmodel.construct.make_occvertex_list(proj_pts)
#    py3dmodel.utility.visualise([[terrain_cmpd], [tree_vol_cmpd], chosen_bldgs, verts ], ["GREEN", "WHITE", "WHITE", "BLUE"]) 
        
    terrain_faces =  py3dmodel.fetch.topo_explorer(terrain_cmpd, "face")
    tree_faces = py3dmodel.fetch.topo_explorer(tree_vol_cmpd, "face")
    bldg_faces = py3dmodel.fetch.topo_explorer(bldg_cmpd, "face")
    
    srf_list = terrain_faces + tree_faces + bldg_faces 
    #srf_list = srf_list[0:100]
    
    print "************* Initialising py2radiance*************" 
    data_folder = "F:\\kianwee_work\\solar\\grd_solar" + str(gcnt)
    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)
        
    rad_data_folder = os.path.join(data_folder, 'py2radiance_data')
    rad = py2radiance.Rad(base_filepath, rad_data_folder)
    
    srf_cnt = 0
    for surface in srf_list:
        srfname = "srf" + str(srf_cnt)
        surface = py3dmodel.modify.fix_face(surface)        
        srf_polygon = py3dmodel.fetch.points_frm_occface(surface)
        srfmat = "RAL9010_pur_white_paint"
        py2radiance.RadSurface(srfname,srf_polygon,srfmat,rad)
        
        srf_cnt += 1
        
    rad.create_rad_input_file()
    
    #once the geometries are created initialise daysim
    daysim_dir = os.path.join(data_folder, 'daysim_data')
    rad.initialise_daysim(daysim_dir)

    #a 60min weatherfile is generated
    weatherfilepath = "F:\\kianwee_work\\digital_repository\\epw\\USA_NJ_Trenton-Mercer.County.AP.724095_TMY3.epw"
    rad.execute_epw2wea(weatherfilepath)
    rad.execute_radfiles2daysim()
    
    #create sensor points
    
    rad.set_sensor_points(proj_pts,sensor_dirs)
    rad.create_sensor_input_file()
    rad.write_default_radiance_parameters()#the default settings are the complex scene 1 settings of daysimPS
    rad.execute_gen_dc("w/m2") #w/m2 or lux
    rad.execute_ds_illum()

    #res = rad.eval_ill_per_sensor()
    #print res
    time2 = time.clock()
    total_time = time2-time1
    print "*******Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
print "DONE"

'''
#write_res2csv(res, sensor_pts, csv_res_filepath)
#py3dmodel.utility.visualise_falsecolour_topo(display2dlist, lx_ress, other_occtopo_2dlist = [facade_list], other_colour_list = ['WHITE'] )
'''