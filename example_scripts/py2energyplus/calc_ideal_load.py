import pyliburo
import os
import time

base_file_path = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_scripts\\py2energyplus\\base.idf"
weather_file_path = "F:\\kianwee_work\\digital_repository\\energyplus_share\\weatherfile\\SGP_Singapore.486980_IWEC.epw"
data_folder_path = "F:\\kianwee_work\\spyder_workspace\\pyliburo_example_files\\example_scripts\\py2energyplus\\ep_data"
time1 = time.clock()
#construct the bldg to be analysed
rec1 = pyliburo.py3dmodel.construct.make_rectangle(10,10)
extrude1 = pyliburo.py3dmodel.construct.extrude(rec1, (0,0,1), 4)
rec1_midpt = pyliburo.py3dmodel.calculate.face_midpt(rec1)

facade_list, roof_list, footprint_list = pyliburo.gml3dmodel.identify_building_surfaces(extrude1)
chosen_facade = facade_list[0]
facade_midpt = pyliburo.py3dmodel.calculate.face_midpt(chosen_facade)
window = pyliburo.py3dmodel.modify.uniform_scale(facade_list[0], 0.95, 0.95,0.4,facade_midpt) 
window = pyliburo.py3dmodel.fetch.shape2shapetype(window)

win_nrml = pyliburo.py3dmodel.calculate.face_normal(window)
win_extrude = pyliburo.py3dmodel.construct.extrude(window, win_nrml, 1)
vertical, shade_list, down = pyliburo.gml3dmodel.identify_building_surfaces(win_extrude)

time2 = time.clock()
print "CONSTRUCTED MODEL", (time2-time1)/60.0
idf_obj = pyliburo.py2energyplus.Idf()
idf_obj.set_version("8.7.0")
idf_obj.set_time_step("15")
idf_obj.set_shadow_calc("20", "100000")
idf_obj.set_north("0")
idf_obj.set_terrain("Urban")
idf_obj.set_solar_dist("FullExterior")
idf_obj.set_max_warmup_days("25")
idf_obj.set_ground_temp(["20", "20", "20", "20", "20", "20","20", "20", "20", "20", "20", "20"])
idf_obj.add_output_surfaces_drawing("DXF")
idf_obj.set_output_control_table_style("HTML","JtoKWH")
idf_obj.add_output_table_summary_report("AllSummary")

pyliburo.py2energyplus.RunPeriod("1", "1", "1", "2", idf_obj)
zone_name = "zone1"
zone_obj = pyliburo.py2energyplus.IdfZone(zone_name,idf_obj)
zone_obj.set_cool_schedule("09:00","17:00", "25")
zone_obj.set_heat_schedule("09:00","17:00", "18")
#zone_obj.set_internal_gains_schedule("09:00","17:00", "20")

srf_list = []

wcnt = 0
for facade in facade_list:
    name = "wall" + str(wcnt)
    con = "Medium Exterior Wall"
    boundary = "Outdoors"
    pyptlist = pyliburo.py3dmodel.fetch.pyptlist_frm_occface(facade)
    srf = pyliburo.py2energyplus.IdfZoneSurface(name, pyptlist,con, "Wall", boundary)
    srf_list.append(srf)
    zone_obj.add_surface(srf)
    wcnt +=1
    
rcnt = 0
for roof in roof_list:
    name = "roof" + str(rcnt)
    con = "Medium Roof/Ceiling"
    boundary = "Outdoors"
    roof = pyliburo.py3dmodel.modify.reverse_face(roof)
    pyptlist = pyliburo.py3dmodel.fetch.pyptlist_frm_occface(roof)
    srf = pyliburo.py2energyplus.IdfZoneSurface(name, pyptlist,con, "Roof", boundary)
    zone_obj.add_surface(srf)
    rcnt +=1
    
fcnt = 0
for floor in footprint_list:
    name = "floor" + str(fcnt)
    con = "Medium Floor"
    boundary = "Adiabatic"
    floor = pyliburo.py3dmodel.modify.reverse_face(floor)
    pyptlist = pyliburo.py3dmodel.fetch.pyptlist_frm_occface(floor)
    srf = pyliburo.py2energyplus.IdfZoneSurface(name, pyptlist,con, "Floor", boundary)
    zone_obj.add_surface(srf)
    fcnt +=1
    

name = "win0"
con = "Sgl Clr 3mm"
host_srf = "wall0"
pyptlist = pyliburo.py3dmodel.fetch.pyptlist_frm_occface(window)
srf = pyliburo.py2energyplus.IdfWindow(name, pyptlist, con, host_srf)
srf_list[0].add_window(srf)

name = "shade0"
host_srf = "wall0"
pyptlist = pyliburo.py3dmodel.fetch.pyptlist_frm_occface(shade_list[0])
srf = pyliburo.py2energyplus.IdfShade(name, pyptlist, None, host_srf)
srf_list[0].add_shade(srf)

pyliburo.py2energyplus.OutputMeter("Cooling:EnergyTransfer", "Hourly", idf_obj)
pyliburo.py2energyplus.OutputMeter("Heating:EnergyTransfer", "Hourly", idf_obj)

idf_obj.execute_idf(base_file_path, weather_file_path, data_folder_path)