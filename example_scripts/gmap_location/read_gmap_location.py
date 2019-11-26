import json
import datetime
from dateutil.tz import gettz
from dateutil.parser import parse

from pyproj import Proj
from py4design import py3dmodel
#========================================================================
#filepaths
#========================================================================
location_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\location\\ckw_json\\LocationHistory\\loc2019jan2sep.json"
terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\terrain.brep"
#========================================================================
#functions
#========================================================================
def normalise(val_list):
    norm_list = []
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
timezone = gettz()
json_data = json.load(location_f)["locations"]
print len(json_data)
location_f.close()

#specify the date range
start = parse('2019-01-01T00:00:00.0Z')
start = start.replace(tzinfo=timezone)
end =  parse('2019-09-30T23:00:00.0Z')
end = end.replace(tzinfo=timezone)

#process the location points 
print "***************** Processing location points*****************" 
pyptlist = []
new_json_data = []
for loc in json_data:
    timestamp = int(loc["timestampMs"])/1000
    date = datetime.datetime.fromtimestamp(timestamp)  # using the local timezone
    date = date.replace(tzinfo=timezone)
    if start <= date <= end:   
        new_json_data.append(loc)
        lon = float(loc["longitudeE7"])/10**7
        lat = float(loc["latitudeE7"])/10**7
        x,y = p(lon, lat)
        if "altitude" not in loc.keys():
            z = 0
        else:
            z = 0
            
        pypt = [x,y,z]
        
        pyptlist.append(pypt)
        date_str = date.strftime("%Y-%m-%d %H:%M:%S.%f")

print "***************** Constructing the boundary based on the location points*****************" 
verts = py3dmodel.construct.make_occvertex_list(pyptlist)
cmpd = py3dmodel.construct.make_compound(verts)
xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(cmpd)
bdry_face = py3dmodel.construct.make_polygon([[xmin, ymin, 0], [xmax, ymin, 0], [xmax, ymax, 0], [xmin, ymax, 0]])
grids = py3dmodel.construct.grid_face(bdry_face, 50, 50)

print "***************** Id the terrains *****************" 
id_terrain_list = id_terrain(bdry_face, terrain_cmpd)
print len(id_terrain_list)

print "***************** Project the points onto the terrain *****************" 
npts = len(pyptlist)
proj_pts = []
pt_cnt = 0
for pypt in pyptlist:
    print pt_cnt, "/", npts
    proj_pt = proj_pt_onto_terrains(pypt, id_terrain_list)
    proj_pts.append(proj_pt)
    pt_cnt +=1

print "***************** Create path geometry for the points*****************" 
edge_brepfilepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\path.brep"
wire = py3dmodel.construct.make_wire(proj_pts)
edges = py3dmodel.fetch.topo_explorer(wire, "edge")
edge_cmpd = py3dmodel.construct.make_compound(edges)
py3dmodel.utility.write_brep(edge_cmpd, edge_brepfilepath)
    
print "***************** Calculate the frequency of the points in the grid *****************" 
freq_list = []
for g in grids:
    freq_list.append(0)

for pypt in pyptlist:
    acnt = 0
    for g in grids:
        in_face = py3dmodel.calculate.point_in_face([pypt[0], pypt[1], 0], g)
        if in_face:
            freq = freq_list[acnt]
            new_freq = freq+1
            freq_list[acnt] = new_freq
            break
        acnt+=1

new_glist = []
new_gdict_list = []
newflist = []
bcnt = 0
for f in freq_list:
    if f !=0:
        new_g = grids[bcnt]
        gdict = {"shape":new_g, "frequency": f}
        new_gdict_list.append(gdict)
        new_glist.append(new_g)
        newflist.append(f)
    bcnt+=1
    
print "***************** Normalise the frequency and extrude the grid *****************" 
ext_brepfilepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\ext.brep"
norm_list = normalise(newflist)
extrude_list = []
ccnt = 0
for gd in new_gdict_list:
    grid = gd["shape"]
    grid_midpt = py3dmodel.calculate.face_midpt(grid)
    proj_gpt = proj_pt_onto_terrains(grid_midpt, id_terrain_list)
    
    gridz = proj_gpt[2]
    grid = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move([0,0,0], [0,0,gridz], grid))
    norm_val = norm_list[ccnt]
    gd["normalise"] = norm_val
    if norm_val !=0:
#        moved_pt = py3dmodel.modify.move_pt(proj_gpt, [0,0,1], norm_val*300)
        extrude = py3dmodel.construct.extrude(grid, [0,0,1], norm_val*300)
        extrude_list.append(extrude)
        
#    ext_edge = py3dmodel.construct.make_edge(proj_gpt, moved_pt)
    ccnt+=1

extrude_cmpd = py3dmodel.construct.make_compound(extrude_list)
py3dmodel.utility.write_brep(extrude_cmpd, ext_brepfilepath)
    
py3dmodel.utility.visualise([[wire], extrude_list], ["RED", "RED"])
