from py4design import py3dmodel
import numpy as np
import csv

csv_filepath = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\model3d\\csv\\ColdTube_pointcloud1.csv"


x_list = []
y_list = []
f = open(csv_filepath)
'''
lines = f.readlines()
print len(lines)
for l in lines:
    print l
'''    

csv_reader = csv.reader(f, delimiter = ",")
#csv_list = list(csv_reader)
#creat the base vector 
base_edge = py3dmodel.construct.make_edge([0,0,0], [0,1,0])

pt_list = []
temp_list = []
cnt = 0
for r in csv_reader:
    if cnt%2 == 0:    
        yrot = float(r[1])
        xrot = float(r[0])
        dist = float(r[2])
        
        if dist < 400:
#            x = -1*dist*np.sin(np.deg2rad(yrot))*np.cos(np.deg2rad(xrot))
#            y = -1*dist*np.sin(np.deg2rad(yrot))*np.sin(np.deg2rad(xrot))
#            z = dist*np.cos(np.deg2rad(yrot))
#            pt = [x,y,z]
            
            edgex = py3dmodel.modify.rotate(base_edge, [0,0,0], [0,0,1], 360-xrot)
            if yrot < 0:
                edgey = py3dmodel.modify.rotate(edgex, [0,0,0], [1,0,0], 360 + yrot)
            else:    
                edgey = py3dmodel.modify.rotate(edgex, [0,0,0], [1,0,0], yrot)
            pypts = py3dmodel.fetch.points_frm_edge(py3dmodel.fetch.topo2topotype(edgey))
            pt2 = pypts[1]
            pt = py3dmodel.modify.move_pt([0,0,0], pt2, dist/100)
            
            v = py3dmodel.construct.make_vertex(pt)
            temp = r[3]
            if temp != "nan":
                pt_list.append(v)
                temp_list.append(float(temp))
        
        #print r
    cnt+=1
    
cmpd = py3dmodel.construct.make_compound(pt_list)
rot_cmpd = py3dmodel.modify.rotate(cmpd, [0,0,0], [1,0,0], 20)
v_list = py3dmodel.fetch.topo_explorer(rot_cmpd, "vertex")
occpt_list = py3dmodel.modify.occvertex_list_2_occpt_list(v_list)
pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpt_list)

c_list = []
for pt in pyptlist:
    c = py3dmodel.construct.make_polygon_circle(pt, [0,1,0], 0.05, division = 3)
    c_list.append(c)

#py3dmodel.utility.visualise([pt_list], ["BLACK"])
#py3dmodel.utility.visualise_falsecolour_topo(pt_list, temp_list)
dae_filepath = "F:\\kianwee_work\\princeton\\2019_01_to_2019_06\\coldtube\\model3d\\dae\\smartscan.dae"
py3dmodel.export_collada.write_2_collada_falsecolour(c_list, temp_list, "temp", dae_filepath)
    
'''
    if r[0] != "time" and r[0] != "Time":
        x = parse(r[0])
        if r[1].isalpha() == False:
            y = float(r[1])
        else:
            y =  r[1]

        x_list.append(x)
        y_list.append(y)
    
f.close()
return x_list, y_list, xmin, xmax
'''