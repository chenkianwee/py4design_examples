import os

from py4design import py3dmodel

#===========================================================================================
#INPUTS
#===========================================================================================
campus_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\merwick"

start_index = 0
end_index = -1
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def read_files_from_folder(folderpath):
    bldg_filepath = os.path.join(folderpath, "bldg.brep")
    bldg_pt_filepath = os.path.join(folderpath, "bldg_pt.brep")
    bldg = py3dmodel.utility.read_brep(bldg_filepath)
    bldg_pt = py3dmodel.utility.read_brep(bldg_pt_filepath)
    
    road_filepath = os.path.join(folderpath, "road.brep")
    road = py3dmodel.utility.read_brep(road_filepath)
    road = move_up_road(road)

    terrain_filepath = os.path.join(folderpath, "terrain.brep")
    terrain = py3dmodel.utility.read_brep(terrain_filepath)

    imp_srf_filepath = os.path.join(folderpath, "impervious_surface.brep")
    imp_srf = py3dmodel.utility.read_brep(imp_srf_filepath)
    imp_srf = move_up_road(imp_srf)

    tree_filepath = os.path.join(folderpath, "tree10by10m.brep")
    tree_pt_filepath = os.path.join(folderpath, "tree10by10m_pt.brep")
    tree = py3dmodel.utility.read_brep(tree_filepath)
    tree_pt = py3dmodel.utility.read_brep(tree_pt_filepath)
    
    return bldg, bldg_pt, road, terrain, imp_srf, tree, tree_pt

def move_up_road(road_cmpd, magnitude = 1):
    mv_road = py3dmodel.modify.move([0,0,0], [0,0,magnitude], road_cmpd)
    return mv_road
#===========================================================================================
#MAIN
#===========================================================================================
list_dir = os.listdir(campus_dir)

print list_dir
if end_index == -1:
    list_dir = list_dir[start_index:]
else:
    list_dir = list_dir[start_index:end_index]
print list_dir

bldg_list = []
bldg_pt_list = []
road_list = []
terrain_list = []
imp_srf_list = []
tree_list = []
tree_pt_list = []

for dirx in list_dir:
    folderpath = os.path.join(campus_dir, dirx)
    bldg, bldg_pt, road, terrain, impr_srf, tree, tree_pt = read_files_from_folder(folderpath)
    cmpd_list = py3dmodel.fetch.topo_explorer(tree, "edge")
    print len(cmpd_list)
    #bldg, bldg_pt, road, terrain, impr_srf = read_files_from_folder(folderpath)
    
    bldg_list.append(bldg)
    bldg_pt_list.append(bldg_pt)
    road_list.append(road)
    terrain_list.append(terrain)
    imp_srf_list.append(impr_srf)
    tree_list.append(tree)
    tree_pt_list.append(tree_pt)

py3dmodel.utility.visualise([bldg_list, terrain_list], 
                            ["WHITE", "GREEN"])
#py3dmodel.utility.visualise([bldg_list, road_list, terrain_list, tree_list, tree_pt_list], 
#                            ["WHITE", "BLACK", "GREEN", "GREEN", "BLUE"])
    
#py3dmodel.utility.visualise([bldg_list, road_list, imp_srf_list, tree_list], 
#                            ["WHITE", "BLACK", "BLUE", "GREEN"])