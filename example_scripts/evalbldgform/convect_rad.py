import numpy as np 

air_speed = 0.2
air_temp_c = 31
dewpt_temp_c = 25

#calc the cooling provided by the fan
hc = 10.4*(air_speed**0.56)
tskin = 0.3182*air_temp_c + 22.406
convective_cooling_rate = hc*(tskin-air_temp_c)

#the skin area of a single person 
#ADubois = 0.202 x person weight**0.425 x person height **0.725
occ_skin_area = 0.202*(73**0.425)*(1.65**0.725)

#cooling from evaporation 
w = 0.06 #skin wettedness
he = 16.5*hc

p_sat_skin = np.power(2.718,(77.3450+0.0057*(tskin+273.15)-7235/(tskin+273.15)))/(np.power((tskin+273.15),8.2))/1000
rh = (100 - (5*(air_temp_c-dewpt_temp_c)))/100
#rh = 0.8
p_sat_air = np.power(2.718,(77.3450+0.0057*(air_temp_c+273.15)-7235/(air_temp_c+273.15)))/(np.power((air_temp_c+273.15),8.2))/1000*rh
qev = w*he*(p_sat_skin - p_sat_air)
#eva_capacity = qev*occ_skin_area

print(convective_cooling_rate)
print(qev)