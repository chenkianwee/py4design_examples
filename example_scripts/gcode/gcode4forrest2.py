import numpy as np
rx = np.arange(-10,10.1,0.2)
ry = np.arange(-10,10.1,0.2)

strx = ""

for x in rx:
    print x
    for y in ry:
        strx = strx + "g1 X" + str(round(x,1)) + " Y" + str(round(y,1)) + "\n"
        #print strx

f = open("C:\\Users\\chaosadmin\\Desktop\\gcode4forrest_0.2_10_10.txt", "w")
f.write(strx)
f.close()