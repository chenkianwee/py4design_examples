from py4design import py3dmodel
from OCC.gp import gp_Pnt
from OCC.BRepPrimAPI import BRepPrimAPI_MakeSphere

# create the shape
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = py3dmodel.construct.make_polygon(points1)
points2 = [(60,50,0),(40,50,0),(50,40,0)]
face2 = py3dmodel.construct.make_polygon(points2)
face3 = py3dmodel.construct.boolean_difference(face1,face2)
face3 = py3dmodel.fetch.topo_explorer(face3, "face")[0]

print len(py3dmodel.fetch.points_frm_occface(face3))
py3dmodel.utility.visualise([[face3]], ["BLUE", "RED"])
'''
extrude = py3dmodel.construct.extrude(face3,(0,0,1),20)
sphere = BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, 0), 0.80).Shape()
cmpd = py3dmodel.construct.make_compound([sphere, extrude])

c1 = py3dmodel.construct.make_polygon_circle((0,0,0),(0,0,1), 0.003, division = 6)
extrude = py3dmodel.construct.extrude(c1, (0,1,1), 0.03)

extrude2 = py3dmodel.construct.extrude(c1, (0,-1,1), 0.01)
extrude3 = py3dmodel.construct.extrude(c1, (-1,-1,1), 0.01)
aShape = py3dmodel.construct.boolean_fuse(extrude, extrude3)
tri_faces = py3dmodel.construct.simple_mesh(aShape)
aShape = py3dmodel.construct.sew_faces(tri_faces)[0]
print py3dmodel.calculate.is_shell_closed(aShape)

tri_faces = py3dmodel.construct.tessellator(c1)

py3dmodel.utility.visualise([tri_faces], ["BLUE", "RED"])
'''
