import pyliburo

points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
points2 = [(60,50,0), (50,75,0),(40,50,0),(50,40,0)]#counterclockwise
points3 = [(75,100,0), (100,100,0),(100,150,0),(75,150,0)]
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)
face2 = pyliburo.py3dmodel.construct.make_polygon(points2)

pypt1 = (0,0,0)
pypt2 = (100,100,0)
edge = pyliburo.py3dmodel.construct.make_edge(pypt1, pypt2)

res = pyliburo.py3dmodel.construct.boolean_common(face1,face2)
res = pyliburo.py3dmodel.construct.boolean_difference(face1,face2)
face = pyliburo.py3dmodel.fetch.geom_explorer(res, "face")[0]
sensor_surfaces, sensor_pts, sensor_dirs = pyliburo.gml3dmodel.generate_sensor_surfaces(face, 10,10)

display2dlist = []
colour_list = []
display2dlist.append(sensor_surfaces)
colour_list.append("WHITE")
#display2dlist.append([face2])
#colour_list.append("WHITE")
pyliburo.py3dmodel.construct.visualise(display2dlist, colour_list, backend = "wx")