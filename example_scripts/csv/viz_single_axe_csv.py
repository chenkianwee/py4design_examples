import os
import csv
from dateutil.parser import parse
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

#formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
formatter = DateFormatter('%m-%d %H:%M')

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\\coldtube_data_15mins\\coldtube_bestglobe_m2tadegc_15mins.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_predicted_mrt_15mins.csv"

title = "MRT vs Air Temp"
graph_dir = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png\\air_vs_mrt"

ymin = 20
ymax = 35
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
x_list2, y_list2 = rmv_non_numeric(x_list2, y_list2)

#z_list = []
#z_list.append(y_list2)
#z_list.append(y_list3)
#zipped_z = zip(*z_list)
#
#cmrt_list = []
#new_x_list2 = []
#zcnt=0
#for z in zipped_z:
#    avg_mrt = avg_mixed_list(z)
#    if type(avg_mrt) == float:
#        cmrt_list.append(avg_mrt)
#        new_x_list2.append(x_list2[zcnt])
#    zcnt+=1

#=================================================================================================================================
#PLOT THE DATA
#=================================================================================================================================
'''
#for colour reference refer to page https://matplotlib.org/examples/color/named_colors.html
#for marker reference refer to page https://matplotlib.org/api/markers_api.html#module-matplotlib.markers
'''

#plt.scatter(new_x_list1, cmrt_list, c = "b", marker=".", label="cube_mrt_avg")
#plt.scatter(x_list2, y_list2, c = "b", marker="s", label="1086")
#plt.scatter(x_list9, y_list9, c = "r", marker=".", label="best_globe1_mrt")

plt.plot([26,17,13], [89.8,131,156.8], 'k-', marker="x", label = "Air Temp")
#plt.plot(x_list2, y_list2, 'k--', marker="", label = "MRT")


#plt.title(title, fontsize=10 )
#plt.xlabel('Date (Mth-Day Hour)', fontsize=10)
#plt.ylabel('Temp ($^oC$)', fontsize=10)
#plt.ylim(ymin,ymax)

plt.legend(bbox_to_anchor=(1.5, 1))
#str_xmin = "2019-01-" + str(23) + "T09:00:00.000"
#str_xmax = "2019-01-" + str(23) + "T18:00:00.000"
#xmin = parse(str_xmin)
#xmax = parse(str_xmax)
#plt.xlim(xmin, xmax) 
#plt.gcf().autofmt_xdate()

graph_filepath = os.path.join(graph_dir, title +".png")
#plt.savefig(graph_filepath, bbox_inches = "tight" , dpi = 300, transparent=True,papertype="a3")
plt.show()

#for i in range(31):    
#    filename = "air_temp_vs_mrt_" + str(i+1) + ".png"
#    img_filepath = os.path.join(graph_dir, filename)
#    
#    str_xmin = "2019-01-" + str(i+1) + "T09:00:00.000"
#    str_xmax = "2019-01-" + str(i+1) + "T18:00:00.000"
#    xmin = parse(str_xmin)
#    xmax = parse(str_xmax)
#    plt.xlim(xmin, xmax) 
#    
#    #legend
#    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3), fancybox=True, ncol=2)
#    
#    # beautify the x-labels
#    plt.gcf().autofmt_xdate()
#    
#    #plt.savefig(img_filepath, bbox_inches = "tight" , dpi = 300, transparent=True,papertype="a3")
#    #plt.show()
