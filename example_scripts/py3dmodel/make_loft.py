from py4design import py3dmodel
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
points2 = [(60,50,10),(40,50,10),(50,40,10)]
face1 = py3dmodel.construct.make_polygon(points1)
face2 = py3dmodel.construct.make_polygon(points2)
moved_face_list = []
'''
flr2flr = 3
for cnt in range(3):
    orig_pt = py3dmodel.calculate.face_midpt(face1)
    loc_pt = py3dmodel.modify.move_pt(orig_pt, (0,0,1), cnt*flr2flr)
    moved_face = py3dmodel.modify.move(orig_pt, loc_pt, face1)
    moved_face_list.append(moved_face)
'''
face_list = [face1, face2]
loft = py3dmodel.construct.make_loft(face_list)
print py3dmodel.fetch.get_topotype(loft)
print len(py3dmodel.fetch.topo_explorer(loft, "face"))
display_2dlist = []
display_2dlist.append([loft])
colour_list = []
colour_list.append("WHITE")
py3dmodel.utility.visualise(display_2dlist, colour_list)