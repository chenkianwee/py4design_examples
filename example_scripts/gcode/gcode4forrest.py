import numpy as np
rx = np.arange(0,360.1,0.2)
ry = np.arange(-90,90.1,0.2)

strx = ""

for x in rx:
    for y in ry:
        strx = strx + "g1 X" + str(x) + " Y" + str(y) + "\n"

f = open("C:\\Users\\chaosadmin\\Desktop\\gcode4forrest_0.2.txt", "w")
f.write(strx)
f.close()
