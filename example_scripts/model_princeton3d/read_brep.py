import os

from py4design import py3dmodel

#===========================================================================================
#INPUTS
#===========================================================================================
campus_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\merwick"

start_index = 1
end_index = -1
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def read_files_from_campus_dir(campus_dir, start_index=0, end_index=-1):
    bldg_list = []
    bldg_pt_list = []
    road_list = []
    terrain_list = []
    impr_srf_list = []
    
    list_dir = os.listdir(campus_dir)
    if end_index == -1:
        list_dir = list_dir[start_index:]
    else:
        list_dir = list_dir[start_index:end_index]
    for dirx in list_dir:        
        bldg_filepath = os.path.join(campus_dir, dirx, "bldg.brep")
        bldg_pt_filepath = os.path.join(campus_dir, dirx, "bldg_pt.brep")
        road_filepath = os.path.join(campus_dir, dirx, "road.brep")
        terrain_filepath = os.path.join(campus_dir, dirx, "terrain.brep")
        imp_srf_filepath = os.path.join(campus_dir, dirx, "impervious_surface.brep")
        
        bldg = py3dmodel.utility.read_brep(bldg_filepath)
        bldg_pt = py3dmodel.utility.read_brep(bldg_pt_filepath)
        road = py3dmodel.utility.read_brep(road_filepath)
        road = move_up_road(road)
        terrain = py3dmodel.utility.read_brep(terrain_filepath)
        terrain = triangulate_terrain(terrain)
        imp_srf = py3dmodel.utility.read_brep(imp_srf_filepath)
        imp_srf = move_up_road(imp_srf)
        
        bldg_list.append(bldg)
        bldg_pt_list.append(bldg_pt)
        road_list.append(road)
        terrain_list.append(terrain)
        impr_srf_list.append(imp_srf)
    
    return bldg_list, bldg_pt_list, road_list, terrain_list, impr_srf_list

def triangulate_terrain(terrain_cmpd):
    vlist = py3dmodel.fetch.topo_explorer(terrain_cmpd, "vertex")
    occptlist = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
    pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occptlist)
    tri = py3dmodel.construct.delaunay3d(pyptlist)
    shell = py3dmodel.construct.sew_faces(tri)[0]
    return shell

def move_up_road(road_cmpd, magnitude = 1):
    mv_road = py3dmodel.modify.move([0,0,0], [0,0,magnitude], road_cmpd)
    return mv_road
#===========================================================================================
#MAIN
#===========================================================================================
bldg_list, bldg_pt_list, road_list, terrain_list, impr_srf_list = read_files_from_campus_dir(campus_dir, start_index = 1, end_index = end_index)

#py3dmodel.utility.visualise([bldg_list, bldg_pt_list, road_list, terrain_list], ["WHITE", "BLUE", "BLACK", "GREEN"])
py3dmodel.utility.visualise([bldg_list, road_list, terrain_list, impr_srf_list], ["WHITE", "BLACK", "GREEN", "BLUE"])