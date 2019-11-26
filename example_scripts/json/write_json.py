import json

filepath = "C:\\Users\\chaosadmin\\Desktop\\test.json"
x = [{"point": [0,0,0], "height":100.0}, {"point": [0,0,1], "height":200}]
json_str = json.dumps(x)

f = open(filepath, "w")
f.write(json_str)
f.close()

json_file = open(filepath, "r")
json_str = json.load(json_file)
print type(json_str[0]["height"])