import csv
from dateutil.parser import parse
from datetime import timedelta

csv_path = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\data\\granfana_data\\csv3\\environment.csv"
csv_path2 = csv_path2 = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\data\\granfana_data\\csv3\\result.csv"
str_start_date = "2019-01-14T17:13:30.000Z"
start_date = parse(str_start_date)
str_end_date = "2019-01-15T17:13:30.000Z"
end_date = parse(str_end_date)
tdelta = timedelta(seconds=30)

def csv2dict(csv_path):
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ";")
    titles = []
    d = {}
    cnt = 0
    for r in csv_reader:
        if cnt == 1:
            titles = r
        if cnt > 1:
            date_str = r[0]
            date = parse(date_str)
            #print date, start_date, end_date
            if start_date <= date <= end_date:
                nr = len(r)
                d2 = []
                for i in range(nr-1):
                    if r[i+1] == "undefined":
                        d2.append(-1.0)
                    else:
                        d2.append(r[i+1])
                    
                d[date] = d2
        cnt+=1
    f.close()
    return d, titles

#date_list = gen_dates(start_date, end_date, tdelta)
#ndates = len(date_list)
csv_dict, titles = csv2dict(csv_path)
key_list = csv_dict.keys()
key_list.sort()
interp_data_list = []
for key in key_list:
    data_list = csv_dict[key]
    data_list2 = data_list[:]
    date_str1 = key.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    data_list = [date_str1] + data_list
    interp_data_list.append(data_list)
    
    
    date2 = key + tdelta
    date_str2 = date2.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    data_list2 = [date_str2] + data_list2
    interp_data_list.append(data_list2)
    

strx = "sep=;\n"
#write the titles
ntitles = len(titles)
tcnt = 0
for title in titles:
    if tcnt == ntitles-1:
        strx = strx + title + "\n"
    else:
        strx = strx + title + ";"
    tcnt+=1
    
for ad in interp_data_list:
    nad = len(ad)
    ad_cnt = 0
    for d in ad:
        if ad_cnt == nad-1:
            strx = strx + d + "\n"
        else:
            strx = strx + d + ";"
        ad_cnt+=1

r_f = open(csv_path2, "w")
r_f.write(strx)
r_f.close()