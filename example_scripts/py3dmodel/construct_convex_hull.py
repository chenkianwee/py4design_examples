import random
from py4design import py3dmodel

xlist = []
vlist = []
for _ in range(5):
    listp = (random.randint(0,20), random.randint(0,20), 0)
    v = py3dmodel.construct.make_vertex(listp)
    vlist.append(v)
    xlist.append(listp)

face_list = py3dmodel.construct.convex_hull3d(xlist)
area, volume  = py3dmodel.construct.convex_hull3d(xlist, return_area_volume = True)
area_list = []
for f in face_list:
    a = py3dmodel.calculate.face_area(f)
    area_list.append(a)
print sum(area_list)
print area, volume

face = py3dmodel.construct.convex_hull2d(xlist)

#py3dmodel.utility.visualise([vlist, face_list, [face]],["GREEN", "WHITE", "RED"])
py3dmodel.utility.visualise([vlist, [face]],["GREEN", "RED"])