import os
from pyliburo import pycitygml
from pyliburo import py3dmodel
from pyliburo import gml3dmodel
from pyliburo import urbangeom

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files","citygml", "example1.gml" )
'''citygml_filepath = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
def eval_density(citygml_filepath):
    read_citygml = pycitygml.Reader()
    read_citygml.load_filepath(citygml_filepath)
    relief_features = read_citygml.get_relief_feature()
    #get the relief feature
    tri_area_list = []
    tri_list = []
    for rf in relief_features:
        pytrianglelist = read_citygml.get_pytriangle_list(rf)
        for pytriangle in pytrianglelist:
            occtriangle = py3dmodel.construct.make_polygon(pytriangle)
            tri_list.append(occtriangle)
            tri_area = py3dmodel.calculate.face_area(occtriangle)
            tri_area_list.append(tri_area)
            
    buildings = read_citygml.get_buildings()    
    flr2flr_height = 3.0
    flr_area_list = []
    flr_plate_list = []
    for building in buildings:
        bldg_occsolid = gml3dmodel.get_building_occsolid(building, read_citygml)
        bldg_height, nstorey = urbangeom.calculate_bldg_height_n_nstorey(bldg_occsolid, flr2flr_height)
        bldg_flr_area, bldg_flr_plates = gml3dmodel.get_bulding_floor_area(building, nstorey, flr2flr_height, read_citygml)
        flr_area_list.append(bldg_flr_area)
        flr_plate_list.extend(bldg_flr_plates)
    
    luses = read_citygml.get_landuses()
    luse_area_list = []
    for luse in luses:
        luse_occface = gml3dmodel.gml_landuse_2_occface(luse, read_citygml)
        area = py3dmodel.calculate.face_area(luse_occface)
        luse_area_list.append(area)
        
    avg_luse = sum(luse_area_list)/len(luse_area_list)
    
    total_build_up_area = sum(flr_area_list)
    site_area = sum(tri_area_list)
    #site_area = 7.5e+06
    density = total_build_up_area/site_area

    print "TOTAL BUILD UP AREA (m2):", total_build_up_area
    print "SITE AREA (m2):", site_area
    print "AVG PLOT AREA (m2):", avg_luse
    print "NET PLOT RATIO:", density
    py3dmodel.utility.visualise([flr_plate_list, tri_list],["WHITE", "GREEN"])
    return density
    
density = eval_density(citygml_filepath)