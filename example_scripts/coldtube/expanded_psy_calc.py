import math

import matplotlib.pyplot as plt
import numpy as np
import calc_panel_view as vf

from py4design import py3dmodel
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

# def calc_mrt_from_qrad(qrad, tskin):
#     e = 0.95
#     s_boltzman = 5.67e-08
#     tmrt4 = qrad/(e*s_boltzman)
#     print(tmrt4)
#     tmrt4 = tmrt4 - ((tskin+273.15)**4)

#     print(tmrt4)
#     tmrt = math.sqrt(tmrt4)
#     return tmrt

def calc_conv_xchange(tskin, tair, vair):
    hcfree = 0.78*((tskin-tair)**0.56)
    # hcforce = 10.4*(vair**0.56)
    hc = hcfree
    qcon = hc*(tskin-tair)
    return qcon
        
#==================================================================
#radiant
#==================================================================
ndir = 1000
xdim = 1.25
ydim = 2.48
otemp = 30

dirs, non_dirs = vf.gen_angle_dir(ndir, 180, (0,1,0))

rec = py3dmodel.construct.make_rectangle(xdim,ydim)
rec = py3dmodel.modify.rotate(rec, (0,0,0), (1,0,0),90)
rec = py3dmodel.fetch.topo2topotype(rec)

# strx = "waterT,Qrad,Qcon,MRT,Distance,SkinT,flux,PanelT,vf,calcMRT\n"
strx = ""
dist = 0.8
for i in range(3):
    total_flux = flux80[i]
    tskin = skin80[i]
    tmrt = mrt80[i]
    ptemp = panel80[i]
    water = water80[i]
    
    avg_temp, view_factor, hit_edges, non_hits = vf.calc_view(dist, rec, dirs, ptemp, otemp)
    
    qrad = calc_radiant_xchange(tskin, tmrt)
    qrad = qrad/0.5
    
    qcon = total_flux - qrad
    
    # strx+= str(water) + "," + str(qrad) + "," + str(qcon) + "," + str(tmrt) + "," + str(dist) + "," + str(tskin) + "," + str(total_flux) + "," +\
    #     str(ptemp) + "," + str(view_factor) + "," + str(avg_temp) + "\n" 
        
    #py3dmodel.utility.visualise([[rec], hit_edges, non_hits], ["WHITE", "BLUE", "BLACK"])
    print("QRAD", qrad, "QCON", qcon, "MRT", tmrt, "Calc MRT", avg_temp, "panel temp", ptemp , "view factor", view_factor)
    # print("WaterT", water, "QRAD", qrad, "QCON", qcon, "MRT", tmrt, "DIST", dist, "view factor", view_factor)

flux_list = ["91.8","134.5","142.8"]

water80l = list(water80)
skin80l = list(skin80)
panel80 = list(panel80)
air80 = list(air80)

plt.scatter(flux_list, water80l, color = "k", marker="+", label = "Water Temp")
plt.scatter(flux_list, panel80,color = "k", marker="x", label = "Panel Temp")
plt.scatter(flux_list, air80,color = "k", marker="^", label = "Air Temp")
plt.scatter(flux_list, skin80l,color = "k", marker="o", label = "Skin Temp")
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, ncol=4)
plt.xlabel('Heat Flux (W/$m^2$)', fontsize=10)
plt.ylabel('Temp ($^oC$)', fontsize=10)

graph_path = "F:\\kianwee_work\\princeton\\journal\\air2srf_conditioning\\img\\png\\flux.png"
plt.savefig(graph_path, bbox_inches = "tight" , dpi = 300, transparent=True,papertype="a3")


# f.write(strx)
# f.close()