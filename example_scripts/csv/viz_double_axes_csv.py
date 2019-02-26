import csv
import os
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

#formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
#formatter = DateFormatter('%H:%M:%S')
formatter = DateFormatter('%m-%d %H:%M')

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_skin_chestforrest_flux.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_skin_chestforrest_temp.csv"
img_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png\\forrest_chest.png"
title = "Forrest Chest"

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt_avg_1min.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt1086.csv"
csv_path3 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt1087.csv"
csv_path4 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph25_mrt1088.csv"

csv_path5 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt_avg_1min.csv"
csv_path6 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1089.csv"
csv_path7 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1090.csv"
csv_path8 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_mrt_ct_ph26_mrt1091.csv"

csv_path9 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2trdegc.csv"
csv_path10 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data\\coldtube_bestglobe_m2vams.csv"

img_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png"
title = "Cube MRT V.S. BestGlobe MRT with Air Speed"

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
x_list2, y_list2, xmin2, xmax2 = csv2plot(csv_path5)
x_list3, y_list3, xmin3, xmax3 = csv2plot(csv_path9, index = [478018, -1])
x_list3, y_list3 = rmv_non_numeric(x_list3, y_list3)
x_list4, y_list4, xmin4, xmax4 = csv2plot(csv_path10, index = [478018, -1])
x_list4, y_list4 = rmv_non_numeric(x_list4, y_list4)

z_list = []
z_list.append(y_list1)
z_list.append(y_list2)
zipped_z = zip(*z_list)

cmrt_list = []
new_x_list1 = []
zcnt = 0
for z in zipped_z:
    avg_mrt = avg_mixed_list(z)
    if type(avg_mrt) == float:
        new_x_list1.append(x_list1[zcnt])
        cmrt_list.append(avg_mrt)
    zcnt += 1


fig, ax1 = plt.subplots()
ax1.plot(new_x_list1, cmrt_list, 'b-', label = "cube mrt")
#ax1.scatter(new_x_list1, cmrt_list, c = 'b', marker=".", label = "cube mrt")
ax1.plot(x_list3, y_list3, 'c--', label = "best_globe_mrt")
#ax1.scatter(x_list3, y_list3, c = 'c', marker=".", label = "best_globe_mrt")
ax1.set_xlabel('Time (Mth/Day Hr:Min)')
ax1.set_ylim(20, 35)
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('Degree ($^oC$)', color='b')
ax1.tick_params('y', colors='b')

ax2 = ax1.twinx()
ax2.plot(x_list4, y_list4, 'r--', label = "air_speed")
#ax2.scatter(x_list4, y_list4, c = 'r', marker = ".", label = "air_speed")
#ax2.set_ylim(25, 38)
ax2.set_ylabel('Air Movement (m/s)', color='r')
ax2.tick_params('y', colors='r')

fig.tight_layout()
ax1.xaxis.set_major_formatter(formatter)
plt.title(title, fontsize=10 )

for i in range(13):
    filename = "cube_mrt_vs_best1_mrt_01_with_airspeed" + str(i+17) + ".png"
    img_path = os.path.join(img_dir, filename)
    
    str_xmin = "2019-01-" + str(i+17) + "T09:00:00.000"
    str_xmax = "2019-01-" + str(i+17) + "T18:00:00.000"
    
    xmin = parse(str_xmin )
    xmax = parse(str_xmax)
    plt.xlim(xmin, xmax) 

    # beautify the x-labels
    ax1.legend(bbox_to_anchor=(1.5, 1))
    #ax2.legend(loc="best")
    plt.gcf().autofmt_xdate()
    plt.savefig(img_path, bbox_inches = "tight", dpi = 300,transparent=True,papertype="a3")
    #plt.show()