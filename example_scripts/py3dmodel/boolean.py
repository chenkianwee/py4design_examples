from py4design import py3dmodel, urbangeom

points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
points2 = [(60,50,0), (50,75,0),(40,50,0),(50,40,0)]#counterclockwise
points3 = [(75,100,0), (100,100,0),(100,150,0),(75,150,0)]
face1 = py3dmodel.construct.make_polygon(points1)
face2 = py3dmodel.construct.make_polygon(points2)

pypt1 = (0,0,0)
pypt2 = (100,100,0)
edge = py3dmodel.construct.make_edge(pypt1, pypt2)

#res = pyliburo.py3dmodel.construct.boolean_common(face1,face2)
res = py3dmodel.construct.boolean_difference(face1,face2)

face = py3dmodel.fetch.topo_explorer(res, "face")[0]
print py3dmodel.fetch.topo_explorer(face, "wire")
sensor_surfaces, sensor_pts, sensor_dirs = urbangeom.generate_sensor_surfaces(face, 10,10)

display2dlist = []
colour_list = []
display2dlist.append(sensor_surfaces)
colour_list.append("WHITE")
#display2dlist.append([face2])
#colour_list.append("WHITE")
py3dmodel.utility.visualise(display2dlist, colour_list)