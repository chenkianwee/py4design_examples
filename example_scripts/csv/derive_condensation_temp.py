import csv 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

condensation_filepath = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\data\\csv\\coldtube_condensation.csv"
res_filepath = "F:\\kianwee_work\\princeton\\journal\\air2srf_conditioning\\img\\png\\coldtube_condensation.png"

f = open(condensation_filepath, "r")
reader = csv.reader(f)
water_list = [0]
air_list = [[0]]
cnt = 0
for r in reader:
    if cnt !=0:
        air_temp = float(r[0])
        dew_pt = float(r[1])
        water_temp = float(r[2])
        air_sep = air_temp - dew_pt
        air_list.append([air_sep])
        water_sep = dew_pt - water_temp
        water_list.append(water_sep)
    cnt+=1

#=================================================================================
#THE LINEAR REGRESSION MODEL
#=================================================================================
lr = LinearRegression(fit_intercept=False)
lr.fit(air_list, water_list)  # x needs to be 2d for LinearRegression

score = lr.score(air_list, water_list)
co = lr.coef_
intercept = lr.intercept_

print "Rsquare SCORE", score, "COEEFF", co, "INTERCEPT", intercept
#=================================================================================
#PLOTTING
#=================================================================================
fig = plt.figure()
#plt.plot(other_panel_t, mrt_predicts, 'r.', markersize=5)
plt.ylim(0,18)
plt.xlim(0,8)
plt.plot(air_list, water_list, 'kx', markersize=5)
plt.plot(air_list, lr.predict(air_list), 'k-')
plt.ylabel('Dew Point - Chilled Water ($^oC$)', color='k')
plt.xlabel('Air Temp - Dew Point ($^oC$)', color='k')
#plt.show()
plt.annotate("$R^2$ = " + str(round(score, 2)), (4,14))
plt.savefig(res_filepath, bbox_inches = "tight" , dpi = 300, transparent=True, papertype="a1")