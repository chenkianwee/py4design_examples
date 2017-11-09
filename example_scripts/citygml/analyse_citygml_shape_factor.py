import os
import time
from py4design import py3dmodel, pycitygml, gml3dmodel, urbangeom, urbanformeval

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
for cnt in range(1):
    citygml_filepath = os.path.join(parent_path, "example_files","citygml", "punggol_luse101.gml" )
    dae_filepath = os.path.join(parent_path, "example_files","dae", "results", "punggol_luse101_shape.dae" )
    
    time1 = time.clock()
    print "#==================================="
    print "EVALUATING MODEL ... ...", citygml_filepath
    print "#==================================="
    
    read_citygml = pycitygml.Reader()
    read_citygml.load_filepath(citygml_filepath)
            
    buildings = read_citygml.get_buildings()    
    flr2flr_height = 3.0
    flr_area_list = []
    flr_plate_list = []
    bsolid_list = []
    for building in buildings:
        bldg_occsolid = gml3dmodel.get_building_occsolid(building, read_citygml)
        bsolid_list.append(bldg_occsolid)
        

    shape_factor_list = urbanformeval.calculate_shape_factor(bsolid_list, flr2flr_height)
    avg_shp_factor = sum(shape_factor_list)/float(len(shape_factor_list))
    time2 = time.clock()
    print "TIME TAKEN", (time2-time1)/60
    print "Average shape factor", avg_shp_factor
    d_str = "AVERAGE Shape Factor: " + str(avg_shp_factor)
    py3dmodel.export_collada.write_2_collada_falsecolour(bsolid_list, shape_factor_list, "Shape Factor", dae_filepath, 
                                                         description_str = d_str, minval = 0.0, maxval = 0.8)

    bvol_list = urbangeom.calculate_urban_vol(bsolid_list)
    print "URBAN VOL (m3)", sum(bvol_list)