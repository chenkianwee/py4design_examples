import matplotlib.pyplot as plt

from matplotlib.sankey import Sankey

fig = plt.figure()
ax = fig.add_subplot( xticks=[], yticks=[])
ax.axis("off")
sankey = Sankey(ax=ax, scale=0.01, offset=1, head_angle=90,
                format='%.0f', unit='%')

sankey.add(flows=[100, -26, -74],
            labels=['', 'Convection', 'Radiation'],
            orientations=[0, -1, 0],
            pathlengths=[1.5, 0.3, 2], 
            facecolor = "r",
            alpha = 0.3,
            rotation = 180)

diagrams = sankey.finish()

sankey_path = "F:\\kianwee_work\\princeton\\journal\\air2srf_conditioning\\img\\png\\conrad3.png"
plt.savefig(sankey_path, bbox_inches = "tight", dpi = 300, transparent=True, papertype="a3")