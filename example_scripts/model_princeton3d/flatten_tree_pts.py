from py4design import py3dmodel
import shapefile

tree_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\terrains\\terrain_10by10km_pt.brep"
shpfile_res = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_trees\\test2.shp"

#============================================================================================================
#FUNCTION
#============================================================================================================
def write_pt_shpfile(pyptlist, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 1)
    w.field('index','N',10)
    cnt=0
    for pypt in pyptlist:
        z = pypt[2]
        if z < 0:
            w.point(pypt[0], pypt[1])
            w.record(cnt)
            cnt+=1
    w.close()

#============================================================================================================
#FUNCTION
#============================================================================================================
trees = py3dmodel.utility.read_brep(tree_filepath)

tree_list = py3dmodel.fetch.topo_explorer(trees, "vertex")
occpt_list = py3dmodel.modify.occvertex_list_2_occpt_list(tree_list)
pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpt_list)
write_pt_shpfile(pyptlist, shpfile_res)