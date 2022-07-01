from ladybug.epw import EPW
from py4design import utility
import numpy as np

epw_data = EPW('F:\\kianwee_work\\digital_repository\\energyplus_share\\weatherfile\\SGP_Singapore.486980_IWEC.epw')

wind_speed = epw_data.wind_speed
ws_list = list(wind_speed)
print sum(ws_list)/float(len(ws_list))

dbt = epw_data.dry_bulb_temperature
print dbt.average_monthly()
for d in dbt.average_monthly():
    print d
dbt_list = list(dbt)

avg_dbt = sum(dbt_list)/float(len(dbt_list))
print round(avg_dbt)

dewpt = epw_data.dew_point_temperature
dewpt_list = list(dewpt)

diff_list = []
for cnt in range(8760):
    dew = dewpt_list[cnt]
    dry = dbt_list[cnt]
    diff = dry-dew
    diff_list.append(diff)
    
print sum(diff_list)/len(diff_list)
print np.percentile(diff_list, [10,20,30,40,50,60,70,80,90,100])
'''
mx_dbt = max(dbt_list)
mn_dbt = min(dbt_list)
mx_dbt_index = dbt_list.index(mx_dbt)

cnt_list = []
dcnt = 0
for dbt in dbt_list:
    if 30 <= dbt:
        cnt_list.append(dcnt)
    dcnt+=1
    


avg_dpt_list = []
for c in cnt_list:
    d = dewpt_list[c]
    avg_dpt_list.append(d)
    
print len(cnt_list)/8760.0

dcnt = 0
dcnt_list = []
for d in dewpt_list:
    if 26 <= d <=28:
        dcnt_list.append(dcnt)
    dcnt+=1
    
high_dbt_list = []
for c in dcnt_list:
    high_dbt_list.append(dbt_list[c])
    
print dbt_list[1121], dewpt_list[1121]
print np.percentile(high_dbt_list, [10,20,30,40,50,60,70,80,90,100])
#print "avg dew pt", sum(avg_dpt_list)/float(len(avg_dpt_list))
#print np.percentile(dbt_list, [10,20,30,40,50,60,70,80,90,100])
#print np.percentile(avg_dpt_list, [10,20,30,40,50,60,70,80,90,100])

#mth_dewpt =  dewpt.average_monthly()
#mth_dewpt =  list(mth_dewpt)
avg_dewpt = sum(dewpt_list)/float(len(dewpt_list))
median = utility.findmedian(dewpt_list)

mx_dewpt = max(dewpt_list)
mn_dewpt = min(dewpt_list)
mx_dewpt_index = dewpt_list.index(mx_dewpt)
mx_dewpt_dbt = dewpt_list[mx_dewpt_index]
mx_dbt_dewpt = dewpt_list[mx_dbt_index]
print avg_dewpt

#calc the lowest supply temperature
sup_temp_lwr_limit = (-2 * (33.8-23.9)) + 23.9
#print sup_temp_lwr_limit
'''