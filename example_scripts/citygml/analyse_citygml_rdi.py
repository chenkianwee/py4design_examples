import os
import time
from py4design import citygml2eval, py3dmodel
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
for cnt in range(1):
    citygml_filepath = os.path.join(parent_path, "example_files", "mdpi_urbform_eg", "citygml", "yishun_central.gml" )
    dae_filepath = os.path.join(parent_path, "example_files","dae", "results", "yishun_central_rdi.dae" )
        
    #or just insert a citygml file you would like to analyse here 
    '''citygml_filepath = "C://file2analyse.gml"'''
    #================================================================================
    #INSTRUCTION: SPECIFY THE CITYGML FILE
    #================================================================================
    displaylist2 = []
    evaluations = citygml2eval.Evals(citygml_filepath)
    
    time1 = time.perf_counter_ns()
    print("#===================================")
    print("EVALUATING MODEL ... ...", citygml_filepath)
    print("#===================================")
    res_dict = evaluations.rdi(rdi_threshold = 0.6)
    
    print ("AVG_RDI", res_dict["average"])
    print ("RDI PERCENTAGE", res_dict["percent"])
    print ("ROAD LENGTH", res_dict["road_length"])
    time2 = time.perf_counter_ns()
    print ("TOTAL TIME TAKEN", (time2-time1)/60)
    d_str = " AVG_RDI: " + str(res_dict["average"]) + "\n" + "RDI PERCENTAGE: " + str(res_dict["percent"]) + "\n" + "ROAD LENGTH: " + str(res_dict["road_length"])
    
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["plots"], res_dict["rdi_list"] , "RDI", dae_filepath, 
                                                         description_str = d_str,
                                                         minval = 0.0, maxval = 1.0, 
                                                         other_occedge_list = res_dict["network_edges"] + res_dict["peripheral_points"])
    
    py3dmodel.utility.visualise_falsecolour_topo(res_dict["plots"], res_dict["rdi_list"], 
                                                 other_occtopo_2dlist = [res_dict["network_edges"] + res_dict["peripheral_points"]], 
                                                 other_colour_list = ["WHITE"])