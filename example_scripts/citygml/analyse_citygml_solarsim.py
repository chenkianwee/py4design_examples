import time
import os
import pyliburo
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

for cnt in range(9):
    #citygml_filepath = os.path.join(parent_path, "example_files","citygml", "punggol_luse101.gml" )
    #dae_result_name = "punggol_luse101"
    #dae_filepath1 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_nshfavi.dae" )
    #dae_filepath2 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_dfavi.dae" )
    #dae_filepath3 = os.path.join(parent_path, "example_files","dae", dae_result_name + "_pveavi.dae" )
    
    citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\example" + str(cnt+1) + ".gml"
    dae_filepath1 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+1) + "_nshfavi.dae"
    dae_filepath2 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+1) + "_dfavi.dae"
    dae_filepath3 = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+1) + "_pveavi.dae"

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
    
    avg_shrfavi, shrfavi_percent, shrfai, topo_list, irrad_ress  = evaluations.shrfavi(irrad_threshold,weatherfilepath,xdim,ydim)
    print "SOLAR REDUCTION FACADE AREA VOLUME INDEX:", avg_shrfavi
    print "SOLAR REDUCTION FACADE AREA INDEX:", shrfai
    
    d_str = "NSHFAVI: " + str(avg_shrfavi) + "\n" + "NSHFAI: " + str(shrfai)
    pyliburo.utility3d.write_2_collada_falsecolour(topo_list, irrad_ress, "kWh/m2", dae_filepath1, description_str = d_str, 
                                                   minval = 300, maxval = 1280)
    #==========================================================================================================================
    #illum threshold (lux)
    #==========================================================================================================================
    avg_dfavi, dfavi_percent, dfai, topo_list, illum_ress = evaluations.dfavi(illum_threshold,weatherfilepath,xdim,ydim)
    print "DAYLIGHT FACADE AREA VOLUME INDEX:", avg_dfavi
    print "DAYLIGHT FACADE AREA INDEX:", dfai
    
    
    d_str = "DFAVI: " + str(avg_dfavi) + "\n" + "DFAI: " + str(dfai)
    pyliburo.utility3d.write_2_collada_falsecolour(topo_list, illum_ress, "lx", dae_filepath2, description_str = d_str, 
                                                   minval = 0, maxval = 10000)
    #==========================================================================================================================
    #solar potential measures the potential energy that can be generated on the building surfaces
    #==========================================================================================================================
    
                                                                              
    avg_pveavi, pveavi_percent, pveai, epv, topo_list, irrad_ress = evaluations.pveavi(roof_irrad_threshold, facade_irrad_threshold,
                                                                                       weatherfilepath,xdim,ydim)
    print "PV ENVELOPE AREA VOLUME INDEX :", avg_pveavi
    print "PV ENVELOPE AREA INDEX :", pveai
    
    
    d_str = "PVEAVI: " + str(avg_pveavi) + "\n" + "PVEAI: " + str(pveai)
    pyliburo.utility3d.write_2_collada_falsecolour(topo_list, irrad_ress, "kWh/m2", dae_filepath3, description_str = d_str, 
                                                   minval = 180, maxval = roof_irrad_threshold)
    
    time2 = time.clock()
    print "TIME TAKEN", (time2-time1)/60
    print "MODEL EVALUATED!"
    
    '''
    avg_pvravi, pvravi_percent, pvrai, epv, topo_list, irrad_ress = evaluations.pvavi(roof_irrad_threshold, weatherfilepath,xdim,ydim, 
                                                                                      surface = "roof")
    
    print "PV ROOF AREA VOLUME INDEX :", avg_pvravi
    
    avg_pvfavi, pvfavi_percent, pvfai, epv, topo_list, irrad_ress = evaluations.pvavi(facade_irrad_threshold, weatherfilepath,xdim,ydim, 
                                                                                      surface = "facade")   
    print "PV FACADE AREA VOLUME INDEX :", avg_pvfavi
    
    '''