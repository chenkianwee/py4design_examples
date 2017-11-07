import os
import time
from pyliburo import urbanformeval, py3dmodel
import read_collada_4_evalurbanform as read_collada

#========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "dae", "example1.dae")

display2dlist = []
colourlist = []
#==================================================================================================
#read and sort collada file
#==================================================================================================
print "READING COLLADA ..."
time1 = time.clock()

solid_list, opengeom_shells, opengeom_faces, edges = read_collada.read_collada(dae_file)
#find the boundary face, for this example we assume the boundary face is the one with the biggest area
farea_list = []
for f in opengeom_faces:
    farea = py3dmodel.calculate.face_area(f)
    farea_list.append(farea)
    
mfarea = max(farea_list)
mfarea_index = farea_list.index(mfarea)
boundary = opengeom_faces[mfarea_index]
opengeom_faces.pop(mfarea_index) 
time2 = time.clock()
tt1 = time2-time1
print "TIME TAKEN 4 COLLADA:", tt1/60.0
#py3dmodel.utility.visualise([edges, opengeom_faces, [boundary]],["BLACK", "WHITE", "GREEN"])
#==================================================================================================
#calculate RDI
#==================================================================================================
print "CALCULATING RDI ..."
time3 = time.clock()

    
rdi_res_dict = urbanformeval.route_directness(edges, opengeom_faces, boundary, rdi_threshold = 0.6)

time4 = time.clock()
tt2 = time4-time3

print "AVG RDI:", rdi_res_dict["average"]
print "RDI:", rdi_res_dict["percent"]
print "TIME TAKEN2 4 RDI:", tt2/60.0

#VISUALISE
display2dlist.append(rdi_res_dict["network_edges"] + rdi_res_dict["peripheral_points"])
colourlist.append("BLUE")
py3dmodel.utility.visualise_falsecolour_topo(rdi_res_dict["plots"], rdi_res_dict["rdi_list"], other_occtopo_2dlist = display2dlist, 
                                             other_colour_list = colourlist)
