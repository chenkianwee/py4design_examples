from py4design import py3dmodel

edge1 = py3dmodel.construct.make_edge((0,0,0),(5,3,0))
edge2 = py3dmodel.construct.make_edge((0,5,0),(5,0,0))


pyptlist = [(2.5,0.5,0), (3,6,0), (2,8,0),(0.5,2,0), (2.5,0.5,0)]
edge3 = py3dmodel.construct.make_bspline_edge(pyptlist)

interptlist = py3dmodel.calculate.intersect_edge_with_edge(edge1, edge3)
circles = []
for interpt in interptlist:
    vert = py3dmodel.construct.make_vertex((interpt[0], interpt[1], interpt[2]))
    circles.append(vert)

print(len(circles))
#create the 2dlist
display2dlist = []
display2dlist.append([edge3])
display2dlist.append([edge1])
display2dlist.append(circles)
colour_list = ["ORANGE", "BLUE", "RED"]

py3dmodel.utility.visualise(display2dlist, colour_list)