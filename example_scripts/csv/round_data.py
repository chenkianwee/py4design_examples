import csv
from dateutil.parser import parse
from datetime import timedelta

#============================================================================================================================================
#INPUTS
#============================================================================================================================================
csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1090.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_mrt_ct_ph26_mrt1090_15mins.csv"

str_start_date = "2018-10-25T17:30:00.000"
start_date = parse(str_start_date)
str_end_date = "2019-01-29T08:45:00.000"
end_date = parse(str_end_date)
tdelta = timedelta(minutes=15)
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
            if start_date <= date <= end_date:
#                nr = len(r)
                d2 = []
                d2.append(float(r[1]))
#                for i in range(nr-1):
#                    if r[i+1] == "undefined":
#                        d2.append(-1.0)
#                    else:
#                        d2.append(float(r[i+1]))
                    
                d[date] = d2
        cnt+=1
    f.close()
    return d, titles

#============================================================================================================================================
#FUNCTIONS
#============================================================================================================================================
    
date_list = gen_dates(start_date, end_date, tdelta)
ndates = len(date_list)
csv_dict, titles = csv2dict(csv_path)
key_list = csv_dict.keys()
print "NUMBER OF DATES", ndates
avg_data_list = []
for cnt in range(ndates):
    avg_datas = []
    first_date = date_list[cnt]
    drange = tdelta/2
    first_date_min = first_date - drange
    first_date_max = first_date + drange        
    print "... progress ...", cnt+1, "/", ndates
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
        
r_f = open(csv_path2, "w+")
r_f.write(strx)
r_f.close()
print "*** Exported ...", csv_path2