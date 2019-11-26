import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
grid_shpfile = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_grid\\main_campus_grid.shp"
#specify the directory to store the results which includes
shp_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_buildings\\main_campus_buildings.shp"
#specify if you want to view the result interactively
viewer = True
#===========================================================================================
#CONSTANTS
#===========================================================================================
bldg_footprint_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\buildings_2015_princeton\\buildings_2015_princeton.shp"
bldg_centrept_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\buildings_centrept_2015_princeton\\buildings_centrept_2015_princeton.shp"
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

def make_bdry_face2d(mn_mx_list):
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face
        
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
        
def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('index','N',10)
    cnt=0
    for occface in occface_list:
        wires = py3dmodel.fetch.topo_explorer(occface, "wire")
        nwires = len(wires)
        
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(occface)
            poly_shp_list = []
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if is_anticlockwise2:
                        pyptlist.reverse()
                else: #means its a hole not a face
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                
                pyptlist2d = []
                for pypt in pyptlist:
                    x = pypt[0]
                    y = pypt[1]
                    pypt2d = [x,y]
                    pyptlist2d.append(pypt2d)
                poly_shp_list.append(pyptlist2d)
                
            w.poly(poly_shp_list)
            w.record(cnt)
                    
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(occface)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
            if is_anticlockwise:
                pyptlist.reverse()
            pyptlist2d = []
            for pypt in pyptlist:
                x = pypt[0]
                y = pypt[1]
                pypt2d = [x,y]
                pyptlist2d.append(pypt2d)
        
            w.poly([pyptlist2d])
            w.record(cnt)
        cnt+=1
    w.close()
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

print "*******Preparing to Find Building***************"

ngrids = len(grid_shpatt_list)
bldg_footprint_list = []
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
        #get the footprints in the grid
        bldg_footprints, buid_list = find_bldgs_in_grid(grid, bcentrept_list, bldg_dict)
        bldg_footprint_list.extend(bldg_footprints)
        
    time2 = time.clock()
    total_time = time2-time1
    print "******* Folder" +  str(uid) + " Time Take:", total_time/60, "mins***************"
    gcnt+=1
    
write_poly_shpfile(bldg_footprint_list, shp_filepath)
if viewer == True:
    py3dmodel.utility.visualise([bldg_footprint_list])