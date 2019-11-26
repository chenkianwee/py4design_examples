import json
import datetime
import math
from dateutil.tz import gettz
from dateutil.parser import parse
from datetime import timedelta

from pyproj import Proj
from py4design import py3dmodel

#========================================================================
#filepaths
#========================================================================
location_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\location\\ckw_json\\LocationHistory\\loc_sep.json"
terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\terrain.brep"

#========================================================================
#functions
#========================================================================
def normalise(val_list):
    norm_list = []
    if len(val_list) == 1:
        minx = 0
        maxx = max(val_list)
    else:
        minx = min(val_list)
        maxx = max(val_list)
    rangex = float(maxx - minx)
    for v in val_list:
        norm = (v-minx)/rangex
        norm_list.append(norm)
    return norm_list

def id_terrain(boundary_face, terrain_compound):
    shells = py3dmodel.fetch.topo_explorer(terrain_compound, "shell")
    id_list = []
    for shell in shells:    
        xmin,ymin,zmin, xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(shell)
        terrain_bdry = py3dmodel.construct.make_polygon([[xmin, ymin, 0], [xmax, ymin, 0], [xmax, ymax, 0], [xmin, ymax, 0]])
        common = py3dmodel.construct.boolean_common(boundary_face, terrain_bdry)
        is_null = py3dmodel.fetch.is_compound_null(common)
        if not is_null:
            id_list.append(shell)
    
    return id_list

def proj_pt_onto_terrains(pypt, terrain_list):
    proj_pt = pypt
    for terrain in terrain_list:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(terrain, pypt, (0,0,1))
        if interpt:
            proj_pt = interpt
            break
    
    return proj_pt
    
def construct_path_edges(pyptlist):
    print "***************** Create path geometry for the points*****************" 
    wire = py3dmodel.construct.make_wire(pyptlist)
    edges = py3dmodel.fetch.topo_explorer(wire, "edge")
    return edges

def get_z_from_pts(pyptlist):
    maxz = -10000
    for pypt in pyptlist:
        z = pypt[2]
        if z > maxz:
            maxz = z
    return maxz
    
def calc_normalise_freq_extrude(pyptlist, grids, max_extrude=300):
    print "***************** Calculate the frequency of the points in the grid *****************" 
    grid_freq_list = []
    for g in grids:
        grid_freq_list.append({"shape":g, "frequency":0, "points":[]})
    
    for pypt in pyptlist:
        for g in grid_freq_list:
            in_face = py3dmodel.calculate.point_in_face([pypt[0], pypt[1], 0], g["shape"])
            if in_face:
                freq = g["frequency"]
                new_freq = freq+1
                g["frequency"] = new_freq
                g["points"].append(pypt)
                break
    

    new_gdict_list = []
    all_freqs = []
    for gd in grid_freq_list:
        f = gd["frequency"]
        if f !=0:
            all_freqs.append(f)
            new_gdict_list.append(gd)
        
    print "***************** Normalise the frequency and extrude the grid *****************" 
    print all_freqs
    norm_list = normalise(all_freqs)
    extrude_list = []
    ccnt = 0
    for gd2 in new_gdict_list:
        grid = gd2["shape"]
        ptsingrid = gd2["points"]
        gridz = get_z_from_pts(ptsingrid)
        grid = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move([0,0,0], [0,0,gridz], grid))
        norm_val = norm_list[ccnt]
        gd2["normalise"] = norm_val
        if norm_val !=0:
            extrude = py3dmodel.construct.extrude(grid, [0,0,1], norm_val*max_extrude)
            extrude_list.append(extrude)
        ccnt+=1
    
    return extrude_list
    
#========================================================================
#main script
#========================================================================
print "*****************Reading the files*****************" 
#get all the terrain shells
terrain_cmpd = py3dmodel.utility.read_brep(terrain_filepath)

#set up the projection
p = Proj(proj='utm',zone=18,ellps='GRS80', preserve_units=False)

#read the location file
location_f = open(location_filepath , "r")
json_data = json.load(location_f)[52:200]
print len(json_data)
location_f.close()

timezone = gettz()
start_date = parse('2019-01-01T00:00:00.0Z')
start_date = start_date.replace(tzinfo=timezone)

hourly_list = []
for _ in range(8760):
    hourly_list.append({"locations":[]})
    
#process the location points 
print "***************** Processing location points*****************" 
pyptlist = []
date_list = []
for loc in json_data:
    timestamp = int(loc["timestampMs"])/1000
    date = datetime.datetime.fromtimestamp(timestamp)  # using the local timezone
    date = date.replace(tzinfo=timezone)
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    td = date-start_date
    hour_index = td.total_seconds()/3600
    hour_index = int(math.floor(hour_index))
    
    lon = float(loc["longitudeE7"])/10**7
    lat = float(loc["latitudeE7"])/10**7
    x,y = p(lon, lat)
    pypt = [x,y,0]
    loc["date"] = date
    loc["pypt"] = pypt    
    pyptlist.append(pypt)
    
    hourly_list[hour_index]["locations"].append(loc)

print "***************** Constructing the boundary based on the location points*****************" 
verts = py3dmodel.construct.make_occvertex_list(pyptlist)
cmpd = py3dmodel.construct.make_compound(verts)
xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(cmpd)
print xmax-xmin, ymax-ymin
bdry_face = py3dmodel.construct.make_polygon([[xmin, ymin, 0], [xmax, ymin, 0], [xmax, ymax, 0], [xmin, ymax, 0]])

grids = py3dmodel.construct.grid_face(bdry_face, 50, 50)

print "***************** Id the terrains *****************" 
id_terrain_list = id_terrain(bdry_face, terrain_cmpd)
print len(id_terrain_list)

hcnt = 0
for locd in hourly_list:
    print hcnt, "/8760"
    locs_list = locd["locations"]
    if locs_list:
        proj_pts = []
        print "LOC list", len(locs_list)
        for loc in locs_list:
            print loc
            pypt = loc["pypt"]
            proj_pt = proj_pt_onto_terrains(pypt, id_terrain_list)
            proj_pts.append(proj_pt)
        
        ext_list = calc_normalise_freq_extrude(proj_pts, grids, max_extrude=300)
        verts = py3dmodel.construct.make_occvertex_list(proj_pts)
        proj_pts2 = py3dmodel.modify.rmv_duplicated_pts(proj_pts)
        nproj_pts = len(proj_pts2)
        
        if nproj_pts > 1:
            print "proj list", nproj_pts
            path_edges = construct_path_edges(proj_pts)
            py3dmodel.utility.visualise([path_edges, verts, ext_list], ["RED", "BLUE", "WHITE"])
        else:
            py3dmodel.utility.visualise([verts, ext_list], ["BLUE", "WHITE"])
        
    hcnt+=1
    
'''
edge_cmpd = py3dmodel.construct.make_compound(edges)
edge_brepfilepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\path.brep"
py3dmodel.utility.write_brep(edge_cmpd, edge_brepfilepath)


ext_brepfilepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\ext.brep"
    
extrude_cmpd = py3dmodel.construct.make_compound(extrude_list)
py3dmodel.utility.write_brep(extrude_cmpd, ext_brepfilepath)
    
py3dmodel.utility.visualise([[wire], extrude_list], ["RED", "RED"])


end_date = parse('2019-10-01T00:00:00.0Z')
end_date = end_date.replace(tzinfo=timezone)

'''