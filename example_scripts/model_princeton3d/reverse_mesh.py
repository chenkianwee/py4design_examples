import json
import numpy as np

json_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\bldgs.json"
json_filepath2 = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\meshes_4carts\\bldgs2.json"
f = open(json_filepath, "r")
json_data = json.load(f)
new_data_list = []
for data in json_data:
    verts = data["vertices"]
    faces = data["indices"]
    
    for face in faces:
        #print face
        face.reverse()
        #print face
    
    face_colours = data["face_colours"]
    
    new_data = {"vertices": verts, "indices": faces, "face_colours": face_colours}
    new_data_list.append(new_data)
    
json_str = json.dumps(new_data_list)
f2 = open(json_filepath2, "w")
f2.write(json_str)
f2.close()