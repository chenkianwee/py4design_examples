import json

from py4design import py3dmodel

def normalise(val_list, minval, maxval):
    norm_list = []
    rangex = maxval-minval
    for v in val_list:
        norm = (v-minval)/float(rangex)
        norm_list.append(norm)
            
    return norm_list

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
    norm_list = normalise(all_freqs, 0, sum(all_freqs))
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
    
    extrude_cmpd = py3dmodel.construct.make_compound(extrude_list)
    return extrude_cmpd

def construct_grids(pyptlist, xdim, ydim):
    if len(pyptlist) == 1:
        grid = py3dmodel.construct.make_rectangle(xdim, ydim)
        grid = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move([0,0,0], pyptlist[0], grid))
        grids = [grid]
    else:
        verts = py3dmodel.construct.make_occvertex_list(pyptlist)
        cmpd = py3dmodel.construct.make_compound(verts)
        xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(cmpd)
        bdry_face = py3dmodel.construct.make_polygon([[xmin, ymin, 0], [xmax, ymin, 0], [xmax, ymax, 0], [xmin, ymax, 0]])
        area = py3dmodel.calculate.face_area(bdry_face)
        if area < xdim*ydim:
            grid = py3dmodel.construct.make_rectangle(xdim, ydim)
            centre_pt = py3dmodel.calculate.points_mean(pyptlist)
            grid = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move([0,0,0], centre_pt, grid))
            grids = [grid]
        else:
            grids = py3dmodel.construct.grid_face(bdry_face, 50, 50)
    return grids


loc_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\location\\ckw_json\\LocationHistory\\weekly\\locations_wk34.json"

json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\travel_extrude4carts\\extrude_meshes_wk34.json"

json_f = open(json_filepath, "r")
json_meshes = json.load(json_f)
json_f.close()
print len(json_meshes)
for mesh in json_meshes:
    att = mesh["attributes"]
    hr_index = att["hour_index"]
    if hr_index == hour_index:
        print mesh
        
    print hr_index

loc_f = open(loc_filepath, "r")
json_data = json.load(loc_f)
print len(json_data)
loc_f.close()
hour_index = 5866
hr_data = json_data[hour_index]
loc_list = hr_data["locations"]
print len(loc_list)
loc_pyptlist = []
for loc in loc_list:
    pypt = loc["pypt"]
    loc_pyptlist.append(pypt)

print loc_pyptlist
unique = py3dmodel.modify.rmv_duplicated_pts(loc_pyptlist)
grids = construct_grids(unique, 50,50)
extruded = calc_normalise_freq_extrude(loc_pyptlist, grids, max_extrude=300)


verts = py3dmodel.construct.make_occvertex_list(unique)



py3dmodel.utility.visualise([verts, grids, [extruded]], ["BLUE", "WHITE", "GREEN"])