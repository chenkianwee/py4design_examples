import os
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

import csv
from dateutil.parser import parse
#=================================================================================================================================
#INPUTS
#=================================================================================================================================
csv_path1 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_mrt_ct_ph25_mrt_avg_corrected_15mins.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_mrt_ct_ph26_mrt_avg_corrected_15mins.csv"

csv_path3 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel2_surfacet_15mins.csv"
csv_path4 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel3_surfacet_15mins.csv"
csv_path5 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel4_surfacet_15mins.csv"
csv_path6 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel6_surfacet_15mins.csv"
csv_path7 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel7_surfacet_15mins.csv"
csv_path8 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel8_surfacet_15mins.csv"

csv_path9 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_red_tank_tankt_15mins.csv"
csv_path10 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_blue_tank_tankt_15mins.csv"

res_dir = "F:\\kianwee_work\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins"
filename = "coldtube_predicted_mrt_15mins.csv"

index_s = 0
index_e = 9183
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
        csv_list = csv_list[index[0]:index[1]]
    xmin = parse(csv_list[1][0])
    xmax = parse(csv_list[-1][0])
    for r in csv_list:
        if r[0] != "time" and r[0] != "Time":
            x = parse(r[0])
            if r[1].isalpha() == False:
                y = float(r[1])
            else:
                y =  r[1]
    
            x_list.append(x)
            y_list.append(y)
        
    f.close()
    return x_list, y_list, xmin, xmax

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

def calc_avg_of_ls(ls):
    cleaned = [ x for x in ls if type(x) == int or type(x) == float]
    if cleaned:
        avg = sum(cleaned)/float(len(cleaned))
    else:
        avg = "undefined"
        
    return avg

def ls2dict(keyls, valuels):
    d = {}
    for i in range(len(keyls)):
        key = keyls[i]
        v  = valuels[i]
        d[key] = v
    
    return d
#=================================================================================================================================
#MAIN
#=================================================================================================================================
t_list1, v_list1, tmax, tmin = csv2plot(csv_path1, index = [index_s, index_e])
t_list2, v_list2, tmax, tmin = csv2plot(csv_path2, index = [index_s, index_e])
t_list3, v_list3, tmax, tmin = csv2plot(csv_path3, index = [index_s, index_e])
t_list4, v_list4, tmax, tmin = csv2plot(csv_path4, index = [index_s, index_e])
t_list5, v_list5, tmax, tmin = csv2plot(csv_path5, index = [index_s, index_e])
t_list6, v_list6, tmax, tmin = csv2plot(csv_path6, index = [index_s, index_e])
t_list7, v_list7, tmax, tmin = csv2plot(csv_path7, index = [index_s, index_e])
t_list8, v_list8, tmax, tmin = csv2plot(csv_path8, index = [index_s, index_e])
#t_list9, v_list9, tmax, tmin = csv2plot(csv_path9, index = [index_s, index_e])
#t_list10, v_list10, tmax, tmin = csv2plot(csv_path10, index = [index_s, index_e])

x = []
y = []
time_list1 = []
time_list2 = []
time_list3 = []
all_panel_t = []
other_panel_t = []

null_list = []

for i in range(len(t_list1)):
    mrt1 = v_list1[i]
    mrt2 = v_list2[i]
    if type(mrt1) == float and type(mrt2) == float:
        mrt = (mrt1+mrt2)/2.0
    else:
        mrt = "undefined"
        
    time = t_list1[i]
    
    panel2_t = v_list3[i]
    panel3_t = v_list4[i]
    panel4_t = v_list5[i]
    panel6_t = v_list6[i]
    panel7_t = v_list7[i]
    panel8_t = v_list8[i]
    avg_panel_t = calc_avg_of_ls([panel2_t, panel3_t, panel4_t, panel6_t, panel7_t, panel8_t])
    
#    red_tankt = v_list9[i]
#    blue_tankt = v_list10[i]
#    avg_tank_t = calc_avg_of_ls([red_tankt, blue_tankt])
    
    parmx = avg_panel_t
    parmy = mrt
    
    if type(parmx) == float and parmx>0 and type(parmy) == float:
        x.append([parmx])
        y.append(parmy)
        time_list1.append(time)
    
    elif type(parmx) == float and parmx>0:
        time_list2.append(time)
        other_panel_t.append([parmx])
        
    else:
        time_list3.append(time)
        null_list.append("undefined")
    
#=================================================================================
#THE LINEAR REGRESSION MODEL
#=================================================================================
# Split X and y into X_
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)

lr = LinearRegression()
lr.fit(x_train, y_train)  # x needs to be 2d for LinearRegression

#=================================================================================
#TEST THE ACCURACY OF OUR MODEL WITH THE TEST MODEL
#=================================================================================
from sklearn.metrics import mean_squared_error, r2_score
import math

y_predict = lr.predict(x_test)
regression_model_mse = mean_squared_error(y_test, y_predict)
variance_score = r2_score(y_test, y_predict )
error = math.sqrt(regression_model_mse)

score = lr.score(x_train, y_train)
co = lr.coef_
intercept = lr.intercept_

print "Rsquare SCORE", score, "COEEFF", co, "INTERCEPT", intercept, "MEAN SQUARE ERROR", regression_model_mse,"ERROR", error, "VARIANCE", variance_score

#=================================================================================
#PREDICT AND CONSTRUCT NEW SET OF MRT VALUES FOR ALL THE PERIODS
#=================================================================================
mrt_predicts = lr.predict(other_panel_t)
d1 = ls2dict(time_list1, y)
d2 = ls2dict(time_list2, list(mrt_predicts))
d3 = ls2dict(time_list3, null_list)
d4 = d1.copy()
d4.update(d2)
d4.update(d3)

sorted_keys = sorted(d4.keys())
print len(sorted_keys)

strx = "time,value\n"
for k in sorted_keys:
    v = d4[k]
    date_str = k.strftime("%Y-%m-%dT%H:%M:%S.000")
    strx = strx + date_str + "," + str(v) + "\n"

filepath = os.path.join(res_dir, filename)
f = open(filepath, "w+")
f.write(strx)
f.close()

#=================================================================================
#PLOTTING
#=================================================================================
fig = plt.figure()
#plt.plot(other_panel_t, mrt_predicts, 'r.', markersize=5)
plt.plot(x, y, 'r.', markersize=5)
plt.plot(x_train, lr.predict(x_train), 'b-')
plt.ylabel('MRT', color='k')
plt.xlabel('Avg Panel Temp', color='k')
plt.show()
