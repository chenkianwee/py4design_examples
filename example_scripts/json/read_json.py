import json
json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\golfcart\\model3d\\solar_travel_data\\ground_solar\\viz_grd_solar_week51.json" 
json_file = open(json_filepath, "r")
solar = json.load(json_file)
print(solar[-1])
solar.append(solar[-1])
json_file.close()
print(len(solar))
json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\golfcart\\model3d\\solar_travel_data\\ground_solar\\viz_grd_solar_week52.json" 
json_file = open(json_filepath, "w")
json.dump(solar, json_file)
json_file.close()

# total = 0
# for i in range(52):
#     json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\golfcart\\model3d\\solar_travel_data\\ground_solar\\viz_grd_solar_week" + str(i) + ".json"
#     json_file = open(json_filepath, "r")
#     solar = json.load(json_file)
#     nsolar = len(solar)
#     total += nsolar
#     print(total, i)
    