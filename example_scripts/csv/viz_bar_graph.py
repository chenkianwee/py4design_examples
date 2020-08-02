import matplotlib.pyplot as plt
#===========================================================================================================
#INPUTS
#===========================================================================================================
positions = ["BaseCase", "Decentralised\nPanels", "Centralised\nPanels", "Decentralised\nAir", "Centralised\nAir"]
values = [300, 911.769829144, 605.884914572, 3473.31317802, 1736.65658901]
#std1 = [stats_panel80[-1], stats_panel90[-1], stats_panelhot[-1]]
#mx1 =[stats_panel80[2], stats_panel90[2], stats_panelhot[2]] 
#mn1 =[stats_panel80[3], stats_panel90[3], stats_panelhot[3]] 

res_filepath = "F:\\kianwee_work\\princeton\\journal\\air2srf_conditioning\\img\\png\\energy_con.png"
#===========================================================================================================
#DRAW BAR GRAPH
#===========================================================================================================
fig, ax1 = plt.subplots()

ax1.bar(positions, values, color="silver", alpha = 1.0)
#ax1.bar(positions2, means2, color="silver", alpha = 0.5, yerr=std2, label = "Avg/Err Air Temp of Comfort Zones")
#ax1.bar(positions3, means3, color="k", alpha = 0.3, yerr=std3, label = "Avg/Err MRT of Comfort Zones")

#mnmx_pos = positions1 + positions2 + positions3 + positions1 + positions2 + positions3
#mnmx = mx1 + mx2 + mx3 + mn1 + mn2+ mn3
#ax1.scatter(mnmx_pos, mnmx, c = "k", marker="^", alpha = 1, label = "Min & Max")

plt.xticks(positions, rotation=45, ha = "right")

ax1.set_ylabel('Energy Consumption (W)', fontsize=10)
#ymin = 12
#ymax = 38
ax1.set_yticks(range(300,3601,300))
#ax1.set_ylim(ymin,ymax)
ax1.tick_params('y', colors='k')
ax1.grid(axis = "y", linestyle = ":", alpha = 0.2, color = "k")
#ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), fancybox=True, ncol=2)

# plt.savefig(res_filepath, bbox_inches = "tight" , dpi = 300, transparent=True,papertype="a3")