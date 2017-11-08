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
dae_file = os.path.join(parent_path, "example_files", "dae", "example1_1.dae")

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
#calculate FAI
#==================================================================================================
print "CALCULATING FAI ..."
time5 = time.clock()

res_dict = urbanformeval.frontal_area_index(solid_list, boundary, (1,1,0), xdim = 100, ydim = 100)
print 'AVG FAI:',res_dict["average"]
    
time6 = time.clock()
tt3 = time6-time5
print "TIME TAKEN3 4 FAI:", tt3/60.0

#VISUALISE

display2dlist.append(res_dict["vertical_surface_list"])
display2dlist.append(res_dict["projected_surface_list"])
colourlist.append("WHITE")
colourlist.append("RED")

py3dmodel.utility.visualise_falsecolour_topo(res_dict["grids"],res_dict["fai_list"], other_occtopo_2dlist = display2dlist, 
                                                        other_colour_list = colourlist)