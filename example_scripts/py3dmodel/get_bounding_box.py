from py4design import py3dmodel

pypt1 = [0,0,0]
pypt2 = [5,5,0]
occedge = py3dmodel.construct.make_edge(pypt1, pypt2)
bbox = py3dmodel.calculate.get_bounding_box(occedge)
print(bbox)