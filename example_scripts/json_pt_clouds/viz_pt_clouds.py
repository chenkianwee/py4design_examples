import json
import time
from scipy.spatial import Delaunay

from py4design import py3dmodel

json_filepath = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\smart_sensor_diagram\\data\\json\\SMART_scans-master\\32v_FOffice_10_2_17.json"
dae_filepath = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\smart_sensor_diagram\\3dmodel\\dae\\wall_temp.dae"

def alpha_shape(points, alpha):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    import numpy as np
    import math
            
    coords = np.array(points)
    tri = Delaunay(coords)
    tri_faces = []
    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]
        # Lengths of sides of triangle
        a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
        b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
        c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)
        # Semiperimeter of triangle
        s = (a + b + c)/2.0
        # Area of triangle by Heron's formula
        area = math.sqrt(s*(s-a)*(s-b)*(s-c))
        circum_r = a*b*c/(4.0*area)
        # Here's the radius filter.
        #print circum_r
        if circum_r < 1.0/alpha:
            pt1 = list(coords[ia])
            pt2 = list(coords[ib])
            pt3 = list(coords[ic])
            pt1.append(0)
            pt2.append(0)
            pt3.append(0)
            pyptlist = [pt1, pt2, pt3]
            tri = py3dmodel.construct.make_polygon(pyptlist)
            tri_faces.append(tri)
    
    merged_f = py3dmodel.construct.merge_faces(tri_faces)
    return merged_f[0]

def pts3d22d(pyptlist3d):
    pypt2d_list = []
    for pypt in pyptlist3d:
        x = pypt[0]
        y = pypt[1]
        pypt2d = (x,y)
        pypt2d_list.append(pypt2d)
        
    return pypt2d_list

def pts2d23d(pyptlist2d):
    pypt3d_list = []
    for pypt in pyptlist2d:
        x = pypt[0]
        y = pypt[1]
        pypt3d = (x,y,0)
        pypt3d_list.append(pypt3d)
        
    return pypt3d_list

def pts2temp(pyptlist, pyptlist2, temp_list):
    temp_list2 = []
    for pypt in pyptlist:
        index = pyptlist2.index(pypt)
        temp = temp_list[index]
        temp_list2.append(temp)

    return temp_list2

def check_pt_in_bdry(grid_box, pyptlist):
    pts = []
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(grid_box)
    for pypt in pyptlist:
        x = pypt[0]
        y = pypt[1]
        z = pypt[2]
        
        if xmin <= x <= xmax and ymin <= y <= ymax and zmin <= z <= zmax:
            pts.append(pypt)
    return pts
            
#===========================================================================================================================
time1 = time.clock()
json_file = open(json_filepath, "r")
pt_clouds = json.load(json_file)
rad_list = []
pyptlist = []
pyptlist_flatten = []
for pt in pt_clouds:
    dist = pt["distance"]
    if dist < 5:
        pos = pt["pos"]
        x = pos["x"]*-1
        y = pos["y"]
        z = pos["z"]
        radiant = pt["radiant"]
        rad_list.append(radiant)
        pypt = (x,y,z)
        pypt_flat = (x,y,0)
        pyptlist.append(pypt)
        pyptlist_flatten.append(pypt_flat)


pyptlist_flatten = py3dmodel.modify.rmv_duplicated_pts_by_distance(pyptlist_flatten, distance = 0.1)
pyptlist_flatten = py3dmodel.modify.rmv_duplicated_pts(pyptlist_flatten, roundndigit = 2)
pyptlist2d = pts3d22d(pyptlist_flatten)
concave_face = alpha_shape(pyptlist2d, 1.2)

occpnt_list = py3dmodel.construct.make_occvertex_list(pyptlist)
pt_cmpd = py3dmodel.construct.make_compound(occpnt_list)
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)

height = zmax-zmin
box = py3dmodel.construct.extrude(concave_face, (0,0,1), height)
box = py3dmodel.modify.move([0,0,0], [0,0,zmin], box)
centre_pt = py3dmodel.calculate.get_centre_bbox(box)
sbox = py3dmodel.modify.scale(box, 0.9, centre_pt)
pt_cmpd2 = py3dmodel.construct.boolean_difference(pt_cmpd, sbox)
box = py3dmodel.fetch.topo2topotype(box)
box = py3dmodel.modify.fix_close_solid(box)
bfaces = py3dmodel.fetch.topo_explorer(box, "face")

grid_list = []
for bface in bfaces:
    grids = py3dmodel.construct.grid_face(bface, 0.1,0.1)
    grid_list.extend(grids)

grid_temps = []
grid_boxes = []

verts = py3dmodel.fetch.topo_explorer(pt_cmpd2, "vertex")
occpts = py3dmodel.modify.occvertex_list_2_occpt_list(verts)
pypts = py3dmodel.modify.occpt_list_2_pyptlist(occpts)
    
for grid in grid_list:
    n = py3dmodel.calculate.face_normal(grid)
    n = py3dmodel.modify.reverse_vector(n)
    grid_box = py3dmodel.construct.extrude(grid,n, 0.2) 
    pypts2 = check_pt_in_bdry(grid_box, pypts)
    occpnt_list = py3dmodel.construct.make_occvertex_list(pypts2)
    pt_cmpd2 = py3dmodel.construct.make_compound(occpnt_list)
    pt_cmpd3 = py3dmodel.construct.boolean_common(grid_box, pt_cmpd2)
    
    verts = py3dmodel.fetch.topo_explorer(pt_cmpd3, "vertex")
    occpts = py3dmodel.modify.occvertex_list_2_occpt_list(verts)
    pypts3 = py3dmodel.modify.occpt_list_2_pyptlist(occpts)

    if pypts3:
        temps = pts2temp(pypts3, pyptlist, rad_list)
        avg_temp = sum(temps)/len(temps)
        #print avg_temp, len(temps)
    else:
        avg_temp = 0
        
    grid_temps.append(avg_temp)
    grid_boxes.append(grid_box)

print "done"

py3dmodel.export_collada.write_2_collada_falsecolour(grid_list, grid_temps, "C", dae_filepath, description_str = None, 
                                                     minval = None, maxval=None, other_occface_list = None, other_occedge_list = None)
time2 = time.clock()
tt = (time2-time1)/60
print "TIME TAKEN", tt
py3dmodel.utility.visualise_falsecolour_topo(grid_list, grid_temps)

#py3dmodel.utility.visualise([grid_boxes, [pt_cmpd2], [sbox], edges], ["WHITE", "BLACK", "RED", "BLUE"])
#print pt_clouds
print "done"
