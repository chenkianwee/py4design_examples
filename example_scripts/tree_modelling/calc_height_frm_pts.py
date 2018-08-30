import os 
import time
from py4design import py3dmodel


#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================    
def read_pts_file(pts_file, delimiter = ","):
    pf = open(pts_file, "r")
    lines = pf.readlines()
    vertex_list = []
    pyptlist = []
    x_list = []
    y_list = []
    z_list = []
    for l in lines:
        l = l.replace("\n","")
        l_list = l.split(delimiter)
        x = float(l_list[0])
        x_list.append(x)
        y = float(l_list[1])
        y_list.append(y)
        z = float(l_list[2])
        z_list.append(z)
        pypt = (x,y,z)
        occ_vertex = py3dmodel.construct.make_vertex(pypt)
        vertex_list.append(occ_vertex)
        pyptlist.append(pypt)
    
    npts = len(x_list)
    x_mean = sum(x_list)/npts
    y_mean = sum(y_list)/npts
    z_mean = sum(z_list)/npts
    
    centre_pt = (x_mean, y_mean, z_mean)
    pt_cmpd = py3dmodel.construct.make_compound(vertex_list)
    return pyptlist, pt_cmpd, centre_pt

#========================================================================================
    
#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
parent_path = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts"
for i in range(2):
    folder = "tree" + str(i+32)
    filename = "tree" + str(i+32) + ".pts"
    pts_file = os.path.join(parent_path,folder,filename)    
    #================================================================================
    #================================================================================ 
    time1 = time.time()
    
    display_2dlist = []
    colour_list = []
    #========================================================================================
    #READ THE CANOPY PT CLOUD
    #========================================================================================
    pyptlist, pt_cmpd, centre_pt = read_pts_file(pts_file)
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pt_cmpd)
    height = zmax-zmin
    print filename, "HEIGHT", height