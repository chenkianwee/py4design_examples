import os
import csv
from dateutil.parser import parse
from datetime import timedelta

#============================================================================================================================================
#INPUTS
#============================================================================================================================================
csv_folder = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_1mins"
csv_folder2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_1hour"

str_start_date = "2018-10-25T17:00:00.000"
start_date = parse(str_start_date)
str_end_date = "2019-01-29T08:00:00.000"
end_date = parse(str_end_date)
tdelta = timedelta(hours=1)
fname_suffix = "1hour"
start_index = 0
end_index = 136
#============================================================================================================================================
#FUNCTIONS
#============================================================================================================================================
def gen_dates(start_date, end_date, tdelta):
    date_list = []
    cur_date = start_date
    while cur_date <= end_date:
        cur_date = cur_date + tdelta
        date_list.append(cur_date)
    return date_list

def csv2dict(csv_path):
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ",")
    titles = []
    d = {}
    cnt = 0
    for r in csv_reader:
        if cnt == 0:
            titles = r
        if cnt > 0:
            date_str = r[0]
            date = parse(date_str)
            #print date, start_date, end_date
            d2 = []
            if r[1].isalpha() == False:
                d2.append(float(r[1]))
                d[date] = d2
        cnt+=1
    f.close()
    return d, titles

#============================================================================================================================================
#FUNCTIONS
#============================================================================================================================================
date_list = gen_dates(start_date, end_date, tdelta)
ndates = len(date_list)
print "NUMBER OF DATES", ndates

fnames = os.listdir(csv_folder)
print fnames[-1]
fnames = fnames[start_index:end_index]
print fnames
nfiles = len(fnames) 
fcnt = 0
for fname in fnames:
    print "*** Processing ...", fname
    print "*** Processing ...", fcnt+1, "/", nfiles, "...files"
    csv_path = os.path.join(csv_folder, fname)
    csv_dict, titles = csv2dict(csv_path)
    key_list = csv_dict.keys()
    avg_data_list = []
    for cnt in range(ndates):
        avg_datas = []
        first_date = date_list[cnt]
        drange = tdelta/2
        first_date_min = first_date - drange
        first_date_max = first_date + drange
        print fname, fcnt+start_index, "/", end_index-1, "... progress ...", cnt+1, "/", ndates
        data_list_list = []
        rmv_key_list = []
        for key in key_list:
            if first_date_min <= key < first_date_max:
                data_list = csv_dict[key]
                data_list_list.append(data_list)
                rmv_key_list.append(key)
                
        key_list = [elem for elem in key_list if elem not in rmv_key_list]
        first_date_str = first_date.strftime("%Y-%m-%dT%H:%M:%S.000")
        avg_datas.append(first_date_str)
        if data_list_list:
            data_list2 = zip(*data_list_list)
            for data2 in data_list2:
                data2 = filter(lambda a: a != -1.0, data2)
                if data2:
                    avg_data = sum(data2)/float(len(data2))
                    avg_datas.append(str(avg_data))
                else:
                    avg_datas.append("undefined")
            avg_data_list.append(avg_datas)
            
        else:
            avg_datas.append("undefined")
            avg_data_list.append(avg_datas)

    #write the titles
    ntitles = len(titles)
    strx = ""
    tcnt = 0
    for title in titles:
        if tcnt == ntitles-1:
            strx = strx + title + "\n"
        else:
            strx = strx + title + ","
        tcnt+=1
        
    for ad in avg_data_list:
        nad = len(ad)
        ad_cnt = 0
        for d in ad:
            if ad_cnt == nad-1:
                strx = strx + d + "\n"
            else:
                strx = strx + d + ","
            ad_cnt+=1
    
    
    fname2 = fname.split(".")[0] + "_" + fname_suffix + ".csv"
    csv_path2 = os.path.join(csv_folder2, fname2)
    r_f = open(csv_path2, "w+")
    r_f.write(strx)
    r_f.close()
    print "*** Exported ...", fname2
    fcnt+=1