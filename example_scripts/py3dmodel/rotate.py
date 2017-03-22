import pyliburo

display_2dlist = []
colour_list = []
points1 = [(0,5,0), (5,5,0), (6,0,0),(5,-5,0),(0,-5,0), (-5,-5,0),(-5,5,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)
extrude1 = pyliburo.py3dmodel.construct.extrude(face1, (0,1,1), 10)

f_mid_pt = pyliburo.py3dmodel.calculate.face_midpt(face1)
rot_ext = pyliburo.py3dmodel.modify.rotate(extrude1, f_mid_pt,(0,0,1), 45)
display_2dlist.append([extrude1])
colour_list.append("WHITE")
display_2dlist.append([rot_ext])
colour_list.append("RED")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)