from py4design import py3dmodel


pyptlist = [[0,0,0], [0,2,0], [2,2,0], [2,0,0], [0,0,0]]
pyptlist1 = [[0.5,0.5,0], [1,0.5,0], [1,1,0], [0.5,1,0], [0.5,0.5,0]]
pyptlist2 = [[1.2,1.2,0], [1.8,1.2,0], [1.8,1.8,0], [1.2,1.8,0], [1.2,1.2,0]]
pyptlist3 = [[2.5,2.5,0], [3,2.5,0], [3,3,0], [2.5,3,0], [2.5,2.5,0]]

occface = py3dmodel.construct.make_polygon_w_holes(pyptlist, [pyptlist1, pyptlist2, pyptlist3])
print py3dmodel.calculate.face_area(occface)
py3dmodel.utility.visualise([[occface]])