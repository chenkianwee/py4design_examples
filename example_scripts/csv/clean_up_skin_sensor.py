from dateutil.parser import parse
import pandas as pd
from datetime import timedelta

#td = timedelta(hours=8)

csv_filepath = "C:\\Users\\chaosadmin\\Downloads\\2018-12-11T04_40_10.260Z_CC_53_5E_44_EC_4F.csv"
res_filepath = "C:\\Users\\chaosadmin\\Downloads\\2018-12-11T04_40_10.260Z_CC_53_5E_44_EC_4F_processed.csv"
f = open(csv_filepath, "r")
lines = f.readlines()
lines = lines[0].split("\r")
lines1 = lines[0:14]
lines2 = lines[14:]
strx = "sep=,\n"
cnt = 0
for l in lines1:
    l = l.split(",")
    fl = filter(None, l)
    if cnt == 13:
        fl = fl[0:11]
    nfl = len(fl)
    if cnt == 12:
        strx = strx + "\n"
    flcnt = 0
    for d in fl:
        if flcnt != nfl-1:
            strx = strx + d + ","
        else:
            strx = strx + d + "\n"
        flcnt+=1
    cnt+=1
    

cnt2 = 0
for l2 in lines2:
    l2 = l2.split(",")[0:11]
    td = timedelta(seconds=cnt2)
    if cnt2 < 2536:
        hr_str = "11"
    else:
        hr_str = "12"
    date_time_str = "2018-12-11 " + hr_str + ":" + l2[0]  
    date_time = parse(date_time_str)

    str_date = date_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    print cnt2, l2[0], str_date
#    date = int(l2[1])
#    pdtime = pd.to_datetime(date,unit='us') + td
#    str_date = pdtime.strftime("%Y-%m-%d %H:%M:%S.%f")
    
    l3 = l2[1:11]
    strx = strx + str_date + ","
    nl3 = len(l3)
    lcnt = 0
    for d2 in l3:
        if lcnt != nl3-1:  
            strx = strx + d2 + ","
        else:
            strx = strx + d2 + "\n"
        lcnt+=1
    cnt2+=1     


f2 = open(res_filepath, "w+")
f2.write(strx)
f2.close()
