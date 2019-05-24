import os
import time
import math
from py4design import py3dmodel, buildingformeval
#==============================================================================
time1 = time.clock()
#make the floor plate
pyptlist = [[0,10,0], [0,25,0], [-25,25,0], [-25,0,0], [-10,0,0], [-10,10,0]]
floor_plate = py3dmodel.construct.make_polygon(pyptlist)
extrude = py3dmodel.construct.extrude(floor_plate, [0,0,1],4)
face_list = py3dmodel.fetch.topo_explorer(extrude, "face")

#get the external facing walls
shade_occface_list = []
roof_occface_list = []
ext_list = []
for f in face_list:
    n = py3dmodel.calculate.face_normal(f)
    if n == (0.0, 1.0, 0.0) or n == (-1.0, 0.0, 0.0):
        ext_list.append(f)
        
    elif n == (0.0, 0.0, 1.0):
        roof_occface_list.append(f)
    else:
        shade_occface_list.append(f)
        
#construct the windows
wwr = 0.4
cut_wall_list = []
win_list = []
shade_list = []
for ext in ext_list:
    mpt = py3dmodel.calculate.face_midpt(ext)
    s_ext = py3dmodel.modify.scale(ext, math.sqrt(wwr), mpt)
    s_ext = py3dmodel.fetch.topo2topotype(s_ext)
    win_nrml = py3dmodel.calculate.face_normal(s_ext)
    shade_extrudes = py3dmodel.construct.extrude(s_ext, win_nrml, 1)
    shade_extrudes = py3dmodel.fetch.topo_explorer(shade_extrudes, "face")
    for s in shade_extrudes:
        s_nrml = py3dmodel.calculate.face_normal(s)
        if s_nrml == (0,0,1):
            shade_occface_list.append(s)
    
    cut_ext = py3dmodel.construct.boolean_difference(ext, s_ext)
    cut_ext = py3dmodel.fetch.topo_explorer(cut_ext, "face")[0]
    tri_face_list = py3dmodel.construct.simple_mesh(cut_ext)
    
    win_list.append(s_ext)
    cut_wall_list.extend(tri_face_list)
    
time2 = time.clock()
print "CONSTRUCTED MODEL", (time2-time1)/60.0, "mins"

print "CALCULATING ETTV..."

#calculate ettv 
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
shp_attribs_list = []

for wall in cut_wall_list:
    shp_attribs = buildingformeval.create_opaque_srf_shape_attribute(wall,2.16,"wall" )
    shp_attribs_list.append(shp_attribs)

for window in win_list:
    shp_attribs = buildingformeval.create_glazing_shape_attribute(window, 1.75, 0.4,"window")
    shp_attribs_list.append(shp_attribs)

for shade in shade_occface_list:
    shp_attribs = buildingformeval.create_shading_srf_shape_attribute(shade, "shade")
    shp_attribs_list.append(shp_attribs)
    
for footprint in [floor_plate]:
    shp_attribs = buildingformeval.create_shading_srf_shape_attribute(footprint, "footprint")
    shp_attribs_list.append(shp_attribs)
    
for roof in roof_occface_list:
    shp_attribs = buildingformeval.create_opaque_srf_shape_attribute(roof,0.5,"roof" )
    shp_attribs_list.append(shp_attribs)
    
result_dictionary = buildingformeval.calc_ettv(shp_attribs_list,weatherfilepath)
time3 = time.clock()
print "CALCULATED ETTV", (time3-time2)/60.0, "mins"

#calculate sensible load
ettv = result_dictionary["ettv"]
facade_area = result_dictionary["facade_area"]
floor_area = py3dmodel.calculate.face_area(floor_plate)

#calculate sensible load for air-tight env
sensible_load1 = buildingformeval.calc_sensible_load(facade_area, 0, floor_area, ettv, 0, equip_load_per_area = 25.0, 
                                                     occ_load_per_person = 75.0, light_load_per_area = 15.0, 
                                                     area_per_person = 10.0)

latent_load1 = buildingformeval.calc_latent_load(floor_area)
system_d1 = buildingformeval.central_all_air_system(sensible_load1, latent_load1, floor_area)

#calculate sensible load for natural ventilation
#need to calculate the solar gain from window

sensible_load2 = buildingformeval.calc_sensible_load(0, 0, floor_area, 0, 0,  equip_load_per_area = 0.0, 
                                                     occ_load_per_person = 75.0, light_load_per_area = 0.0, 
                                                     area_per_person = 10.0)

loads_2b_rmv = buildingformeval.calc_ach_4_equip(floor_area, 4, 25, 15, ach = 6, air_temp_increase = 2.0)
solar_gain = buildingformeval.calc_solar_gain_rad(shp_attribs_list, weatherfilepath)
print "SOLAR GAIN", solar_gain
sensible_load2 = sensible_load2 + loads_2b_rmv + solar_gain

system_d2 = buildingformeval.con_free_panels_w_fans(sensible_load2, floor_area, air_temp_c = 27.5, dewpt_temp_c = 24.3)

print "SENSIBLE LOAD", sensible_load1, sensible_load2
print "ALL-AIR-ENERGY", system_d1["energy_consumed_hr"], "CONDENSATION-FREE-ENERGY", system_d2 #["energy_consumed_hr"], system_d2["supply_temperature_for_panels"]

#py3dmodel.utility.visualise([cut_wall_list, win_list, shade_occface_list], ["WHITE", "BLUE", "BLACK"])