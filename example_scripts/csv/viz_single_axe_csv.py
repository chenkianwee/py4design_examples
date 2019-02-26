import os
import csv
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

#formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
formatter = DateFormatter('%Y:%m:%d')

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt_avg_1min.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt1086.csv"
csv_path3 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt1087.csv"
csv_path4 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt1088.csv"

csv_path5 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt_avg_1min.csv"
csv_path6 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1089.csv"
csv_path7 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1090.csv"
csv_path8 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1091.csv"

csv_path9 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m1trdegc.csv"

title = "Cube MRT V.S. BestGlobe MRT"

#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
def csv2plot(csv_path, index = None):
    x_list = []
    y_list = []
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ",")
    csv_list = list(csv_reader)
    if index !=None:
        csv_list[index[0]:index[1]]
    xmin = parse(csv_list[1][0])
    xmax = parse(csv_list[-1][0])
    cnt = 0
    for r in csv_list:
        if cnt!=0:
            x = parse(r[0])
            if r[1].isalpha() == False:
                y = float(r[1])
            else:
                y =  r[1]

            x_list.append(x)
            y_list.append(y)
        cnt+=1
        
    f.close()
    return x_list, y_list, xmin, xmax

def avg_mixed_list(listx):
    float_list = []
    for x in listx:
        if type(x) == float:
            float_list.append(x)
    if float_list:
        avg = sum(float_list)/float(len(float_list))
    else:
        avg = 'undefine'
    return avg

def rmv_non_numeric(listx, listy):
    data_list = []
    date_list = []
    cnt = 0
    for y in listy:
        if type(y) == float:
            data_list.append(y)
            date_list.append(listx[cnt])
        cnt+=1
    return date_list, data_list
#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
x_list1, y_list1, xmin1, xmax1 = csv2plot(csv_path)
#x_list2, y_list2, xmin2, xmax2 = csv2plot(csv_path2)
#x_list3, y_list3, xmin3, xmax3 = csv2plot(csv_path3)
#x_list4, y_list4, xmin4, xmax4 = csv2plot(csv_path4)
x_list5, y_list5, xmin5, xmax5 = csv2plot(csv_path5)
#x_list6, y_list6, xmin6, xmax6 = csv2plot(csv_path6)
#x_list7, y_list7, xmin7, xmax7 = csv2plot(csv_path7)
#x_list7, y_list8, xmin8, xmax8 = csv2plot(csv_path8)

z_list = []
z_list.append(y_list1)
z_list.append(y_list5)
zipped_z = zip(*z_list)

new_x_list1 = []
cmrt_list = []
zcnt=0
for z in zipped_z:
    avg_mrt = avg_mixed_list(z)
    if type(avg_mrt) == float:
        new_x_list1.append(x_list1[zcnt])
        cmrt_list.append(avg_mrt)
        
    zcnt+=1

x_list9, y_list9, xmin9, xmax9 = csv2plot(csv_path9, index = [478018, -1])
x_list9, y_list9 = rmv_non_numeric(x_list9, y_list9)
#for colour reference refer to page https://matplotlib.org/examples/color/named_colors.html
#for marker reference refer to page https://matplotlib.org/api/markers_api.html#module-matplotlib.markers

#plt.scatter(new_x_list1, cmrt_list, c = "b", marker=".", label="cube_mrt_avg")
#plt.scatter(x_list2, y_list2, c = "b", marker="s", label="1086")
#plt.scatter(x_list3, y_list3, c = "b", marker="x", label="1087")
#plt.scatter(x_list4, y_list4, c = "b", marker="o", label="1088")
#plt.scatter(x_list5, y_list5, c = "r", marker=".", label="ph26_mrt_avg")
#plt.scatter(x_list6, y_list6, c = "r", marker="s", label="1089")
#plt.scatter(x_list7, y_list8, c = "r", marker="x", label="1090")
#plt.scatter(x_list7, y_list8, c = "r", marker="o", label="1091")

#plt.scatter(x_list9, y_list9, c = "r", marker=".", label="best_globe1_mrt")
plt.plot(new_x_list1, cmrt_list, 'b-', label = "cube_mrt") 
plt.plot(x_list9, y_list9, 'r-', label = "best_globe1_mrt")

plt.title(title, fontsize=10 )
plt.xlabel('Date', fontsize=10)
plt.ylabel('Temp ($^oC$)', fontsize=10)
plt.legend(bbox_to_anchor=(1.05, 1))
plt.ylim(20,35)

img_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png"
for i in range(1):    
    filename = "cube_mrt_vs_best1_mrt_01" + str(i+18) + ".png"
    img_filepath = os.path.join(img_dir, filename)
    
    str_xmin = "2019-01-" + str(i+18) + "T09:00:00.000"
    str_xmax = "2019-01-" + str(i+18) + "T18:00:00.000"
    xmin = parse(str_xmin)
    xmax = parse(str_xmax)
    plt.xlim(xmin, xmax) 
    
    # beautify the x-labels
    plt.gcf().autofmt_xdate()

    plt.savefig(img_filepath, bbox_inches = "tight" , dpi = 300, transparent=True,papertype="a1")
    #plt.show()