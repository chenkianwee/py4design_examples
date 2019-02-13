import csv
#csv_path = "F:\\kianwee_work\\spyder_workspace\\py4design_examples\\example_scripts\\gui\\coldtube_data\\panel6.csv"
csv_path = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\data\\granfana_data\\csv3\\environment.csv"
csv_path2 = csv_path2 = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\data\\granfana_data\\csv3\\result.csv"
f = open(csv_path, mode = "r")
csv_reader = csv.reader(f, delimiter = ",")
strx = "sep=;\n"
cnt = 0
for r in csv_reader:
    if cnt > 0:
        nr = len(r)
        scnt =0
        for s in r:
            if scnt == nr-1:
                strx = strx + s + "\n"
            else:
                strx = strx + s + ";"
            scnt+=1
    cnt+=1

f.close()
#csv_path2 = "F:\\kianwee_work\\spyder_workspace\\py4design_examples\\example_scripts\\gui\\coldtube_data\\panel6_1.csv"
f2 = open(csv_path2, "w")
f2.write(strx)
f2.close()