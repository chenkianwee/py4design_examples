import os
import json

import numpy as np
#==========================================================================================================================================
#functions
#==========================================================================================================================================
def eval_ill(ill_path):
    """
    This function reads the daysim result file from the simulation and returns the results as a dictionaries.
        
    Returns
    -------
    hourly results: list of dictionaries
        List of Dictionaries of hourly irradiance results (Wh/m2) or illuminance in (lux) that corresponds to the sensor points depending on the output parameter.
        Each dictionary is an hour of results of all the sensor points. Each dictionary has key "date" and "result_list". 
        The "date" key points to a date string e.g. "12 31 23.500" which means Dec 31st 23hr indicating the date and hour of the result.
        The "result_list" key points to a list of results, which is the result of all the sensor points. 
    
    """
    ill_file = open(ill_path, "r")
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
        
    ill_file.close()
    return res_dict_list

def read_sensor_pts(sensor_filepath):
    f = open(sensor_filepath, "r")
    pts = f.readlines()
    pyptlist = []
    pydir_list = []
    for pt in pts:
        pt = pt.replace("\n", "")
        pt_list = pt.split(" ")
        pypt = [float(pt_list[0]), float(pt_list[1]), float(pt_list[2])]
        pydir = [float(pt_list[3]), float(pt_list[4]), float(pt_list[5])]
        pyptlist.append(pypt)
        pydir_list.append(pydir)
    
    return pyptlist, pydir_list

def eval_ill_per_sensor(ill_path):
    """
    This function reads the daysim result file from the simulation and returns a list of results.
        
    Returns
    -------
    results per sensor : list of results
        Each row is a sensor srf with 8760 colume of hourly result
    
    """
    res_dict_list = eval_ill(ill_path)
    npts = len(res_dict_list[0]["result_list"])
    sensorptlist = []
    for _ in range(npts):
        sensorptlist.append([])

    for res_dict in res_dict_list:
        result_list = res_dict["result_list"]
        for rnum in range(npts):
            sensorptlist[rnum].append(result_list[rnum])
    return sensorptlist

def sort_monthly(annual_hr_list):
    annual = []
    for i in range(12):
        if i == 0:        
            mthly = annual_hr_list[0:744]
        elif i ==1:
            mthly = annual_hr_list[744:1416]
        elif i ==2:
            mthly = annual_hr_list[1416:2160]
        elif i ==3:
            mthly = annual_hr_list[2160:2880]
        elif i ==4:
            mthly = annual_hr_list[2880:3624]
        elif i ==5:
            mthly = annual_hr_list[3624:4344]
        elif i ==6:
            mthly = annual_hr_list[4344:5088]
        elif i ==7:
            mthly = annual_hr_list[5088:5832]
        elif i ==8:
            mthly = annual_hr_list[5832:6552]
        elif i ==9:
            mthly = annual_hr_list[6552:7296]
        elif i ==10:
            mthly = annual_hr_list[7296:8016]
        elif i ==11:
            mthly = annual_hr_list[8016:8760]
        annual.append(mthly)
    return annual

def write_mthly2json(point_res_list, solar_grid_dir):
    pm = 0
    for pmth in point_res_list:
        json_filepath = os.path.join(solar_grid_dir, "grd_solar_mth" + str(pm)+ ".json")
        json_str = json.dumps(pmth)
        f = open(json_filepath, "w")
        f.write(json_str)
        f.close()
        pm+=1
        
#==========================================================================================================================================
#main script
#==========================================================================================================================================
json_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json"

point_res_list = []#results separated into monthly 
for _ in range(12):
    point_res_list.append([])

#for cnt in range(19):
#    data_folder = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart\\grd_solar" + str(cnt)
#    solar_grid_dir = os.path.join(json_dir, "grd_solar" + str(cnt))
#    if not os.path.isdir(solar_grid_dir):
#        os.mkdir(solar_grid_dir)
        
#    point_res_list = []#results separated into monthly 
#    for _ in range(12):
#        point_res_list.append([])
#    
#    daysim_res_dir = os.path.join(data_folder, 'daysim_data', 'res')
#    ill_filepath = os.path.join(daysim_res_dir, 'daysim_data.ill')
#    pts_filepath = os.path.join(data_folder , "daysim_data", "pts", "sensor_points.pts")
#    
#    pyptlist, pydir_list = read_sensor_pts(pts_filepath)
#    res_2dlist = eval_ill_per_sensor(ill_filepath)
#    pcnt = 0
#    for pypt in pyptlist:
#        res_list = res_2dlist[pcnt]
#        mthly_res = sort_monthly(res_list)
#        mth_cnt = 0
#        for mth in mthly_res:
#            point_dict = {"point": pypt, "solar": mth}
#            point_res_list[mth_cnt].append(point_dict)
#            mth_cnt+=1
#            
#        pcnt+=1
#        
#    write_mthly2json(point_res_list, solar_grid_dir)
    
#    for i in range(6):
#        i= i+6
#        json_filepath = os.path.join(solar_grid_dir, "grd_solar_mth" + str(i)+ ".json")
#        f = open(json_filepath , "r")
#        json_data = json.load(f)
#        point_res_list[i].extend(json_data)
        
#write_mthly2json(point_res_list, json_dir)
overall_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json\\overall"



percentile_list = []
all_solar = []
for i in range(12):
    percentile_dict = {"month": i+1}
    mth_solar = []
    json_filepath = os.path.join(overall_dir, "grd_solar_mth" + str(i)+ ".json")
    f = open(json_filepath , "r")
    json_data = json.load(f)
    for d in json_data:
        solar_list = d["solar"]    
        #solar_list = [ elem for elem in solar_list if elem != 0]
        mth_solar.extend(solar_list)
        
    percentiles = np.percentile(mth_solar, [0,10,20,30,40,50,60,70,80,90,100])
    percentile_dict["percentiles"] = percentiles.tolist()
    percentile_list.append(percentile_dict)
    
f.close()


percentile_json_filepath = os.path.join(overall_dir, "solar_percentile.json")
json_str2 = json.dumps(percentile_list)
f3 = open(percentile_json_filepath, "w")
f3.write(json_str2)
f3.close()

#all_solar_json_filepath = os.path.join(overall_dir, "all_solar.json")
#solar_dict = [{"solar": all_solar}]
#json_str = json.dumps(solar_dict)
#f2 = open(all_solar_json_filepath, "w")
#f2.write(json_str)
#f2.close()
#
#
#percentiles = np.percentile(mth_solar, [0,10,20,30,40,50,60,70,80,90,100])
#print percentiles
#



