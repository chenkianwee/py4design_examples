import json
import datetime
from dateutil.tz import gettz
from dateutil.parser import parse
#========================================================================
#filepaths
#========================================================================
location_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\location\\ckw_json\\LocationHistory\\Location History.json"
res_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\location\\ckw_json\\LocationHistory\\example_file.json"
#========================================================================
#main script
#========================================================================
print("*****************Reading the files*****************")
#read the location file
location_f = open(location_filepath , "r")
json_data = json.load(location_f)["locations"]
location_f.close()

print(len(json_data))
timezone = gettz()

#specify the date range
start = parse('2019-09-02T08:00:00.0Z')
start = start.replace(tzinfo=timezone)
end =  parse('2019-09-02T18:00:00.0Z')
end = end.replace(tzinfo=timezone)

#process the location points 
print("***************** Processing location points*****************")
new_json_data = []
for loc in json_data:
    timestamp = int(loc["timestampMs"])/1000
    date = datetime.datetime.fromtimestamp(timestamp)  # using the local timezone
    date = date.replace(tzinfo=timezone)
    if start <= date <= end:   
        new_json_data.append(loc)

loc_dict = {"locations":new_json_data}
f = open(res_filepath, "w")
json.dump(loc_dict, f)
f.close()
print(len(new_json_data))