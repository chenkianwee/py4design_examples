import math
from py4design import py3dmodel

pts_file = "C:\\Users\\chenkianwee\\Desktop\\sfm_tryouts\\coldtube2\\pts\\coldtube_panel2_8.pts"
dae_filepath = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\dae\\grid.dae"
#===========================================================================
#===========================================================================
    
vertex_list = []
pyptlist = []

print "READING POINT CLOUDS OF ..."
pf = open(pts_file, "r")
lines = pf.readlines()
print "NUMBER OF POINTS:", len(lines)
    
print "ANALYSING POINTS & CONVERTING POINTS TO OCC VERTICES..."
for l in lines:
    l = l.replace("\n","")
    l_list = l.split(",")
    
    x = float(l_list[0])
    y = float(l_list[1])
    z = float(l_list[2])
    #temp = float(l_list[6])
    pypt = (x,y,z)
    
    occ_vertex = py3dmodel.construct.make_vertex(pypt)
    vertex_list.append(occ_vertex)
    pyptlist.append(pypt)          
    
print "COMPUTING THE BOUNDING BOX FOR THE POINTS..."
cmpd = py3dmodel.construct.make_compound(vertex_list)
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(cmpd)
face = py3dmodel.construct.convex_hull2d(pyptlist)
midpt = py3dmodel.calculate.face_midpt(face)
face = py3dmodel.modify.move(midpt, (midpt[0],midpt[1],zmin),face)
face = py3dmodel.fetch.topo_explorer(face, "face")[0]
face = py3dmodel.construct.make_offset(face, -0.2)
grids = py3dmodel.construct.grid_face(face, 0.3,0.3)
py3dmodel.export_collada.write_2_collada(dae_filepath, occface_list = grids)
#py3dmodel.utility.visualise([grids, vertex_list], ["RED", "BLACK"])