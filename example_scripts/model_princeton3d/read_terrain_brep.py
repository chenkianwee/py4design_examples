import os
from py4design import py3dmodel

terrain_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrains"
n_terrains = 420
start_cnt = 0

zmin_list = []
zmax_list = []
t_list = []
for i in range(n_terrains):
    t_filename = "terrain_10by10km_pt_" + str(i) + ".brep"
    t_filepath = os.path.join(terrain_dir, t_filename)
    terrain = py3dmodel.utility.read_brep(t_filepath)
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(terrain)
    zmin_list.append(zmin)
    zmax_list.append(zmax)
    t_list.append(terrain)
    
zmin_list2 = sorted(zmin_list)
mnz = zmin_list2[1]
mxz = max(zmax_list)
print mnz, mxz
print zmin_list2
py3dmodel.utility.visualise([t_list], ["GREEN"])