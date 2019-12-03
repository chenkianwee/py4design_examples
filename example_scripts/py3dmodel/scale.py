from py4design import py3dmodel, urbangeom

displaylist = []
points1 = [(0,5,0), (5,5,0), (6,0,0),(5,-5,0),(0,-5,0), (-5,-5,0),(-5,5,0)]#clockwise
face1 = py3dmodel.construct.make_polygon(points1)
extrude1 = py3dmodel.construct.extrude(face1, (0,1,1), 10)

trsfshape = py3dmodel.modify.uniform_scale(extrude1, 1, 2, 2,(0,5,0))
mpt = py3dmodel.calculate.face_midpt(face1)
trsfshape2 = py3dmodel.modify.scale(face1, 2,mpt)

print(py3dmodel.fetch.topo2topotype(trsfshape))
faces = py3dmodel.fetch.topo_explorer(trsfshape, "face")


mesh_face_list = py3dmodel.construct.simple_mesh(trsfshape)

face_list = py3dmodel.fetch.topo_explorer(trsfshape, "face")
sensor_list = []
for face in face_list:
    sensor_surfaces, sensor_pts, sensor_dirs = urbangeom.generate_sensor_surfaces(face,3,3)
    sensor_list.extend(sensor_surfaces)

display2dlist = []
#display2dlist.append(sensor_list)
display2dlist.append([face1])
display2dlist.append([trsfshape2])
py3dmodel.utility.visualise(display2dlist, ["WHITE", 'BLACK'])