import csv
import os
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

#formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
#formatter = DateFormatter('%H:%M:%S')
formatter = DateFormatter('%m-%d %H')

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2trdegc.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_1mins\\coldtube_mrt_ct_ph25_mrt_avg_corrected_1mins.csv"
csv_path3 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_1mins\\coldtube_mrt_ct_ph26_mrt_avg_corrected_1mins.csv"
csv_path4 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2tadegc.csv"
csv_path5 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2tgcdegc.csv"
csv_path6 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2vams.csv"

csv_path7 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1090.csv"
csv_path8 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1091.csv"
csv_path9 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2trdegc.csv"
csv_path10 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2vams.csv"

graph_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png"
title = "Cube MRT V.S. BestGlobe MRT with Air Speed, Air Temp & Globe Temp"

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
x_list1, y_list1 = rmv_non_numeric(x_list1, y_list1)

x_list2, y_list2, xmin2, xmax2 = csv2plot(csv_path2)
x_list3, y_list3, xmin3, xmax3 = csv2plot(csv_path3)

x_list4, y_list4, xmin4, xmax4 = csv2plot(csv_path4)
x_list4, y_list4 = rmv_non_numeric(x_list4, y_list4)
x_list5, y_list5, xmin5, xmax5 = csv2plot(csv_path5)
x_list5, y_list5 = rmv_non_numeric(x_list5, y_list5)
x_list6, y_list6, xmin6, xmax6 = csv2plot(csv_path6)
x_list6, y_list6 = rmv_non_numeric(x_list6, y_list6)

z_list = []
z_list.append(y_list2)
z_list.append(y_list3)
zipped_z = zip(*z_list)

cmrt_list = []
new_x_list2 = []
zcnt=0
for z in zipped_z:
    avg_mrt = avg_mixed_list(z)
    if type(avg_mrt) == float:
        cmrt_list.append(avg_mrt)
        new_x_list2.append(x_list2[zcnt])
    zcnt+=1

#=================================================================================================================================
#THE FIRST AXIS
#=================================================================================================================================
fig, ax1 = plt.subplots()
#ax1.scatter(new_x_list1, cmrt_list, c = 'b', marker=".", label = "cube mrt")
#ax1.scatter(x_list3, y_list3, c = 'c', marker=".", label = "best_globe_mrt")

ax1.plot(x_list4, y_list4, 'r-', label = "Air Temp")
ax1.plot(x_list5, y_list5, 'g-', label = "Globe Temp")
ax1.plot(x_list1, y_list1, 'c-', label = "MRT_globe")
ax1.plot(new_x_list2, cmrt_list, 'b-', label = "MRT_cube")

ax1.set_xlabel('Time (Mth-Day Hr)')

ax1.set_ylim(20, 35)
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('Degree ($^oC$)', color='b')
ax1.tick_params('y', colors='b')
#=================================================================================================================================
#THE SECOND AXIS
#=================================================================================================================================
ax2 = ax1.twinx()
ax2.plot(x_list6, y_list6, 'k--', label = "air_speed")
#ax2.scatter(x_list4, y_list4, c = 'r', marker = ".", label = "air_speed")
#ax2.set_ylim(25, 38)
ax2.set_ylabel('Air speed (m/s)', color='k')
ax2.tick_params('y', colors='k')

fig.tight_layout()
ax1.xaxis.set_major_formatter(formatter)
plt.title(title, fontsize=10 )

#=================================================================================================================================
#THE SECOND AXIS
#=================================================================================================================================
for i in range(13):
    filename = "cube_mrt_vs_best_mrt_02_with_airspeed" + str(i+16) + ".png"
    img_path = os.path.join(graph_dir, filename)
    
    str_xmin = "2019-01-" + str(i+16) + "T09:00:00.000"
    str_xmax = "2019-01-" + str(i+16) + "T18:00:00.000"
    
    xmin = parse(str_xmin )
    xmax = parse(str_xmax)
    plt.xlim(xmin, xmax) 

    # beautify the x-labels
    ax1.legend(bbox_to_anchor=(1.4, 1))
    #ax2.legend(loc="best")
    plt.gcf().autofmt_xdate()
    # plt.savefig(img_path, bbox_inches = "tight", dpi = 300,transparent=True,papertype="a3")
    #plt.show()