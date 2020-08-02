import json
#=======================================================================================================================================
#parameters
#=======================================================================================================================================
json_filepath = "F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\golfcart\\location\\json\\Testing_Golf_cart_.json" 
res_path = "F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\golfcart\\location\\json\\Testing_Golf_cart_converted.json" 
#=======================================================================================================================================
#functions
#=======================================================================================================================================
def values2loc(values, json_path):
    dic = {'locations':[]}
    for v in values:
        ts = int(v[0]) * 1000
        lat = int(v[1][0] * 10e6)
        lng = int(v[1][1] * 10e6)
        v_d = {'timestampMs': ts, 'latitudeE7': lat, 
               'longitudeE7':lng}
        dic['locations'].append(v_d)
        
    with open(json_path, 'w') as outfile:
        json.dump(dic, outfile)

#=======================================================================================================================================
#main script
#=======================================================================================================================================
#read the json file 
json_file = open(json_filepath, "r")
json_data = json.load(json_file)
json_file.close()

#get all the data from the json file and write it as a csv
data = json_data['data'][0]
fields = data['fields']
print(fields)
values = data['values']
values2loc(values, res_path)
# print(values)