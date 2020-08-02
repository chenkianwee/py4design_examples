import math

import matplotlib.pyplot as plt
import numpy as np
#==================================================================
#flux data 
#==================================================================
skin50 = np.array([34.08952381, 33.41611111, 32.85295238])
air50 = np.array([31.3, 30.33666667, 30])
globe50 = np.array([31.2, 29.9, 29.27])
mrt50 = np.array([29, 25.44367006, 23.58398661])
panel50 = np.array([27.090011, 19.02333, 14.80332867])
water50 = np.array([26.95, 16.75, 12.15])
flux50 = np.array([89.82496704, 130.9758092, 156.8276265])

skin80 = np.array([34.07804762, 33.31042857, 32.92484127])
air80 = np.array([31.3, 30.29666667, 29.94666667])
globe80 = np.array([31.2, 29.79666667, 29.22333333])
mrt80 = np.array([30, 28.77186394, 27.41242194])
panel80 = np.array([26.22999, 18.76999367, 14.80332867])
water80 = np.array([26.1, 16.3, 11.8])
flux80 = np.array([91.84464027, 134.5354832, 142.8413894])

#==================================================================
#constant
#==================================================================
e = 0.95
s_boltzman = 5.67e-08
arad = 0.7 
#==================================================================
#function
#==================================================================
def calc_radiant_xchange(tskin, tmrt):
    e = 0.95
    s_boltzman = 5.67e-08
    a1 = (273.15+((tskin + tmrt)/2))**3
    hr = 4*e*s_boltzman*a1
    qrad = hr * e * (tskin-tmrt)
    return qrad

def calc_mrt_from_qrad(qrad, tskin):
    e = 0.95
    s_boltzman = 5.67e-08
    tmrt4 = qrad/(e*s_boltzman)
    tmrt4 = tmrt4 - ((tskin+273.15)**4)

    tmrt = math.sqrt(tmrt4)
    return tmrt

def calc_conv_xchange(tskin, tair, vams, rh):
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

    return total_con

#==================================================================
#calc convection and radiant
#==================================================================
vams = 0.19
rh = 72.5

qcons = []
qrads = []
for i in range(3):
    tskin = skin50[i]
    tair = air50[i]
    tmrt = mrt50[i]
    tpanel = panel50[i]
    twater = water50[i]
    total_flux = flux50[i]
    
    qcon = calc_conv_xchange(tskin, tair, vams, rh)
    con_percent = qcon/total_flux * 100
    qcons.append(con_percent)
    
    qrad = total_flux - qcon
    rad_percent = qrad/total_flux * 100
    qrads.append(rad_percent)

print(qrads, qcons)

#=================================================================================================================================
#THE FIRST AXIS
#=================================================================================================================================
fig, ax1 = plt.subplots()
width = 0.3
flux50 = np.array([89.82496704, 130.9758092, 156.8276265])

scenarios = ["89.8W/$m^2$", "131.0W/$m^2$", "156.8W/$m^2$"]

water80 = list(water50)
skin80 = list(skin50)
panel80 = list(panel50)
air80 = list(air50)

ms = 8
ax1.plot(scenarios, water80, color = "k", marker="2", ms = 12, label = "Water Temp")
ax1.plot(scenarios, panel80, color = "k", marker="x", ms = ms, label = "Panel Temp")
ax1.plot(scenarios, air80, color = "k", marker="^", ms = ms, label = "Air Temp")
ax1.plot(scenarios, skin80, color = "k", marker="o", ms = ms, label = "Skin Temp")

ax1.yaxis.set_ticks(np.arange(10,36,2.5))
ax1.set_ylim(10,35)
ax1.grid(axis = "y", linestyle = ":", alpha = 0.2, color = "k")
ax1.set_ylabel('Temperature ($^oC$)', fontsize=10, color = 'k', alpha = 1)

#=================================================================================================================================
#THE SECOND AXIS
#=================================================================================================================================
ax2 = ax1.twinx()

ax2.bar(scenarios, qcons, width, color="k", alpha = 0.3, label = "Convective %")
ax2.bar(scenarios, qrads, width, bottom = qcons, color="k", alpha = 0.6, label = "Radiative %")
ax2.set_xlabel('Heat Flux (W/$m^2$)', fontsize=10, color = 'k')

ax2.yaxis.set_ticks(range(0,105,10))
ax2.set_ylim(0,100)
# Make the y-axis label, ticks and tick labels match the line color.
ax2.set_ylabel('Convective/Radiative\n Exchange (%)', labelpad = -5, fontsize=10, color = 'k', alpha = 0.6)
ax2.tick_params('y', colors='grey')

ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), fancybox=True, ncol=4)
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), fancybox=True, ncol=4)

fig.tight_layout()

graph_path = "F:\\kianwee_work\\princeton\\journal\\air2srf_conditioning\\img\\png\\flux.png"
plt.savefig(graph_path, bbox_inches = "tight" , dpi = 300, transparent=True,papertype="a3")