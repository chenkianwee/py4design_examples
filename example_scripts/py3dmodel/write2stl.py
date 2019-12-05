from py4design import py3dmodel

stl_path = "C:\\Users\\chaosadmin\\Desktop\\test2.stl"
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = py3dmodel.construct.make_polygon(points1)
extrude1 = py3dmodel.construct.extrude(face1, (0,0,1), 50)

py3dmodel.utility.write_2_stl(extrude1, stl_path)