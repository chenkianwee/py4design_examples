from py4design import py3dmodel
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
points2 = [(60,50,50),(40,50,50),(50,40,50)]
points3 = [(60,50,80),(40,50,80),(50,40,80)]
points4 = [(60,50,100),(40,50,100),(50,40,100)]
face1 = py3dmodel.construct.make_polygon(points1)
face1 = py3dmodel.construct.make_polygon_circle((40,50,0), (0,0,1), 25)
face2 = py3dmodel.construct.make_polygon(points2)
face3 = py3dmodel.construct.make_polygon(points3)
face4 = py3dmodel.construct.make_polygon(points4)
moved_face_list = []
'''
flr2flr = 3
for cnt in range(3):
    orig_pt = py3dmodel.calculate.face_midpt(face1)
    loc_pt = py3dmodel.modify.move_pt(orig_pt, (0,0,1), cnt*flr2flr)
    moved_face = py3dmodel.modify.move(orig_pt, loc_pt, face1)
    moved_face_list.append(moved_face)

face_list = [face1, face2]
loft = py3dmodel.construct.make_loft(face_list)
print py3dmodel.fetch.get_topotype(loft)
print py3dmodel.fetch.get_topotype("shell")
face_list2 = py3dmodel.fetch.topo_explorer(loft, "face")
print len(face_list2)
grids = py3dmodel.construct.grid_face(face_list2[9],10,10)
'''


face_list = [face1, face2, face3, face4]
loft = py3dmodel.construct.make_loft(face_list)

display_2dlist = []
display_2dlist.append([face2])
display_2dlist.append([face1])
display_2dlist.append([loft])

colour_list = []
colour_list.append("WHITE")
colour_list.append("RED")
colour_list.append("BLUE")

#display_2dlist.append(face_list2)
#colour_list.append("RED")
py3dmodel.utility.visualise(display_2dlist, colour_list)