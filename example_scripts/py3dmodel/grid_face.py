from py4design import py3dmodel

points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = py3dmodel.construct.make_polygon(points1)
grids = py3dmodel.construct.grid_face(face1, 10,10)
flist = py3dmodel.modify.sort_face_by_xy(grids)

py3dmodel.utility.visualise_falsecolour_topo(flist, range(len(flist)))    
#py3dmodel.utility.visualise([grids], ["RED"])