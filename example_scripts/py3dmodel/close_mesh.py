from py4design import py3dmodel
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise

#TODO HAVE TO FIX THE SCRIPT
stl_filepath = "C:\\Users\\smrckwe\\Desktop\\test.stl"
face1 = py3dmodel.construct.make_polygon(points1)
extrude1 = py3dmodel.construct.extrude(face1, (0,0,1), 5)

tri_faces = py3dmodel.construct.simple_mesh(extrude1)
#delete one face of the mesh so that it is open
del tri_faces[10]
shell_list = py3dmodel.construct.sew_faces(tri_faces)
is_closed = py3dmodel.calculate.is_shell_closed(shell_list[0])
hole_faces = py3dmodel.construct.merge_faces(tri_faces)
py3dmodel.utility.visualise([shell_list], ["RED"])

tri_faces.extend(hole_faces)
shell_list = py3dmodel.construct.sew_faces(tri_faces)
solid = py3dmodel.construct.make_solid(shell_list[0])
solid = py3dmodel.modify.fix_close_solid(solid)
py3dmodel.utility.visualise([[solid]], ["RED"])
py3dmodel.utility.write_2_stl2(solid,stl_filepath)

faces = py3dmodel.fetch.topo_explorer(solid, "face")
#n = py3dmodel.calculate.face_normal_as_edges(faces, normal_magnitude = 5)
#for f in faces:
#    print py3dmodel.calculate.face_normal(f)
#closed = py3dmodel.calculate.is_shell_closed(shell_list[0])
#
#print closed
#py3dmodel.utility.visualise([tri_faces2, hole_faces, n], ["BLUE", "RED", "BLACK"])

