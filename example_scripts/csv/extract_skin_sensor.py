import os
import csv
from dateutil.parser import parse

csv_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\skin_sensor_raw"
res_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data"

fnames = os.listdir(csv_dir)
print fnames
#fnames = fnames[0:2]
raw_sensor_fx = 1.953125 #uV
for fname in fnames:
    csv_filepath = os.path.join(csv_dir, fname)
    f = open(csv_filepath)
    reader = csv.reader(f)
    print csv_filepath
    reader_list  = list(reader)
    #reader_list = reader_list[0:20]
    dev_id = reader_list[2][0].split("=")[1].replace(" ", "")
    filename = "coldtube_skin_" + reader_list[3][0].split("=")[1].replace(" ", "").lower()
    #======================================================================
    #GET THE CONSTANTS REQUIRED FOR CALCULATING THE WATTS AND TEMP
    #======================================================================    
    constant_row = reader_list[12]
    s1 = (float(constant_row[0].split("=")[1]))/1000 #nV/(W/m2)
    t1 = float(constant_row[3].split("=")[1]) #mC
    
    title_row = reader_list[14]
    data_rows = reader_list[15:]
    
    str_watts = "time,value,name\n"
    str_temp = "time,value,name\n"
    
    nrows = len(data_rows)
    cnt = 0
    print filename
    
    for r in data_rows:
        
        time = parse(r[0])
        time_str = time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        hf_a1 = float(r[4])
        temp_a1 = float(r[5])
        heat_fx = (hf_a1*raw_sensor_fx)/s1 #w/m2
        skin_temp = (temp_a1 - t1)/1000
        if cnt != nrows-1:
            #WRITE THE FILE FOR WATTS
            str_watts = str_watts + time_str + "," + str(heat_fx) + "," + dev_id + "\n"  
            #WRITE THE FILE FOR TEMP
            str_temp = str_temp + time_str + "," + str(skin_temp) + "," + dev_id + "\n"  
        else:
            #WRITE THE FILE FOR WATTS
            str_watts = str_watts + time_str + "," + str(heat_fx) + "," + dev_id  
            #WRITE THE FILE FOR TEMP
            str_temp = str_temp + time_str + "," + str(skin_temp) + "," + dev_id + "\n"
            
        cnt+=1
    
    flx_filepath = os.path.join(res_dir, filename + "_flux.csv")
    flx_f = open(flx_filepath, "w+")
    flx_f.write(str_watts)
    flx_f.close()
    print "*** Export ...", flx_filepath
    
    temp_filepath = os.path.join(res_dir, filename + "_temp.csv")
    temp_f = open(temp_filepath, "w+")
    temp_f.write(str_temp)
    temp_f.close()
    print "*** Export ... ...", temp_filepath
    f.close()