import math

from py4design import skyviewfactor
from py4design import py3dmodel
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

def calc_view(mdist, rec, dirs, ptemp, otemp):    
    midpt = py3dmodel.calculate.face_midpt(rec)
    rec = py3dmodel.modify.reverse_face(rec)
    nrml = py3dmodel.calculate.face_normal(rec)
    # ref_dir = py3dmodel.modify.reverse_vector(nrml)
    moved_pt = py3dmodel.modify.move_pt(midpt, nrml, mdist)
    temps = []
    hits = []
    hit_edges = []
    non_hits = []
    for dirx in dirs:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(rec, moved_pt, dirx)
        # angle = py3dmodel.calculate.angle_bw_2_vecs(ref_dir, dirx)
        # rads = math.radians(angle)
        
        if interpt:
            hits.append(dirx)
            edge = py3dmodel.construct.make_edge(moved_pt, interpt)
            hit_edges.append(edge)
            # weight = math.cos(rads)
            #temp = 15.0*weight
            temp = ptemp
            temps.append(temp)
        else:
            moved_pt2 = py3dmodel.modify.move_pt(moved_pt, dirx, 1)
            edge = py3dmodel.construct.make_edge(moved_pt, moved_pt2)
            non_hits.append(edge)
            # weight = math.sin(rads)
            #temp = 30.0*weight
            temp = otemp
            temps.append(temp)
            
    # weights = cosine_weighting(ref_dir, dirs)
    # total_weight = sum(weights)
    
    ndirs = len(dirs)
    avg_temp = sum(temps)/float(ndirs)
    nhits = len(hits)
    view_factor = nhits/float(ndirs)
    return avg_temp, view_factor, hit_edges, non_hits

def cosine_weighting(ref_dir, dirs):
    weights = []
    for adir in dirs:
        angle = py3dmodel.calculate.angle_bw_2_vecs(ref_dir, adir)
        rad = math.radians(angle)
        weight = math.cos(rad)
        weights.append(weight)
    
    return weights
    
def gen_angle_dir(ndir, angle, ref_dir):
    dirs = gen_dir(ndir)
    ndirs = []
    non_dirs = []
    angle_half = angle/2
    #only half of the hemisphere
    for adir in dirs:
        angle = py3dmodel.calculate.angle_bw_2_vecs(ref_dir, adir)
        if angle < angle_half:
            ndirs.append(adir)
        else:
            non_dirs.append(adir)
    return ndirs, non_dirs

def dir2edges(dirs):
    edges = []
    for adir in dirs:
        edge = py3dmodel.construct.make_edge([0,0,0], adir)
        edges.append(edge)
    return edges
#============================================================================
#main script
#============================================================================
if __name__ == '__main__':
    ndir = 2000
    xdim = 1.25
    ydim = 2.48
    otemp = 30
    
    ref_dir = (0,1,0)
    all_dirs = gen_dir(ndir)
    angle_dirs, non_dirs = gen_angle_dir(ndir, 180, (0,1,0))
    
    weights = cosine_weighting(ref_dir, angle_dirs)
    
    angle_edges = dir2edges(angle_dirs)
    py3dmodel.utility.visualise_falsecolour_topo(angle_edges, weights)
    #non_edges = dir2edges(non_dirs)
    
    # py3dmodel.utility.visualise([angle_edges, non_edges], ["RED", "BLUE" ])