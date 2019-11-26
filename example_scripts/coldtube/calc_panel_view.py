import math

from py4design import skyviewfactor
from py4design import py3dmodel

ndir = 1000
xdim = 1.25
ydim = 2.48

#=============================================================================
def gen_dir(ndir):
    unitball = skyviewfactor.tgDirs(ndir)
    dirs = unitball.getDirList()
    xyzs = []
    for dirx in dirs:
        x = dirx.x
        y = dirx.y
        z = dirx.z
        xyz = (x,y,z)
        xyzs.append(xyz)
    return xyzs

def calc_view(mdist, rec, dirs):    
    midpt = py3dmodel.calculate.face_midpt(rec)
    rec = py3dmodel.modify.reverse_face(rec)
    nrml = py3dmodel.calculate.face_normal(rec)
    ref_dir = py3dmodel.modify.reverse_vector(nrml)
    moved_pt = py3dmodel.modify.move_pt(midpt, nrml, mdist)
    temps = []
    hits = []
    hit_edges = []
    non_hits = []
    for dirx in dirs:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(rec, moved_pt, dirx)
        angle = py3dmodel.calculate.angle_bw_2_vecs(ref_dir, dirx)
        rads = math.radians(angle)
        
        if interpt:
            hits.append(dirx)
            edge = py3dmodel.construct.make_edge(moved_pt, interpt)
            hit_edges.append(edge)
            weight = math.cos(rads)
            #temp = 15.0*weight
            temp = 15.0/weight
            temps.append(temp)
        else:
            moved_pt2 = py3dmodel.modify.move_pt(moved_pt, dirx, 1)
            edge = py3dmodel.construct.make_edge(moved_pt, moved_pt2)
            non_hits.append(edge)
            weight = math.sin(rads)
            #temp = 30.0*weight
            temp = 30.0*weight
            temps.append(temp)
            
    weights = cosine_weighting(ref_dir, dirs)
    total_weight = sum(weights)
    
    ndirs = len(dirs)
    avg_temp = sum(temps)/float(ndirs)
    nhits = len(hits)
    view_factor = nhits/float(ndirs)
    print "avg temp", avg_temp, "view_factor", view_factor
    return view_factor, hit_edges, non_hits

def cosine_weighting(ref_dir, dirs):
    weights = []
    for adir in dirs:
        angle = py3dmodel.calculate.angle_bw_2_vecs(ref_dir, adir)
        rad = math.radians(angle)
        weight = math.cos(rad)
        weights.append(weight)
    
    return weights
    
#=============================================================================

rec = py3dmodel.construct.make_rectangle(xdim,ydim)
rec = py3dmodel.modify.rotate(rec, (0,0,0), (1,0,0),90)
rec = py3dmodel.fetch.topo2topotype(rec)

dirs = gen_dir(ndir)
ref_vec = (0,1,0)
ndirs = []

for adir in dirs:
    angle = py3dmodel.calculate.angle_bw_2_vecs(ref_vec, adir)
    if angle < 90.0:
        rad = math.radians(angle)
        weight = math.cos(rad)
        ndirs.append(adir)
        
mdist = 1
vf, hes, nhes = calc_view(mdist, rec, ndirs)
py3dmodel.utility.visualise([[rec], hes, nhes], ["WHITE", "BLUE", "BLACK"])

#for _ in range(12):
#    vf, hes, nhes = calc_view(mdist, rec, dirs)
#    
#    mdist+=0.1