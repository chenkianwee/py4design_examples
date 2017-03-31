import time
import os
import pyliburo
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

for cnt in range(1):
    citygml_filepath = os.path.join(parent_path, "example_files","citygml", "punggol_luse101.gml" )
    dae_result_name = "punggol_luse101"
    dae_filepath1 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_nshffai.dae" )
    dae_filepath2 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_nshffai2.dae" )
    dae_filepath3 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_dffai.dae" )
    dae_filepath4 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_dffai2.dae" )
    dae_filepath5 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_pvefai.dae" )
    dae_filepath6 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_pvefai2.dae" )
    
    '''
    citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\example" + str(cnt+7) + ".gml"
    dae_filepath1 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_nshfavi.dae"
    dae_filepath2 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_nshfavi2.dae"
    dae_filepath3 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_dfavi.dae"
    dae_filepath4 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_dfavi2.dae"
    dae_filepath5 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_pveavi.dae"
    dae_filepath6 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_pveavi2.dae"
    
    
    if cnt == 0:
        citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\toa_payoh_central.gml"
        dae_filepath1 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_nshfavi.dae"
        dae_filepath2 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_nshfavi2.dae"
        dae_filepath3 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_dfavi.dae"
        dae_filepath4 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_dfavi2.dae"
        dae_filepath5 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_pveavi.dae"
        dae_filepath6 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "toa_payoh_central_pveavi2.dae"
        
    if cnt == 1:
        citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\yishun_central.gml"
        dae_filepath1 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_central_nshfavi.dae"
        dae_filepath2 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_central_nshfavi2.dae"
        dae_filepath3 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_centrall_dfavi.dae"
        dae_filepath4 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_centrall_dfavi2.dae"
        dae_filepath5 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_central_pveavi.dae"
        dae_filepath6 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "yishun_central_pveavi2.dae"
        
    if cnt == 2:
        citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\punggol_central.gml"
        dae_filepath1 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_nshfavi.dae"
        dae_filepath2 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_nshfavi2.dae"
        dae_filepath3 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_dfavi.dae"
        dae_filepath4 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_dfavi2.dae"
        dae_filepath5 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_pveavi.dae"
        dae_filepath6 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\" + "punggol_central_pveavi2.dae"
    
    '''
    #or just insert a citygml file you would like to analyse here 
    '''citygml_filepath = "C://file2analyse.gml"'''
    
    #change the filepath to where you want to save the file to 
    weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
    
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    xdim = 9
    ydim = 9
    
    #==========================================================================================================================
    
    #80w/m2 is the benchmark envelope thermal transfer value for spore greenmark basic for commercial buildings
    #its calculated as an hourly average, multiplying it by 8760 hrs, we get the rough value for the permissible annual solar heat gain
    #1.5 is a factor to account for the raw irradiation falling on the surface, the higher we assume the better your envelope quality. 
    #factor of 1.5 means we expect 60% of the heat to be transmitted through the envelope 
    #==========================================================================================================================
    
    irrad_threshold = (80*4549)/1000.0#kw/m2
    illum_threshold = 10000#lux ~~254kw/m2
    roof_irrad_threshold = 1280 #kwh/m2
    facade_irrad_threshold = 512 #kwh/m2

    #=========================================================================================================================================
    #SPECIFY ALL THE NECCESSARY INPUTS
    #=========================================================================================================================================
    #==========================================================================================================================
    #irrad_threshold (kwh/m2)
    #==========================================================================================================================
    time1 = time.clock()
    print "#==================================="
    print "EVALUATING MODEL ... ...", citygml_filepath
    print "#==================================="
    
    
    res_dict  = evaluations.nshffai(irrad_threshold,weatherfilepath,xdim,ydim)
    print "NON SOLAR HEATED FACADE TO FLOOR AREA INDEX:", res_dict["afi"]
    print "NON SOLAR HEATED FACADE AREA INDEX:", res_dict["ai"]
    
    d_str = "NSHFFAI: " + str(res_dict["afi"]) + "\n" + "NSHFAI: " + str(res_dict["ai"])
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                                   "kWh/m2", dae_filepath1, description_str = d_str, 
                                                   minval = 0, maxval = 404.4)
    
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["building_solids"], res_dict["afi_list"], "NSHFFAI", 
                                                   dae_filepath2, description_str = d_str, 
                                                   minval = 0.0, maxval = 0.8)
    

    #==========================================================================================================================
    #illum threshold (lux)
    #==========================================================================================================================
    res_dict = evaluations.dffai(illum_threshold,weatherfilepath,xdim,ydim)
    print "DAYLIGHT FACADE TO FLOOR AREA INDEX:", res_dict["afi"]
    print "DAYLIGHT FACADE AREA INDEX:", res_dict["ai"]
    
    
    d_str = "DFFAI: " + str(res_dict["afi"]) + "\n" + "DFAI: " + str(res_dict["ai"])
    
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                                   "lx", dae_filepath3, description_str = d_str, 
                                                   minval = 0, maxval = 11111.11)
    
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["building_solids"], res_dict["afi_list"], "DFFAI", 
                                                   dae_filepath4, description_str = d_str, 
                                                   minval = 0.0, maxval = 0.8)
    

    #==========================================================================================================================
    #solar potential measures the potential energy that can be generated on the building surfaces
    #==========================================================================================================================
    
                                                                              
    res_dict = evaluations.pvefai(roof_irrad_threshold, facade_irrad_threshold,weatherfilepath,xdim,ydim)
                                                                                       
    print "PV ENVELOPE TO FACADE AREA INDEX :", res_dict["afi"]
    print "PV ENVELOPE AREA INDEX :", res_dict["ai"]
    
    
    d_str = "PVEFAI: " + str(res_dict["afi"]) + "\n" + "PVEAI: " + str(res_dict["ai"])
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], "kWh/m2", dae_filepath5, 
                                                   description_str = d_str, minval = 180, maxval = roof_irrad_threshold)
    
    bsolid = res_dict["building_solids"]
    print "solid list", len(bsolid)
    pyliburo.utility3d.write_2_collada_falsecolour(res_dict["building_solids"], res_dict["afi_list"][0], "PVEFAI", 
                                                   dae_filepath6, description_str = d_str, 
                                                   minval = 0.0, maxval = 0.8)
    
    time2 = time.clock()
    print "TIME TAKEN", (time2-time1)/60
    print "MODEL EVALUATED!"
    '''
    res_dict = evaluations.pvafai(roof_irrad_threshold, weatherfilepath,xdim,ydim, surface = "roof")
                                                                                      
    print "PV ROOF TO FLOOR AREA INDEX :", res_dict["afi"]
    
    res_dict = evaluations.pvafai(facade_irrad_threshold, weatherfilepath,xdim,ydim, surface = "facade")  
                                                                                       
    print "PV FACADE TO FLOOR AREA INDEX :", res_dict["afi"]
    '''