import time
import os
from py4design import py3dmodel, citygml2eval
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

for cnt in range(1):
    citygml_filepath = os.path.join(parent_path, "example_files","citygml", "punggol_luse101.gml" )
    dae_result_name = "punggol_luse101"
    dae_filepath1 = os.path.join(parent_path, "example_files","dae", "results", dae_result_name + "_nshffai.dae" )
    dae_filepath2 = os.path.join(parent_path, "example_files","dae", "results", dae_result_name + "_nshffai2.dae" )
    dae_filepath3 = os.path.join(parent_path, "example_files","dae", "results", dae_result_name + "_dffai.dae" )
    dae_filepath4 = os.path.join(parent_path, "example_files","dae", "results", dae_result_name + "_dffai2.dae" )
    dae_filepath5 = os.path.join(parent_path, "example_files","dae", "results", dae_result_name + "_pvefai.dae" )
    dae_filepath6 = os.path.join(parent_path, "example_files","dae", "results", dae_result_name + "_pvefai2.dae" )
        
    #or just insert a citygml file you would like to analyse here 
    '''citygml_filepath = "C://file2analyse.gml"'''
    
    #change the filepath to where you want to save the file to 
    weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
    
    evaluations = citygml2eval.Evals(citygml_filepath)
    xdim = 9
    ydim = 9
    
    lower_irrad_threshold = 254#kw/m2
    upper_irrad_threshold = 364#kw/m2
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
    
    res_dict  = evaluations.nshffai(upper_irrad_threshold,weatherfilepath,xdim,ydim)
    print "NON SOLAR HEATED FACADE TO FLOOR AREA INDEX:", res_dict["afi"]
    print "NON SOLAR HEATED FACADE AREA INDEX:", res_dict["ai"]
    
    d_str = "NSHFFAI: " + str(res_dict["afi"]) + "\n" + "NSHFAI: " + str(res_dict["ai"])
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                                   "kWh/m2", dae_filepath1, description_str = d_str, 
                                                   minval = 0, maxval = 758.17)

    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["building_solids"], res_dict["afi_list"], "NSHFFAI", 
                                                   dae_filepath2, description_str = d_str, 
                                                   minval = 0.0, maxval = 0.8)
    
    us_dict = evaluations.usffai(lower_irrad_threshold, upper_irrad_threshold,weatherfilepath,xdim,ydim)
    print "USEFUL SOLAR FACADE TO FLOOR AREA INDEX :", us_dict["afi"]
    
    #==========================================================================================================================
    #illum threshold (lux)
    #==========================================================================================================================
    res_dict = evaluations.dffai(illum_threshold,weatherfilepath,xdim,ydim)
    print "DAYLIGHT FACADE TO FLOOR AREA INDEX:", res_dict["afi"]
    print "DAYLIGHT FACADE AREA INDEX:", res_dict["ai"]
    
    
    d_str = "DFFAI: " + str(res_dict["afi"]) + "\n" + "DFAI: " + str(res_dict["ai"])
    
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], 
                                                   "lx", dae_filepath3, description_str = d_str, 
                                                   minval = 0, maxval = 11111.11)
    
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["building_solids"], res_dict["afi_list"], "DFFAI", 
                                                   dae_filepath4, description_str = d_str, 
                                                   minval = 0.0, maxval = 0.8)
    

    #==============================================================================================
    #solar potential measures the potential energy that can be generated on the building surfaces
    #==============================================================================================
    res_dict = evaluations.pvefai(roof_irrad_threshold, facade_irrad_threshold,weatherfilepath,xdim,ydim)
                                                                                       
    print "PV ENVELOPE TO FACADE AREA INDEX :", res_dict["afi"]
    print "PV ENVELOPE AREA INDEX :", res_dict["ai"]
    
    
    d_str = "PVEFAI: " + str(res_dict["afi"]) + "\n" + "PVEAI: " + str(res_dict["ai"])
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["sensor_surfaces"], res_dict["solar_results"], "kWh/m2", dae_filepath5, 
                                                   description_str = d_str, minval = 180, maxval = roof_irrad_threshold)
    
    bsolid = res_dict["building_solids"]
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["building_solids"], res_dict["afi_list"][0], "PVEFAI", 
                                                   dae_filepath6, description_str = d_str, 
                                                   minval = 0.0, maxval = 0.8)
    
    time2 = time.clock()
    print "TIME TAKEN", (time2-time1)/60
    print "MODEL EVALUATED!"

    res_dict = evaluations.pvafai(roof_irrad_threshold, weatherfilepath,xdim,ydim, surface = "roof")
                                                                                      
    print "PV ROOF TO FLOOR AREA INDEX :", res_dict["afi"]
    
    res_dict = evaluations.pvafai(facade_irrad_threshold, weatherfilepath,xdim,ydim, surface = "facade")  
                                                                                       
    print "PV FACADE TO FLOOR AREA INDEX :", res_dict["afi"]