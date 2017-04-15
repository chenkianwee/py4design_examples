import os
import time
import pyliburo
time1 = time.clock()
#construct the bldg to be analysed
pypt_list = [(0,20,0), (20,0,0), (40,0,0),(60,20,0), (60,40,0),(40,60,0),(20,60,0),(0,40,0)]
occface = pyliburo.py3dmodel.construct.make_polygon(pypt_list)


midpt = pyliburo.py3dmodel.calculate.face_midpt(occface)
moved_pt = pyliburo.py3dmodel.modify.move_pt(midpt, (0,0,1),3)
occface2 = pyliburo.py3dmodel.modify.move(midpt,moved_pt,occface)
scaled_occface2 = pyliburo.py3dmodel.modify.uniform_scale(occface2, 1,1,1,moved_pt)

moved_pt2 = pyliburo.py3dmodel.modify.move_pt(midpt, (0,0,1),7)
occface3 = pyliburo.py3dmodel.modify.move(midpt,moved_pt2,occface)
scaled_occface3 = pyliburo.py3dmodel.modify.uniform_scale(occface3, 0.5,0.5,1,moved_pt2)

loft = pyliburo.py3dmodel.construct.make_loft([occface,scaled_occface2, scaled_occface3])
occface_list = pyliburo.py3dmodel.fetch.geom_explorer(loft, "face")
occface_list.append(occface)
occface_list.append(scaled_occface3)
shell_list = pyliburo.py3dmodel.construct.make_shell_frm_faces(occface_list)
fixed_occshell = pyliburo.py3dmodel.modify.fix_shell_orientation(shell_list[0])
occsolid = pyliburo.py3dmodel.construct.make_solid(fixed_occshell)
occsolid = pyliburo.py3dmodel.modify.fix_close_solid(occsolid)
facade_list, roof_list, footprint_list = pyliburo.gml3dmodel.identify_building_surfaces(occsolid)

win_occface_list = []
wall_occface_list = []
shade_occface_list = []
for facade in facade_list:
    fmidpt = pyliburo.py3dmodel.calculate.face_midpt(facade)
    fnrml = pyliburo.py3dmodel.calculate.face_normal(facade)
    fnrml = (round(fnrml[0],2), round(fnrml[1],2), round(fnrml[2],2))
    win_occface = pyliburo.py3dmodel.fetch.shape2shapetype(pyliburo.py3dmodel.modify.uniform_scale(facade, 0.1,0.1,0.1, fmidpt))
    
    wall_occface = pyliburo.py3dmodel.construct.boolean_difference(facade,win_occface)
    tri_wall_occface_list = pyliburo.py3dmodel.construct.simple_mesh(wall_occface)
    new_tri_wall_occface_list = []
    for tri_face in tri_wall_occface_list:
        tri_nrml = pyliburo.py3dmodel.calculate.face_normal(tri_face)
        tri_nrml = (round(tri_nrml[0],2), round(tri_nrml[1],2), round(tri_nrml[2],2))
        if tri_nrml != fnrml:
            reversed_face = pyliburo.py3dmodel.modify.reverse_face(tri_face)
            new_tri_wall_occface_list.append(reversed_face)
        else:
            new_tri_wall_occface_list.append(tri_face)
            
    #create shading for the windows
    shade_extrude = pyliburo.py3dmodel.construct.extrude(win_occface,fnrml,1)
    vert_list, shade_list, down_list = pyliburo.gml3dmodel.identify_building_surfaces(shade_extrude)
    shade_occface_list.extend(shade_list)
    win_occface_list.append(win_occface)
    wall_occface_list.extend(new_tri_wall_occface_list)
    
'''
sky_occface_list = []
roof_occface_list = []

for roof in roof_list:
    fmidpt = pyliburo.py3dmodel.calculate.face_midpt(roof)
    fnrml = pyliburo.py3dmodel.calculate.face_normal(roof)
    fnrml = (round(fnrml[0],2), round(fnrml[1],2), round(fnrml[2],2))
    sky_occface = pyliburo.py3dmodel.fetch.shape2shapetype(pyliburo.py3dmodel.modify.uniform_scale(roof, 0.3,0.3,0.3, fmidpt))
    roof_occface = pyliburo.py3dmodel.construct.boolean_difference(roof,sky_occface)
    tri_roof_occface_list = pyliburo.py3dmodel.construct.simple_mesh(roof_occface)
    new_tri_roof_occface_list = []
    for tri_face in tri_roof_occface_list:
        tri_nrml = pyliburo.py3dmodel.calculate.face_normal(tri_face)
        tri_nrml = (round(tri_nrml[0],2), round(tri_nrml[1],2), round(tri_nrml[2],2))
        if tri_nrml != fnrml:
            reversed_face = pyliburo.py3dmodel.modify.reverse_face(tri_face)
            new_tri_roof_occface_list.append(reversed_face)
        else:
            new_tri_roof_occface_list.append(tri_face)
            
    sky_occface_list.append(sky_occface)
    roof_occface_list.extend(new_tri_roof_occface_list)
'''
#construct the surrounding bldgs
pypt_list2 = [(80,20,0), (140,20,0), (140,40,0),(80,40,0)]
occface = pyliburo.py3dmodel.construct.make_polygon(pypt_list2)
extrude = pyliburo.py3dmodel.construct.extrude(occface, (0,0,1), 30)
surround_occface_list = pyliburo.py3dmodel.fetch.geom_explorer(extrude, "face")

time2 = time.clock()
print "CONSTRUCTED MODEL", (time2-time1)/60.0

print "CALCULATING ETTV..."

#calculate ettv 
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
shp_attribs_list = []
for wall in wall_occface_list:
    shp_attribs = pyliburo.buildingformeval.create_opaque_srf_shape_attribute(wall,1,"wall" )
    shp_attribs_list.append(shp_attribs)
    
for roof in roof_list:
    shp_attribs = pyliburo.buildingformeval.create_opaque_srf_shape_attribute(roof,0.5,"roof" )
    shp_attribs_list.append(shp_attribs)

for window in win_occface_list:
    shp_attribs = pyliburo.buildingformeval.create_glazing_shape_attribute(window,2.82,0.81,"window")
    shp_attribs_list.append(shp_attribs)

for shade in shade_occface_list:
    shp_attribs = pyliburo.buildingformeval.create_shading_srf_shape_attribute(shade, "shade")
    shp_attribs_list.append(shp_attribs)

for surround in surround_occface_list:
    shp_attribs = pyliburo.buildingformeval.create_shading_srf_shape_attribute(surround, "surrounding")
    #shp_attribs_list.append(shp_attribs)

for footprint in footprint_list:
    shp_attribs = pyliburo.buildingformeval.create_shading_srf_shape_attribute(footprint, "footprint")
    shp_attribs_list.append(shp_attribs)
    
result_dictionary = pyliburo.buildingformeval.calc_ettv(shp_attribs_list,weatherfilepath)
print result_dictionary
time3 = time.clock()
print "CALCULATED ETTV", (time3-time2)/60.0

time4 = time.clock()
#calculate cooling energy 
facade_area = result_dictionary["facade_area"]
roof_area = result_dictionary["roof_area"]
floor_area = pyliburo.py3dmodel.calculate.face_area(occface)
ettv = result_dictionary["ettv"]
rttv = result_dictionary["rttv"]
system_dict_list = pyliburo.buildingformeval.calc_cooling_energy_consumption(facade_area, roof_area, floor_area, ettv, rttv)
chosen_system = pyliburo.buildingformeval.choose_efficient_cooling_system(system_dict_list)
print chosen_system
time5 = time.clock()
print "CALCULATED COOLING ENERGY ", (time5-time4)/60.0

display_2dlist = []
colour_list = []
display_2dlist.append(wall_occface_list)
display_2dlist.append(win_occface_list)
display_2dlist.append(roof_list)
display_2dlist.append(footprint_list)
display_2dlist.append([extrude])
display_2dlist.append(shade_occface_list)

colour_list.append("WHITE")
colour_list.append("GREEN")
colour_list.append("RED")
colour_list.append("YELLOW")
colour_list.append("BLUE")
colour_list.append("BLACK")
colour_list.append("BLACK")
pyliburo.py3dmodel.construct.visualise(display_2dlist,colour_list)