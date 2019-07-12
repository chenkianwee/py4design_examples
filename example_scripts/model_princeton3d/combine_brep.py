from py4design import py3dmodel

terrain_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\337\\terrain.brep"
bldg_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\337\\bldg.brep"
bldg_pt_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\337\\bldg_pt.brep"
#bldg_filepath1 = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\191\\bldg3.brep"
#bldg_pt_filepath1 = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\191\\bldg_pt3.brep"

#bldg_filepath2 = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\191\\bldg_merged.brep"
#bldg_pt_filepath2 = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\191\\bldg_pt_merged.brep"

road_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\context\\337\\road.brep"
#tree_filepath = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\tree_hull.brep"

terrain = py3dmodel.utility.read_brep(terrain_filepath)
bldgs = py3dmodel.utility.read_brep(bldg_filepath)
bldg_pts = py3dmodel.utility.read_brep(bldg_pt_filepath)

#bldgs1 = py3dmodel.utility.read_brep(bldg_filepath1)
#bldg_pts1 = py3dmodel.utility.read_brep(bldg_pt_filepath1)

#bcmpd = py3dmodel.construct.make_compound([bldgs, bldgs1])
#py3dmodel.utility.write_brep(bcmpd, bldg_filepath2)

#bcmpd1 = py3dmodel.construct.make_compound([bldg_pts, bldg_pts1])
#py3dmodel.utility.write_brep(bcmpd1, bldg_pt_filepath2)

roads = py3dmodel.utility.read_brep(road_filepath)
#trees = py3dmodel.utility.read_brep(tree_filepath)

py3dmodel.utility.visualise([[terrain], [bldgs], [roads], [bldg_pts]], ["GREEN", "WHITE", "BLACK", "BLUE"])
#py3dmodel.utility.visualise([[terrain], [roads], [bcmpd], [bcmpd1]], ["GREEN", "BLACK", "WHITE", "BLUE"])