vams = 0.19
rh = 72.5
tair = 30.3
# tskin = 0.3182*tair + 22.406
tskin = 33.3
t_delta = tskin-tair

hc_force = 10.4 * (vams**0.56)
hc_free = 0.78 * (t_delta**0.56)

qcon_force = hc_force * t_delta
qcon_free = hc_free * t_delta

w = 0.12
he_force = 16.5*hc_force
he_free = 16.5* hc_free

pskin1 = 77.3450 + (0.0057 * (tskin+273.15)) - (7235/(tskin+273.15))
pskin_sat = ((2.718**pskin1)/(tskin+273.15)**8.2) * 0.001

pair1 = 77.3450 + (0.0057 * (tair+273.15)) - (7235/(tair+273.15))
pair = ((2.718**pair1)/(tair+273.15)**8.2) * 0.001 * 72.5 * 0.01
pdiff = pskin_sat - pair

qev_force = w * he_force * pdiff
qev_free = w * he_free * pdiff
total_con = qcon_force + qcon_free + qev_force + qev_free 

emissivity = 0.98
boltzman = 5.670367*10**-8

ar_ad = 1

panels = [26.22999, 18.76999367, 14.80332867]

tmrt = panels[2]
td = tskin-tmrt
td4 = (tskin+273.15)**4-(tmrt+273.15)**4

temp3 = (273.15 + ((tskin+tmrt)/2))**3
hr = 4*emissivity*boltzman*ar_ad*temp3
qrad = emissivity*boltzman*td4
print(qrad)
print(qrad + total_con)