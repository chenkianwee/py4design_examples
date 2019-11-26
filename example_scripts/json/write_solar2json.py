import os 
import time
import json

from dateutil.parser import parse
from datetime import timedelta

import shapefile
from py4design import py3dmodel, urbangeom

#===========================================================================================
#INPUTS
#===========================================================================================
bldg_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall\\bldg.brep"
solar_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\rad\\daysim_data\\res\\daysim_data.ill"
sensor_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\rad\\daysim_data\\pts\\sensor_points.pts"

shp_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\main_campus_roofs\\main_campus_roofs.shp"
json_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\json"
filename = "solar"
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def eval_daysim_res(res_filepath):
    ill_file = open(res_filepath, "r")
    ill_results = ill_file.readlines()
    res_dict_list = []
    for ill_result in ill_results:
        result_dict = {}
        ill_result = ill_result.replace("\n", "")
        ill_resultlist = ill_result.split(" ")
        date = ill_resultlist[0] + " " + ill_resultlist[1] + " " + ill_resultlist[2]
        result_dict["date"] = date
        resultlist = ill_resultlist[4:]
        resultlist_f = []
        for r in resultlist:
            resultlist_f.append(float(r))
        result_dict["result_list"] = resultlist_f
        res_dict_list.append(result_dict)
    
    return res_dict_list

def eval_res_per_sensor(res_filepath):
    res_dict_list = eval_daysim_res(res_filepath)
    npts = len(res_dict_list[0]["result_list"])
    sensorptlist = []
    for _ in range(npts):
        sensorptlist.append([])

    for res_dict in res_dict_list:
        result_list = res_dict["result_list"]
        for rnum in range(npts):
            sensorptlist[rnum].append(result_list[rnum])
    return sensorptlist

def read_sensor_pts(sensor_filepath):
    s_file = open(sensor_filepath, "r")
    results = s_file.readlines()
    pyptlist = []
    for r in results:
        r = r.replace("\n", "")
        r_list = r.split(" ")
        x = float(r_list[0])
        y = float(r_list[1])
        pypt = [x,y,0]
        pyptlist.append(pypt)
        
    return pyptlist

def monthly_watts(watts_list):
    annual = []
    for i in range(12):
        if i == 0:        
            mthly = watts_list[0:744]
        elif i ==1:
            mthly = watts_list[744:1416]
        elif i ==2:
            mthly = watts_list[1416:2160]
        elif i ==3:
            mthly = watts_list[2160:2880]
        elif i ==4:
            mthly = watts_list[2880:3624]
        elif i ==5:
            mthly = watts_list[3624:4344]
        elif i ==6:
            mthly = watts_list[4344:5088]
        elif i ==7:
            mthly = watts_list[5088:5832]
        elif i ==8:
            mthly = watts_list[5832:6552]
        elif i ==9:
            mthly = watts_list[6552:7296]
        elif i ==10:
            mthly = watts_list[7296:8016]
        elif i ==11:
            mthly = watts_list[8016:8760]
        annual.append(mthly)
    return annual
    
def write_poly_shpfile(occface_list, shp_filepath, attname_list, att_list):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('uid','N',10)
    for attname in attname_list:
        print attname
        w.field(attname,'N', decimal=2)
         
    cnt=0
    for occface in occface_list:
        wires = py3dmodel.fetch.topo_explorer(occface, "wire")
        nwires = len(wires)
        atts = att_list[cnt]
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(occface)
            poly_shp_list = []
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if is_anticlockwise2:
                        pyptlist.reverse()
                else: #means its a hole not a face
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                
                pyptlist2d = []
                for pypt in pyptlist:
                    x = pypt[0]
                    y = pypt[1]
                    pypt2d = [x,y]
                    pyptlist2d.append(pypt2d)
                poly_shp_list.append(pyptlist2d)
                
            w.record(cnt, atts[0], atts[1], atts[2])
            w.poly(poly_shp_list)
                    
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(occface)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
            if is_anticlockwise:
                pyptlist.reverse()
            pyptlist2d = []
            for pypt in pyptlist:
                x = pypt[0]
                y = pypt[1]
                pypt2d = [x,y]
                pyptlist2d.append(pypt2d)
                
            w.record(cnt, atts[0], atts[1], atts[2])
            w.poly([pyptlist2d])
            
        cnt+=1
    w.close()
    
#===========================================================================================
#MAIN
#===========================================================================================
time1 = time.clock()
display2dlist = []
print "*******Reading Buildings***************"
bldg_cmpd = py3dmodel.utility.read_brep(bldg_filepath)
bldg_solids = py3dmodel.fetch.topo_explorer(bldg_cmpd, "solid")

roof_list = []
facade_list = []
footprint_list = []

attname_list = ["zmin", "zmax", "height"]
att_list = []

print "*******Separating Building Surfaces***************"
for bldg_solid in bldg_solids:
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(bldg_solid)
    facades, roofs, footprints = urbangeom.identify_building_surfaces(bldg_solid)
    height = zmax-zmin
    atts = [zmin, zmax, height]
    att_list.append(atts)
    
    facade_list.extend(facades)
    roof_list.extend(roofs)
    footprint_list.extend(footprints)

print "*******Writing to ShpFile***************"
write_poly_shpfile(roof_list, shp_filepath, attname_list, att_list)

print "*******Reading Solar Results***************"
solar_res = eval_res_per_sensor(solar_filepath)
#solar_res = solar_res[0:100]

print "*******Reading Sensor Points***************"
sensor_ptlist = read_sensor_pts(sensor_filepath)
#sensor_ptlist = sensor_ptlist[0:100]

print "*******For Each Roof Find Sensor Points***************"
roof_perf_list = []
#roof_list = roof_list[0:100]
nroofs = len(roof_list)
rcnt = 0
for roof in roof_list:
    print "*******Processing", rcnt+1, "/", nroofs, "***************"
    area = py3dmodel.calculate.face_area(roof)
    nroof = py3dmodel.modify.flatten_face_z_value(roof)
    res_list = []
    pcnt_list = []
    watts_list = []
    
    pcnt = 0
    for pt in sensor_ptlist:
        is_in_face = py3dmodel.calculate.point_in_face(pt, nroof)
        if is_in_face:
            pcnt_list.append(pcnt)
        pcnt+=1
    
    for i in pcnt_list:
        ress = solar_res[i]
        res_list.append(ress)
        
    zip_res_list = zip(*res_list)
    for r in zip_res_list:
        avg = sum(r)/float(len(r))
        watts = avg*area
        watts = round(watts, 2)
        watts_list.append(watts)
        

    mthly_watts = monthly_watts(watts_list)
    roof_perf_list.append(mthly_watts)
    rcnt+=1
        
#setup 12 list for each month 
mthly_res_list = []
for _ in range(12):
    mthly_res_list.append([])
    
rcnt = 0
for roofp in roof_perf_list:
    scnt = 0
    for p in roofp:
        mth_dict = {"uid":rcnt, "solar":p}
        mthly_res_list[scnt].append(mth_dict)
        scnt+=1
        
    rcnt+=1
        
fcnt = 0
for mr in mthly_res_list:
    #it should be the number of roof surfaces
    print len(mr), len(roof_list), "it should be the same number"
    json_str = json.dumps(mr)
    json_filepath = os.path.join(json_dir, filename + str(fcnt) + ".json")
    f = open(json_filepath, "w")
    f.write(json_str)
    f.close()
    fcnt +=1
    
time2 = time.clock()
total = time2-time1/60.0
print "*******Total Time Taken:", total, "***************"