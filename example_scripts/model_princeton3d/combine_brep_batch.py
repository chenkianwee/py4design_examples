import os

from py4design import py3dmodel

#===========================================================================================
#INPUTS
#===========================================================================================
campus_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus"

res_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus_overall"

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

    tree_filepath = os.path.join(folderpath, "tree5by5m.brep")
    tree_pt_filepath = os.path.join(folderpath, "tree5by5m_pt.brep")
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
    print "*******Converting Folder", dirx, "Folder", cnt+1, "of", ndir, "***************"
    folderpath = os.path.join(campus_dir, dirx)
    bldg, bldg_pt, road, terrain, impr_srf, tree, tree_pt = read_files_from_folder(folderpath)
    bldg_list.append(bldg)
    bldg_pt_list.append(bldg_pt)
    road_list.append(road)
    terrain_list.append(terrain)
    imp_srf_list.append(impr_srf)
    tree_list.append(tree)
    tree_pt_list.append(tree_pt)
    cnt+=1

res_folderpath = os.path.join(res_dir, "overall")
if not os.path.isdir(res_folderpath):
    os.mkdir(res_folderpath)
        
#overall_bldg_filepath = os.path.join(res_folderpath, "bldg.brep")
#bldg_cmpd = py3dmodel.construct.make_compound(bldg_list)
#py3dmodel.utility.write_brep(bldg_cmpd, overall_bldg_filepath)
#
#overall_bldg_pt_filepath = os.path.join(res_folderpath, "bldg_pt.brep")
#bldg_pt_cmpd = py3dmodel.construct.make_compound(bldg_pt_list)
#py3dmodel.utility.write_brep(bldg_pt_cmpd, overall_bldg_pt_filepath)
#
#overall_road_filepath = os.path.join(res_folderpath, "road.brep")
#road_cmpd = py3dmodel.construct.make_compound(road_list)
#py3dmodel.utility.write_brep(road_cmpd, overall_road_filepath)
#
#overall_terrain_filepath = os.path.join(res_folderpath, "terrain.brep")
#terrain_cmpd = py3dmodel.construct.make_compound(terrain_list)
#py3dmodel.utility.write_brep(terrain_cmpd, overall_terrain_filepath)
#
#overall_imp_filepath = os.path.join(res_folderpath, "impervious_surface.brep")
#imp_cmpd = py3dmodel.construct.make_compound(imp_srf_list)
#py3dmodel.utility.write_brep(imp_cmpd, overall_imp_filepath)

overall_tree_filepath = os.path.join(res_folderpath, "tree5by5m.brep")
tree_cmpd = py3dmodel.construct.make_compound(tree_list)
py3dmodel.utility.write_brep(tree_cmpd, overall_tree_filepath)

overall_tree_pt_filepath = os.path.join(res_folderpath, "tree_pt5by5m.brep")
tree_pt_cmpd = py3dmodel.construct.make_compound(tree_pt_list)
py3dmodel.utility.write_brep(tree_pt_cmpd, overall_tree_pt_filepath)
