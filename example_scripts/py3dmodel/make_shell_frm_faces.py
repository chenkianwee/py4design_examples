from py4design import py3dmodel

display_list = []
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
points2 = [(60,50,0), (50,75,0),(40,50,0),(50,40,0)]#counterclockwise
faces2bsewed = []

face1 = py3dmodel.construct.make_polygon(points1)
extrude1 = py3dmodel.construct.extrude(face1, (0,0,1), 50)
ext1_faces = py3dmodel.fetch.faces_frm_solid(extrude1)[0:2]
ext11_faces = py3dmodel.fetch.faces_frm_solid(extrude1)[5:6]
print(len(ext11_faces))
faces2bsewed.extend(ext1_faces)
#faces2bsewed.extend(ext11_faces)

face2 = py3dmodel.construct.make_polygon(points2)
extrude2 = py3dmodel.construct.extrude(face2, (0,0,1), 80)
ext2_faces = py3dmodel.fetch.faces_frm_solid(extrude2)[2:3]
faces2bsewed.extend(ext2_faces)

shell_list = py3dmodel.construct.sew_faces(faces2bsewed)
print(len(shell_list))

display2dlist = []
display2dlist.append(shell_list)
py3dmodel.utility.visualise(display2dlist, ["WHITE"])