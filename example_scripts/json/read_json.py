import json
json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\json\\solar0.json" 
json_file = open(json_filepath, "r")
solar = json.load(json_file)
print len(solar)

"""
for s in solar:
    slist = s["solar"]
    if len(slist) !=0:
        print len(slist)
"""