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
csv_path1 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_bestglobe_m2tadegc_15mins.csv"
csv_path2 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_predicted_mrt_15mins.csv"
csv_path3 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_environment_ct_ph23_dewpointt_15mins.csv"
csv_path4 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_bestglobe_m2vams_15mins.csv"

csv_path5 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_red_tank_tankt_15mins.csv"
csv_path6 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_blue_tank_tankt_15mins.csv"

csv_path7 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel3_surfacet_15mins.csv"
csv_path8 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel7_surfacet_15mins.csv"
csv_path9 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel2_surfacet_15mins.csv"
csv_path10 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel4_surfacet_15mins.csv"
csv_path11 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel6_surfacet_15mins.csv"
csv_path12 = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_data_15mins\\coldtube_panel8_surfacet_15mins.csv"

graph_dir = "F:\\kianwee_work\princeton\\2019_01_to_2019_06\\coldtube\\data\\graph\\png\\operative_temp"
title = "Operative Temperature"

index_s = 0
index_e = 9183
#=================================================================================================================================
#FUNCTIONS
#=================================================================================================================================
def calc_neutral_temp(to_av, vams):
    tn = 17.8 + (0.31*to_av)
    tcf_l_90 = tn - 2.5
    tcf_u_90 = tn + 2.5
    
    tcf_l_80 = tn - 3.5
    tcf_u_80 = tn + 3.5
    
    #calc cooling effect
    cooling_effect = calc_cooling_effect(vams)
    if to_av >= 12:
        tcf_u_90 = tcf_u_90 + cooling_effect
        tcf_u_80 = tcf_u_80 + cooling_effect
        
    return tn, tcf_l_90, tcf_u_90, tcf_l_80, tcf_u_80
    
def calc_cooling_effect(vams):
    cooling_effect = 0
    if 0.6 <= vams < 0.9:
        cooling_effect = 1.2
    elif 0.9 <= vams < 1.2:
        cooling_effect = 1.8
    elif vams >= 1.2:            
        cooling_effect = 2.2
        
    return cooling_effect

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
t_list1, v_list1, tmax, tmin = csv2plot(csv_path1, index = [index_s, index_e])
t_list2, v_list2, tmax, tmin = csv2plot(csv_path2, index = [index_s, index_e])
t_list3, v_list3, tmax, tmin = csv2plot(csv_path3, index = [index_s, index_e])
t_list4, v_list4, tmax, tmin = csv2plot(csv_path4, index = [index_s, index_e])
t_list5, v_list5, tmax, tmin = csv2plot(csv_path5, index = [index_s, index_e])
t_list6, v_list6, tmax, tmin = csv2plot(csv_path6, index = [index_s, index_e])
t_list7, v_list7, tmax, tmin = csv2plot(csv_path7, index = [index_s, index_e])
t_list8, v_list8, tmax, tmin = csv2plot(csv_path8, index = [index_s, index_e])
t_list9, v_list9, tmax, tmin = csv2plot(csv_path9, index = [index_s, index_e])
t_list10, v_list10, tmax, tmin = csv2plot(csv_path10, index = [index_s, index_e])
t_list11, v_list11, tmax, tmin = csv2plot(csv_path11, index = [index_s, index_e])
t_list12, v_list12, tmax, tmin = csv2plot(csv_path12, index = [index_s, index_e])

state_list = []
state80_list = []
state90_list = []
statehot_list = []

con_list = []
con_time_list = []
ta_list = []
tr_list = []
avg_panel_list = []
avg_tank_list = []
vams_list = []
to_list = []
time_list = []
dpt_list = []

to80_list = []
time80_list = []

to90_list = []
time90_list = []

tohot_list = []
timehot_list = []

tcf_l_90_list = []
tcf_u_90_list = []
tcf_l_80_list = [] 
tcf_u_80_list = []

t_p_diff_list = []
valid_time = []
valid_mea = []

avg_diff_temps = []
#=================================================================================================================================
#LOOP THROUGH ALL THE DATA
#=================================================================================================================================
for cnt in range(len(v_list1)):
    #CALC THE NEUTRAL TEMPERATURE AND THE 90% AND 80% SATISFACTION ZONE
    if 0<=cnt<=600:
        mean_mth_dbt = 27.48
    if 601<=cnt<=3480:
        mean_mth_dbt = 26.7
    if 3481<=cnt<=6456:
        mean_mth_dbt = 26.34
    if 6457<=cnt<=9181:
        mean_mth_dbt = 26.69
    
    vams = v_list4[cnt]
    if type(vams) != float:
        vams = 0.1

    tn, tcf_l_90, tcf_u_90, tcf_l_80, tcf_u_80 = calc_neutral_temp(mean_mth_dbt, vams)
    #CALC THE OPERATIVE TEMPERATURE 
    ta = v_list1[cnt]
    #best_tr = v_list10[cnt]
    #tr1 = v_list2[cnt]
    #tr2 = v_list3[cnt]
    tr = v_list16[cnt]
    
    to = "undefined"
    
    if type(tr) == float and type(ta) == float:
        to = (ta+tr)/2.0
#    if type(tr1) == float and type(tr2) == float and type(ta) == float:
#        tr = (tr1+tr2)/2.0
#        to = (ta+tr)/2.0
#    elif type(best_tr) == float and type(ta) == float:
#        tr = best_tr
#        to = (ta + best_tr)/2.0
    
    #=================================================================================================================================
    #GET ALL THE INFORMATION FROM THE CSVs
    #=================================================================================================================================
    panel2 = v_list11[cnt]
    panel3 = v_list7[cnt]
    panel4 = v_list12[cnt]
    panel6 = v_list13[cnt]
    panel7 = v_list8[cnt]
    panel8 = v_list14[cnt]
    avg_panel_temp = calc_avg_of_ls([panel2, panel3, panel4, panel6, panel7, panel8])
    
    tankt_red = v_list5[cnt]
    tankt_blue = v_list6[cnt]
    avg_tank_temp = calc_avg_of_ls([tankt_red, tankt_blue])
    
    dpt = v_list15[cnt]
    
    
    #=================================================================================================================================
    #MAKE SURE ALL THE INFO IS AVAILABLE
    #=================================================================================================================================
#    if type(to) == float and type(avg_panel_temp) == float and type(avg_tank_temp) == float and type(dpt) == float and dpt > 0:
    if type(to) == float and type(avg_tank_temp) == float and type(dpt) == float and dpt > 0:
        time = t_list1[cnt]
        #=================================================================================================================================
        #DEFINE THE OEPRATIONAL CONDITIONS
        #=================================================================================================================================
#        avg_panel_u_limit = avg_tank_temp+4
        tank_temp_l_limit = (-2 * (ta-dpt)) + dpt
#        tank_temp_u_limit = 30
        
#        t_dp_diff = dpt - tank_temp_l_limit
#        t_p_diff_list.append(t_dp_diff)
#        valid_mea.append(to)
#        valid_time.append(time)
        
#        avg_diff = avg_panel_temp - avg_tank_temp
#        avg_diff_temps.append(avg_diff)
#        if tank_temp_l_limit < avg_tank_temp <= tank_temp_u_limit:
#            if avg_panel_temp <= 35:
        
        tcf_l_90_list.append(tcf_l_90)
        tcf_u_90_list.append(tcf_u_90)
        tcf_l_80_list.append(tcf_l_80)
        tcf_u_80_list.append(tcf_u_80)
        time_list.append(time)
        ta_list.append(ta)
        tr_list.append(tr)
        dpt_list.append(dpt)
        if avg_tank_temp >= tank_temp_l_limit:
            toa = v_list9[cnt]
            #print ta, dpt, tank_temp_l_limit, avg_tank_temp, avg_panel_temp, time
    #        to_list.append(to)
    #        vams_list.append(vams)
    #        avg_panel_list.append(avg_panel_temp)
            
    #        avg_tank_list.append(avg_tank_temp)
    #        state = []
    #        if type(toa) == float and type(avg_panel_temp)==float:
    #            tod = ta - tr
    #            state = [to, ta, tr, avg_panel_temp, float(cnt)]
    #        
    #        state_list.append(state)
            
            if tcf_l_80 <= to <= tcf_u_80:
    #            state80_list.append(state)
                to80_list.append(to)
                time80_list.append(time)
                
                if tcf_l_90 <= to <= tcf_u_90:
    #                state90_list.append(state)
                    
                    del to80_list[-1]
                    to90_list.append(to)
                    
                    del time80_list[-1]
                    time90_list.append(time)
            else:
    #            statehot_list.append(state)
                tohot_list.append(to)
                timehot_list.append(time)
        else:            
            con_list.append(to)
            con_time_list.append(time)

#=================================================================================================================================
#END OF LOOP
#=================================================================================================================================
#print "AVG SUP PANEL TEMPS", sum(avg_diff_temps)/len(avg_diff_temps)
#print "TOTAL MEASUREMENTS", len(valid_mea)
nstates = len(to_list)            
#n80 = len(state80_list)
#n90 = len(state90_list)
#nhot = len(statehot_list)
#comfy_percent80 = n80/float(nstates)
#comfy_percent90 = n90/float(nstates)
#uncomfy_percent = nhot/float(nstates)

#print "TOTAL STATES", nstates, "S80", n80, "S90", n90, "STATEHOT", len(statehot_list)
#print "PERCENTAGE OF COMFORTABLE 90% SATISFACTION", comfy_percent90
#print "PERCENTAGE OF COMFORTABLE 80% SATISFACTION", comfy_percent80
#print "PERCENTAGE OF THERMALLY UNCOMFORTABLE", uncomfy_percent
#=================================================================================================================================
#THE FIRST AXIS
#=================================================================================================================================
#CONSTRUCT THE COMFORT ZONE
formatter = DateFormatter('%m-%d %H')
fig, ax1 = plt.subplots()

ax1.fill_between(time_list, tcf_l_80_list, tcf_u_80_list, facecolor='black', alpha=0.8, label = "80% Satisfaction Zone" )
ax1.fill_between(time_list, tcf_l_90_list, tcf_u_90_list, facecolor='grey', alpha = 0.5, label = "90% Satisfaction Zone")
ax1.scatter(timehot_list, tohot_list, c = "k", marker="x", alpha = 1, label = "Uncomfortable (measured)")
ax1.scatter(time80_list, to80_list, c = "silver", marker="s", alpha = 0.5, label = "80% Satisfied (measured)")
ax1.scatter(time90_list, to90_list, c = "k", marker="o", alpha = 0.8, label = "90% Satisfied (measured)")
ax1.scatter(con_time_list, con_list, c = "k", marker="*", alpha = 0.8, label = "Condensation")
ax1.plot(time_list, ta_list, 'k-', marker="^", label = "Air Temp")
ax1.plot(time_list, tr_list, 'k--', marker="", label = "MRT")
ax1.plot(time_list, dpt_list, 'k:', marker="", label = "Dewpoint")
#ax1.plot(time_list, ta_list, color = "silver", linestyle = "--", marker="^", alpha=0.5, label = "Air Temp")
#ax1.plot(time_list, avg_panel_list, color = "k", linestyle = "--", marker = "v", alpha=0.5, label = "Avg Panel Temp")
#ax1.plot(time_list, avg_tank_list, color = "k", linestyle = "-", alpha=0.5, label = "Avg Tank Temp")
#ax1.plot(time_list, dpt_list, color = "k", linestyle = "-.", alpha=0.5, label = "Dew Point Temp")
#ax1.scatter(valid_time, valid_mea, c = "k", marker="o", alpha=0.5, label = "Valid Measurements")

ax1.set_xlabel('Time (Month-Day Hour)', fontsize=10)
ax1.xaxis.set_major_formatter(formatter)

ax1.set_ylabel('Operative Temperature ($^oC$)', fontsize=10)
ymin = 22
ymax = 35
ax1.set_yticks(range(ymin,ymax+1,2))
ax1.set_ylim(ymin,ymax)
ax1.tick_params('y', colors='k')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3), fancybox=True, ncol=3)
#=================================================================================================================================
#THE SECOND AXIS
#=================================================================================================================================
#ax2 = ax1.twinx()
#ax2.plot(time_list, vams_list, color = "k", linestyle = ":", alpha=0.5, label = "Air Speed")
##ax2.scatter(x_list4, y_list4, c = 'r', marker = ".", label = "air_speed")
#ax2.set_ylim(0.0, 0.6)
#ax2.set_ylabel('Air Speed', color='k')
#ax2.tick_params('y', colors='k')
#ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.7), fancybox=True, ncol=3)
##fig.tight_layout()
#=================================================================================================================================
#THE GRAPH SETTINGS
#=================================================================================================================================
ax1.xaxis.set_major_formatter(formatter)

plt.gcf().autofmt_xdate()
plt.title(title, fontsize=10 )
#==============================================
#COMMENT OUT WHEN LOOP IS TURN ON
#==============================================
#str_xmin = "2018-11-09"
#str_xmax = "2019-01-31"
#    
#xmin = parse(str_xmin )
#xmax = parse(str_xmax)
#
#date_list = gen_dates4xaxis(xmin, xmax, 5)
#ax1.set_xticks(date_list)
#
#ax1.set_xlim(xmin, xmax)
#ax1.grid(axis = "y", linestyle = ":", alpha = 0.2, color = "k")
#
#graph_path = os.path.join(graph_dir, "coldtube_overall_data.png")
#plt.savefig(graph_path, bbox_inches = "tight", dpi = 300, transparent=False, papertype="a3")
#==============================================
#==============================================
for i in range(31): 
    str_xmin = "2019-01-" + str(i+1) + "T09:00"
    str_xmax = "2019-01-" + str(i+1) + "T18:00"
    
    xmin = parse(str_xmin )
    xmax = parse(str_xmax)
    date_list = gen_dates4xaxis(xmin, xmax, 6)
    ax1.set_xticks(date_list)
    ax1.set_xlim(xmin, xmax)
    ax1.grid(axis = "y", linestyle = ":", alpha = 0.1, color = "k")
    graph_path = os.path.join(graph_dir, "2019jan" + str(i+1) + ".png")
    plt.savefig(graph_path, bbox_inches = "tight", dpi = 300, transparent=False, papertype="a3")
#=================================================================================================================================
#STATS SUMMARY
#=================================================================================================================================
#nparms = 5
#state_list = rmv_empty_list(state_list, nparms)
#state80_list = rmv_empty_list(state80_list, nparms)
#state90_list = rmv_empty_list(state90_list, nparms)
#statehot_list = rmv_empty_list(statehot_list, nparms)
#
#stats_panel80 = calc_stats_state(state80_list, 3)
#stats_panel90 = calc_stats_state(state90_list, 3)
#stats_panelhot = calc_stats_state(statehot_list, 3)
#
#stats_air80 = calc_stats_state(state80_list, 1)
#stats_air90 = calc_stats_state(state90_list, 1)
#stats_airhot = calc_stats_state(statehot_list, 1)
#
#stats_rad80 = calc_stats_state(state80_list, 2)
#stats_rad90 = calc_stats_state(state90_list, 2)
#stats_radhot = calc_stats_state(statehot_list, 2)
#
#print "state80panel", stats_panel80, "state90panel", stats_panel90, "hotpanel", stats_panelhot
#print "state80air", stats_air80, "state90air", stats_air90, "hotair", stats_airhot
#print "state80rad", stats_rad80, "state90rad", stats_rad90, "hotrad", stats_radhot

#===========================================================================================================
#DRAW BAR GRAPH
#===========================================================================================================
#fig, ax1 = plt.subplots()
#
#positions1 = ["80%PanelT", "90%PanelT", "UncomfyPanelT"]
#means1 = [stats_panel80[0], stats_panel90[0], stats_panelhot[0]]
#std1 = [stats_panel80[-1], stats_panel90[-1], stats_panelhot[-1]]
#mx1 =[stats_panel80[2], stats_panel90[2], stats_panelhot[2]] 
#mn1 =[stats_panel80[3], stats_panel90[3], stats_panelhot[3]] 
#
#positions2 = ["80%AirT", "90%AirT", "UncomfyAirT"]
#means2 = [stats_air80[0], stats_air90[0], stats_airhot[0]]
#std2 = [stats_air80[-1], stats_air90[-1], stats_airhot[-1]]
#mx2 =[stats_air80[2], stats_air90[2], stats_airhot[2]] 
#mn2 =[stats_air80[3], stats_air90[3], stats_airhot[3]] 
#
#positions3 = ["80%MRT", "90%MRT", "UncomfyMRT"]
#means3 = [stats_rad80[0], stats_rad90[0], stats_radhot[0]]
#std3 = [stats_rad80[-1], stats_rad90[-1], stats_radhot[-1]]
#mx3 =[stats_rad80[2], stats_rad90[2], stats_radhot[2]] 
#mn3 =[stats_rad80[3], stats_rad90[3], stats_radhot[3]] 
#
#ax1.bar(positions1, means1, color="k", alpha = 0.5, yerr=std1, label = "Avg/Err Panel Temp of Comfort Zones")
#ax1.bar(positions2, means2, color="silver", alpha = 0.5, yerr=std2, label = "Avg/Err Air Temp of Comfort Zones")
#ax1.bar(positions3, means3, color="k", alpha = 0.3, yerr=std3, label = "Avg/Err MRT of Comfort Zones")
#
#mnmx_pos = positions1 + positions2 + positions3 + positions1 + positions2 + positions3
#mnmx = mx1 + mx2 + mx3 + mn1 + mn2+ mn3
#ax1.scatter(mnmx_pos, mnmx, c = "k", marker="^", alpha = 1, label = "Min & Max")
#
##ax1.set_xlabel('Thermal Comfort Zone', fontsize=10)
#plt.xticks(positions1 + positions2+positions3, rotation=45, ha = "right")
#
#ax1.set_ylabel('Temperature ($^oC$)', fontsize=10)
#ymin = 12
#ymax = 38
#ax1.set_yticks(range(ymin,ymax+1,2))
#ax1.set_ylim(ymin,ymax)
#ax1.tick_params('y', colors='k')
#ax1.grid(axis = "y", linestyle = ":", alpha = 0.2, color = "k")
#ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), fancybox=True, ncol=2)

#=================================================================================================================================
#THE PARALLEL COORDINATE PLOT
#=================================================================================================================================
#s80_colour_list = ["blue"]*len(state80_list)
#s80_tran_list =  [0.5]*len(state80_list)
#
#sh_colour_list = ["red"]*len(statehot_list)
#sh_tran_list =  [0.5]*len(statehot_list)
#
#n_state_list = state80_list + statehot_list #statehot_list  #state80_list  #state80_list + statehot_list
#colour_list =  s80_colour_list + sh_colour_list #sh_colour_list  #s80_colour_list #s80_colour_list + sh_colour_list
#transparency_list = s80_tran_list + sh_tran_list #sh_tran_list  #s80_tran_list  #s80_tran_list + sh_tran_list
#
##print len(n_state_list), len(colour_list), len(transparency_list) 
#pyoptimise.draw_graph.parallel_coordinates(n_state_list, ["to", "ta", "tr", "panel_t", "cnt"], style = colour_list,  transparency = transparency_list)