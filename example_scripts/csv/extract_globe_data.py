import csv
import os
from dateutil.parser import parse

globe_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\globe_data\\raw"
res_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\globe_data\\globe"
fnames = os.listdir(globe_dir)
#fnames = fnames[0:2]
for fname in fnames:
    globe_filepath = os.path.join(globe_dir, fname)
    f = open(globe_filepath, "r")

    csv_reader = csv.reader(f, delimiter = "\t")
    csv_rows = list(csv_reader)
    csv_rows = csv_rows[19:]
    tobezip_list = []
    for r in csv_rows:
        r = filter(None, r)
        if r:
            if len(r) > 1:
                tobezip_list.append(r)
    
    zipped_list = zip(*tobezip_list)
    
    tcol = zipped_list[1]
    if tcol[0][1:-1] != "Time":
        tcol = zipped_list[2]
        dcol = zipped_list[1]
        
        
    else:
        date = fname.split("_")[0]
        ntimes = len(tcol)
        dcol = []
        dcol.append(" Date ")
        for _ in range(ntimes-1):
            yr = date[0:4]
            mth = date[4:6]
            day = date[6:]
            dcol.append(" " + day + "/" + mth + "/" + yr + " ")
        
    tcol2 = []
    tcnt = 0
    for t in tcol:
        t2 = t[1:-1]
        d = dcol[tcnt]
        d2 = d[1:-1]
        
        if tcnt !=0:
            d2split = d2.split("/")
            yr = d2split[2]
            mth = d2split[1]
            day = d2split[0]
            if len(mth) <2:
                mth = "0"+mth
            if len(day) < 2:
                day = "0" + day
                
            d3 = yr + mth + day
            d = parse(d3 + "T" + t2)
            dstr = d.strftime("%Y-%m-%dT%H:%M:%S.%f")
            tcol2.append(dstr)
        else:
            tcol2.append(t2)
        tcnt+=1

    data_zipped_list = zipped_list[3:]
    nfiles = len(data_zipped_list)
    data_zipped_list2 = [tcol2] + data_zipped_list
    
    for data in data_zipped_list:
        title = ''.join(e for e in data[0] if e.isalnum())    
        res_filepath = os.path.join(res_dir, "coldtube_bestglobe_" + title.lower() + ".csv")
        #check if the file already exist 
        is_exist = os.path.isfile(res_filepath)
        if is_exist:
            res_file = open(res_filepath, "a")
        else:
            res_file = open(res_filepath, "w+")
            
        res_str = ""
        ndata = len(data)
        dcnt = 0
        for d in data:
            if dcnt == 0:                
                if not is_exist:
                    res_str += tcol2[dcnt] + "," + d.replace(" ", "") + "\n"
            else:
                try:
                    float(d)
                    res_str += tcol2[dcnt] + "," + d.replace(" ", "") + "\n"
                except:
                    pass
    
            dcnt+=1
                
        res_file.write(res_str)
        res_file.close()
        print "*** Exported ...", fname, "...", title
    f.close()
