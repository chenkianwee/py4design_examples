from py4design import py3dmodel
import random
cylinder_radius = 0.038
cylinder_height = 0.06
thickness = 0.003
slit_width = 0.005

c_edge_list = py3dmodel.construct.circles_frm_pyptlist([[0,0,0]], 1)
wire = py3dmodel.construct.make_wire_frm_edges(c_edge_list)
face = py3dmodel.construct.make_face_frm_wire(wire)
face_midpt = py3dmodel.calculate.face_midpt(face)
face_scaled = py3dmodel.fetch.topo2topotype(py3dmodel.modify.uniform_scale(face, 
                                                                             cylinder_radius, 
                                                                             cylinder_radius, 
                                                                             cylinder_radius, 
                                                                             face_midpt))

face_scaled2 = py3dmodel.fetch.topo2topotype(py3dmodel.modify.uniform_scale(face, 
                                                                             cylinder_radius-thickness, 
                                                                             cylinder_radius-thickness, 
                                                                             cylinder_radius-thickness, 
                                                                             face_midpt))
extrude = py3dmodel.construct.extrude(face_scaled, (0,0,1), cylinder_height)
extrude2 = py3dmodel.construct.extrude(face_scaled2, (0,0,1), cylinder_height-(thickness*2))
ext2_m = py3dmodel.modify.move(face_midpt, (face_midpt[0], face_midpt[1],thickness*-1),extrude2)
diff_shape = py3dmodel.construct.boolean_difference(extrude, extrude2)

#make the slits
box_slit = py3dmodel.construct.make_box(slit_width, 
                                        cylinder_radius*3, 
                                        cylinder_height - (thickness*6))

box_slit_m = py3dmodel.modify.move((0,0,0), (0,0,thickness*3), box_slit)
box_slit_list = []
for rcnt in range(20):
    rot = rcnt*18
    rot_box_split = py3dmodel.modify.rotate(box_slit_m, (0,0,0.005), (0,0,1), rot)
    box_slit_list.append(rot_box_split)
    
slit_cmpd = py3dmodel.construct.make_compound(box_slit_list)
diff_shape1 = py3dmodel.construct.boolean_difference(diff_shape, slit_cmpd)

#mesh for the top
grids = py3dmodel.construct.grid_face(face, 0.5,0.5)
gcmpd = py3dmodel.construct.make_compound(grids)
scaled_cmpd = py3dmodel.fetch.topo2topotype(py3dmodel.modify.uniform_scale(gcmpd, 
                                                                             0.03, 
                                                                             0.03, 
                                                                             0.03, 
                                                                             face_midpt))
grids = py3dmodel.fetch.topo_explorer(scaled_cmpd, "face")
meshed_hole = []
for grid in grids:
    gmid_pt= py3dmodel.calculate.face_midpt(grid)
    gmid_pt = (gmid_pt[0], gmid_pt[1], 0.04)
    random_list = [0.4,0.6,0.8,1.0]
    scale_factor = random.choice(random_list)*0.003
    face_scaled1 = py3dmodel.fetch.topo2topotype(py3dmodel.modify.uniform_scale(face, 
                                                                             scale_factor, 
                                                                             scale_factor, 
                                                                             scale_factor, 
                                                                             face_midpt))
    
    moved_mesh = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move((0,0,0), (gmid_pt), face_scaled1))
    ext1 = py3dmodel.construct.extrude(moved_mesh, (0,0,1), 0.08)
    meshed_hole.append(ext1)
    
meshed_cmpd = py3dmodel.construct.make_compound(meshed_hole)
diff_shape2 = py3dmodel.construct.boolean_difference(diff_shape1, meshed_cmpd)

#put in sbb word
brep_text = py3dmodel.construct.make_brep_text("SBB", thickness*2)
txt_midpt = py3dmodel.calculate.get_centre_bbox(brep_text)
brep_text = py3dmodel.modify.move(txt_midpt, (0,0,0), brep_text)
text_face = py3dmodel.fetch.topo_explorer(brep_text, "face")
txt_list = []
for tf in text_face:
    ex_txt = py3dmodel.construct.extrude(tf, (0,0,1), 0.1)
    txt_list.append(ex_txt)
    
txt_cmpd = py3dmodel.construct.make_compound(txt_list)
diff_shape3 = py3dmodel.construct.boolean_difference(diff_shape2, txt_cmpd)
diff_shape3 = py3dmodel.construct.simple_mesh(diff_shape3)
py3dmodel.export_collada.write_2_collada("C:\\Users\\smrckwe\\Desktop\\vcylinder.dae", occface_list = diff_shape3)
display_2dlist = []
display_2dlist.append(diff_shape3)
#display_2dlist.append(txt_list)
py3dmodel.utility.visualise(display_2dlist, ["BLUE", "WHITE"])