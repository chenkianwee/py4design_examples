import os
import csv
from dateutil.parser import parse
from datetime import timedelta

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from py4design import pyoptimise, utility
#=================================================================================================================================
#INPUTS
#=================================================================================================================================

csv_path = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_1mins\\coldtube_panel2_supplyt_1mins.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_1mins\\coldtube_panel2_returnt_1mins.csv"

#graph_dir = "F:\\kianwee_work\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png\\adaptive_comfort\\2019_01"
graph_dir = "F:\\kianwee_work\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png"
#title = "Operative, Air, Tank and Panel Temperature v.s. Air Speed"
title = "Operative Temperature"

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

def gen_dates4xaxis(start_date, end_date, nintervals):
    date_range = end_date - start_date
    interval = date_range/nintervals
    date_list = []
    for i in range(nintervals):
        new_date = start_date + (interval *i)
        date_list.append(new_date)
    
    date_list.append(end_date)
    return date_list

def rmv_empty_list(list_2d, nparms):
    n_state_list = []
    for s in list_2d:
        if len(s) == nparms:
            n_state_list.append(s)
    return n_state_list

def cnt2time(list_2d):
    time_list = []      
    for s in list_2d:
        cnt = int(s[-1])
        time = t_list1[cnt]
        time_list.append(time)
        
    return time_list

def calc_avg_of_ls(ls):
    cleaned = [ x for x in ls if type(x) == int or type(x) == float]
    if cleaned:
        avg = sum(cleaned)/float(len(cleaned))
    else:
        avg = "undefined"
        
    return avg

def calc_stats_state(state_list, index):
    slist = []
    for state in state_list:
        s = state[index]
        slist.append(s)
        
    avg = sum(slist)/float(len(slist))
    median = utility.findmedian(slist)
    mx = max(slist)
    mn = min(slist)
    std = np.std(slist)
    
    return [round(avg,2), round(median,2), round(mx,2), round(mn,2), round(std,2)]
#=================================================================================================================================
#MAIN
#=================================================================================================================================
t_list1, v_list1, tmax, tmin = csv2plot(csv_path, index = [index_s, index_e])
t_list2, v_list2, tmax, tmin = csv2plot(csv_path2, index = [index_s, index_e])

water_density = 997 #kg/m3
spec_heat_water = 4200 #j/kgc

vol_per_panel = 0.1 #l/s
vol_15 = vol_per_panel*15*60
mass = vol_15*3 

panel_area = 1.25*2.48

hr_list = []
for cnt in range(len(v_list2)):
    sup = v_list1[cnt]
    ret = v_list2[cnt]
    if sup != "undefined" and ret != "undefined":
        diff = float(ret)-float(sup)
        if diff < 0:
            diff = 0
        heat_removed = 0.1*spec_heat_water*(diff)
        watts = heat_removed
        watts_m2 = watts/panel_area
        print sup, ret
        print diff
        print watts, "WATTS"
        hr_list.append(watts_m2)

#print hr_list