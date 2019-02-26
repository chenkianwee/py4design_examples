import csv
from dateutil.parser import parse
from datetime import timedelta

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt_avg_1min.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt_avg_1min.csv"
f1 = open(csv_path, "r")
f2 = open(csv_path2, "r")
reader1 = csv.reader(f1, delimiter = ",")
reader2 = csv.reader(f2, delimiter = ",")

reader_list1 = list(reader1)[1:]
reader_list2 = list(reader2)[1:]
n = len(reader_list2)
for cnt in range(n):
    date1 = reader_list1[cnt][0]
    date2 = reader_list2[cnt][0]
    datetime1 = parse(date1)
    datetime2 = parse(date2)
    if datetime1 != datetime2:
        print "THE DIFF IN TIME", datetime1, datetime2, "THE LINE DIFF", cnt
        break