import time
import pyliburo

for cnt in range(9):
    #citygml_filepath = os.path.join(parent_path, "example_files","citygml", "example1.gml" )
    #dae_filepath = os.path.join(parent_path, "example_files","dae", "example1_fai.dae" )
        
    citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\example" + str(cnt+1) + ".gml"
    dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+1) + "_shape_factor.dae"
    '''
    if cnt == 0:
        citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\toa_payoh_central.gml"
        dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_shape_factor.dae"
        
        
    if cnt == 1:
        citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\yishun_central.gml"
        dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_central_shape_factor.dae"
        
        
    if cnt == 2:
        citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\punggol_central.gml"
        dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_shape_factor.dae"
        
    '''
    time1 = time.clock()
    print "#==================================="
    print "EVALUATING MODEL ... ...", citygml_filepath
    print "#==================================="
    
    read_citygml = pyliburo.pycitygml.Reader()
    read_citygml.load_filepath(citygml_filepath)
            
    buildings = read_citygml.get_buildings()    
    flr2flr_height = 3.0
    flr_area_list = []
    flr_plate_list = []
    bsolid_list = []
    for building in buildings:
        bldg_occsolid = pyliburo.gml3dmodel.get_building_occsolid(building, read_citygml)
        bsolid_list.append(bldg_occsolid)
        
    '''
    shape_factor_list = pyliburo.urbanformeval.calculate_shape_factor(bsolid_list, flr2flr_height)
    avg_shp_factor = sum(shape_factor_list)/float(len(shape_factor_list))
    time2 = time.clock()
    print "TIME TAKEN", (time2-time1)/60
    print "Average shape factor", avg_shp_factor
    d_str = "AVERAGE Shape Factor: " + str(avg_shp_factor)
    #pyliburo.utility3d.write_2_collada_falsecolour(bsolid_list, shape_factor_list, "Shape Factor", dae_filepath, 
    #                                               description_str = d_str, minval = 0.0, maxval = 0.8)
    '''
    bvol_list = pyliburo.urbanformeval.calculate_urban_vol(bsolid_list)
    print "URBAN VOL", sum(bvol_list)