import json
import csv
#=======================================================================================================================================
#parameters
#=======================================================================================================================================
json_filepath = "F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\golfcart\\location\\json\\Testing_Golf_Cart_4people_2_19.json" 
csv_meta_path = "F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\golfcart\\location\\csv\\metadata200219.csv"
csv_data_path = "F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\golfcart\\location\\csv\\data200219.csv"
#=======================================================================================================================================
#functions
#=======================================================================================================================================

def meta2csv(dictionary, csv_path):
    with open(csv_path, 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, dictionary.keys())
        w.writeheader()
        w.writerow(dictionary)
        
def data2csv(fields, values, csv_path):
    #write the heading first 
    strx = ""
    for cnt,field in enumerate(fields):
        if cnt != len(fields)-1:
            if cnt == 1:
                strx = strx + "lat,lng,"
            else:
                strx = strx + field + ","
            
        else:
            strx = strx + field + "\n"
            
    for cnt,v in enumerate(values):
        print(v)
        for cnt2,w in enumerate(v):
            # print(cnt2,w)
            if cnt2 != len(v)-1:
                if cnt2==1:
                    # print(w)
                    strx = strx + str(w[0]) + "," + str(w[1]) + ","
                else:
                    strx = strx + str(w) + ","
            else:
                strx = strx + str(w) + "\n"
    f = open(csv_path, "w")
    f.write(strx)
    f.close()
    
#=======================================================================================================================================
#main script
#=======================================================================================================================================
#read the json file 
json_file = open(json_filepath, "r")
json_data = json.load(json_file)
json_file.close()

#get all the meta data from the file and write it to a csv
metadata = json_data['metadata']
meta2csv(metadata, csv_meta_path)

#get all the data from the json file and write it as a csv
data = json_data['data'][0]
fields = data['fields']
values = data['values']
data2csv(fields, values, csv_data_path)