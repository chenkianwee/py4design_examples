from py4design import py3dmodel
  
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]
c1 = py3dmodel.construct.make_polygon_circle((0,0,0), (0,0,1), 10)
c2 = py3dmodel.construct.make_polygon_circle((0,0,15), (0,1,1), 8)

f1_1 = py3dmodel.construct.make_polygon(points1)

f1_pt = py3dmodel.calculate.face_midpt(f1_1)
f1_2 = py3dmodel.modify.scale(f1_1, 0.3,f1_pt)
f1 = py3dmodel.construct.boolean_difference(f1_1,f1_2)
f1 = py3dmodel.fetch.topo_explorer(f1, "face")[0]

f2 = py3dmodel.modify.rotate(f1, f1_pt, (0,0,1), 30)
f2 = py3dmodel.modify.move(f1_pt, [f1_pt[0], f1_pt[1],20], f2)
f2 = py3dmodel.fetch.topo2topotype(f2)
loft = py3dmodel.construct.extrude(f1, (0,0,1), 20)
#loft = py3dmodel.construct.make_loft([f1,f2])
edges = py3dmodel.fetch.topo_explorer(loft, "edge")
face_list = py3dmodel.fetch.topo_explorer(loft, "face")
#face_list.append(f1)
#face_list.append(f2)

tri_list = []
vlist = []
fcnt = 0
for f in face_list:

    if fcnt == 21:
        extrude = py3dmodel.construct.extrude(f,(0,0,1), 20)
        py3dmodel.utility.visualise([[extrude]], ["BLUE"])
    tri_faces = py3dmodel.construct.triangulate_face(f)
    for tf in tri_faces:
        pyptlist = py3dmodel.fetch.points_frm_occface(tf)
        centre_pt = py3dmodel.calculate.points_mean(pyptlist)
        v = py3dmodel.construct.make_vertex(centre_pt)
        vlist.append(v)
    tri_list.extend(tri_faces)
    fcnt+=1
tri_cmpd = py3dmodel.construct.make_compound(tri_list)
edges2 = py3dmodel.fetch.topo_explorer(tri_cmpd, "edge")
shell_list = py3dmodel.construct.sew_faces(tri_list)
print len(shell_list)
shell = shell_list[0]
print py3dmodel.calculate.is_shell_closed(shell)

display_2dlist = []
#display_2dlist.append([loft])
display_2dlist.append(tri_list)
display_2dlist.append(vlist)


colour_list = []
#colour_list.append("BLUE")
colour_list.append("RED")
colour_list.append("BLACK")

py3dmodel.utility.visualise(display_2dlist, colour_list)