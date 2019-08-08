import os

from py4design import py3dmodel

#===========================================================================================
#INPUTS
#===========================================================================================
campus_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus"

dae_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\dae\\main_campus"

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

    terrain_filepath = os.path.join(folderpath, "terrain.brep")
    terrain = py3dmodel.utility.read_brep(terrain_filepath)

    imp_srf_filepath = os.path.join(folderpath, "impervious_surface.brep")
    imp_srf = py3dmodel.utility.read_brep(imp_srf_filepath)

    tree_filepath = os.path.join(folderpath, "tree10by10m.brep")
    tree_pt_filepath = os.path.join(folderpath, "tree10by10m_pt.brep")
    tree = py3dmodel.utility.read_brep(tree_filepath)
    tree_pt = py3dmodel.utility.read_brep(tree_pt_filepath)
    
    return bldg, bldg_pt, road, terrain, imp_srf, tree, tree_pt
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

ndir = len(list_dir)
cnt = 0
for dirx in list_dir:
    print "*******Converting Folder", dirx, "Folder", cnt, "of", ndir, "***************"
    folderpath = os.path.join(campus_dir, dirx)
    bldg, bldg_pt, road, terrain, impr_srf, tree, tree_pt = read_files_from_folder(folderpath)
    #bldg, bldg_pt, road, terrain, impr_srf = read_files_from_folder(folderpath)
    dae_folderpath = os.path.join(dae_dir, dirx)
    if not os.path.isdir(dae_folderpath):
        os.mkdir(dae_folderpath)
        
    bldg_daepath = os.path.join(dae_folderpath, "building.dae")
    bfaces = py3dmodel.fetch.topo_explorer(bldg, "face")
    py3dmodel.export_collada.write_2_collada(bldg_daepath, occface_list = bfaces)
    
    road_daepath = os.path.join(dae_folderpath, "road.dae")
    py3dmodel.export_collada.write_2_collada(road_daepath, occface_list = [road])
    
    terrain_daepath = os.path.join(dae_folderpath, "terrain.dae")
    py3dmodel.export_collada.write_2_collada(terrain_daepath, occface_list = [terrain])
    
    tree_daepath = os.path.join(dae_folderpath, "tree.dae")
    tree_faces = py3dmodel.fetch.topo_explorer(tree, "face")

    tree_edges = py3dmodel.fetch.topo_explorer(tree, "edge")
    py3dmodel.export_collada.write_2_collada(tree_daepath, occface_list = tree_faces, occedge_list = tree_edges)
    
    bldg_list.append(bldg)
    bldg_pt_list.append(bldg_pt)
    road_list.append(road)
    terrain_list.append(terrain)
    imp_srf_list.append(impr_srf)
    tree_list.append(tree)
    tree_pt_list.append(tree_pt)
    cnt+=1

#py3dmodel.utility.visualise([bldg_list, terrain_list], 
#                            ["WHITE", "GREEN"])

#py3dmodel.utility.visualise([bldg_list, road_list, terrain_list, tree_list, tree_pt_list], 
#                            ["WHITE", "BLACK", "GREEN", "GREEN", "BLUE"])
    
#py3dmodel.utility.visualise([bldg_list, road_list, imp_srf_list, tree_list], 
#                            ["WHITE", "BLACK", "BLUE", "GREEN"])