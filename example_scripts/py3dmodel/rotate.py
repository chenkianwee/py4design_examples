from py4design import py3dmodel

display_2dlist = []
colour_list = []
points1 = [(0,5,0), (5,5,0), (6,0,0),(5,-5,0),(0,-5,0), (-5,-5,0),(-5,5,0)]#clockwise
face1 = py3dmodel.construct.make_polygon(points1)
extrude1 = py3dmodel.construct.extrude(face1, (0,1,1), 10)

f_mid_pt = py3dmodel.calculate.face_midpt(face1)
rot_ext = py3dmodel.modify.rotate(extrude1, f_mid_pt,(0,0,1), 45)
display_2dlist.append([extrude1])
colour_list.append("WHITE")
display_2dlist.append([rot_ext])
colour_list.append("RED")
py3dmodel.utility.visualise(display_2dlist, colour_list)