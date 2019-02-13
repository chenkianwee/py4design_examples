from py4design import skyviewfactor
from py4design import py3dmodel

ndir = 100
xdim = 1
ydim = 2

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
    moved_pt = py3dmodel.modify.move_pt(midpt, nrml, mdist)
    hits = []
    hit_edges = []
    non_hits = []
    for dirx in dirs:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(rec, moved_pt, dirx)
        if interpt:
            hits.append(dirx)
            edge = py3dmodel.construct.make_edge(moved_pt, interpt)
            hit_edges.append(edge)
        else:
            moved_pt2 = py3dmodel.modify.move_pt(moved_pt, dirx, 1)
            edge = py3dmodel.construct.make_edge(moved_pt, moved_pt2)
            non_hits.append(edge)
            
    
    nhits = len(hits)
    view_factor = nhits/float(ndir)
    print view_factor, mdist
    return view_factor, hit_edges, non_hits
#=============================================================================

rec = py3dmodel.construct.make_rectangle(xdim,ydim)
rec = py3dmodel.modify.rotate(rec, (0,0,0), (1,0,0),90)
rec = py3dmodel.fetch.topo2topotype(rec)

dirs = gen_dir(ndir)

mdist = 0.1
for _ in range(12):
    vf, hes, nhes = calc_view(mdist, rec, dirs)
    py3dmodel.utility.visualise([[rec], hes, nhes], ["WHITE", "BLUE", "BLACK"])
    mdist+=0.1