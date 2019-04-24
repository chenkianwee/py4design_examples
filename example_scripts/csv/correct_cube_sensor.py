import csv
from dateutil.parser import parse

csv_filepath = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt_avg.csv"
res_filepath = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt_avg_corrected.csv"
mrt_correction = 1.3

f = open(csv_filepath, "r")
reader = csv.reader(f, delimiter = ",")
reader_list = list(reader)
reader_list2 = reader_list[1:]
start_date = parse("2019-01-16T23:59:00.000")
end_date = parse("2019-01-18T00:00:00.000")

strx = reader_list[0][0] + "," + reader_list[0][1] + "\n"
cnt=0
for r in reader_list2:
    date = r[0]
    datetime = parse(date)
    if start_date < datetime < end_date:
        data = float(r[1])
        corrected = data - mrt_correction
        corrected_str = str(corrected)
        strx = strx + date + "," + corrected_str + "\n"    
    else:
        if cnt != len(reader_list2)-1:
            strx = strx + date + "," + r[1] + "\n"
        else:
            strx = strx + date + "," + r[1]
    cnt+=1    
    
f.close()    
f2 = open(res_filepath, "w+")
f2.write(strx)
f2.close()