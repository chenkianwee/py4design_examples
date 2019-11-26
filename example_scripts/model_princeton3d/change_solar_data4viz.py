import os 
import json

solar_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json\\viz"

def files2open(thehour):
    if 0 <= thehour < 744:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth0.json")
        thehour2 = thehour
    
    elif 744 <= thehour < 1416:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth1.json")
        thehour2 = thehour - 744
        
    elif 1416 <= thehour < 2160:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth2.json")
        thehour2 = thehour - 1416
        
    elif 2160 <= thehour < 2880:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth3.json") 
        thehour2 = thehour - 2160
        
    elif 2880 <= thehour < 3624:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth4.json")
        thehour2 = thehour - 2880
        
    elif 3624 <= thehour < 4344:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth5.json")
        thehour2 = thehour - 3624
        
    elif 4344 <= thehour < 5088:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth6.json") 
        thehour2 = thehour - 4344
        
    elif 5088 <= thehour < 5832:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth7.json") 
        thehour2 = thehour - 5088
        
    elif 5832 <= thehour < 6552:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth8.json") 
        thehour2 = thehour - 5832
        
    elif 6552 <= thehour < 7296:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth9.json") 
        thehour2 = thehour - 6552
        
    elif 7296 <= thehour < 8016:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth10.json") 
        thehour2 = thehour - 7296
        
    elif 8016 <= thehour < 8760:
        json_filepath = os.path.join(solar_dir, "viz_grd_solar_mth11.json")
        thehour2 = thehour - 8016
        
    return json_filepath, thehour2
    
def solar_data2weeks(solar_dir):
    for i in range(52):            
        week_hours = 168
        i2 = i+1
        end_hr = week_hours * i2
        start_hr = end_hr - week_hours
        if i == 51:
            end_hr = 8759
            
        json_path1, start_hr = files2open(start_hr)
        json_path2, end_hr = files2open(end_hr)
        json_datas = []
        
        if json_path1 == json_path2:     
            f = open(json_path1, "r")
            json_data = json.load(f)
            json_datas.extend(json_data)
            f.close()
        else:
            json_datas = []
            nhours = []
            for jpath in [json_path1, json_path2]:
                f = open(jpath, "r")
                json_data = json.load(f)
                nhours.append(len(json_data))
                json_datas.extend(json_data)
                
            end_hr = end_hr + nhours[0]
        
        print len(json_datas), start_hr, end_hr
        week_data = json_datas[start_hr:end_hr]
        
        viz_solar_filepath = os.path.join(solar_dir, "viz_grd_solar_week" + str(i)+ ".json")
        week_f = open(viz_solar_filepath, "w")
        week_str = json.dumps(week_data)
        week_f.write(week_str)
        week_f.close()
    
solar_data2weeks(solar_dir)