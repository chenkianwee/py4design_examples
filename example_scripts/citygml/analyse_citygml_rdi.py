import os
import time
from pyliburo import citygml2eval
from pyliburo import py3dmodel
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
for cnt in range(2):
    citygml_filepath = os.path.join(parent_path, "example_files","citygml", "example1.gml" )
    dae_filepath = os.path.join(parent_path, "example_files","dae", "example1_rdi.dae" )
    
    #citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\example" + str(cnt+7) + ".gml"
    #dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+7) + "_rdi.dae"
        
    #or just insert a citygml file you would like to analyse here 
    '''citygml_filepath = "C://file2analyse.gml"'''
    #================================================================================
    #INSTRUCTION: SPECIFY THE CITYGML FILE
    #================================================================================
    displaylist2 = []
    evaluations = citygml2eval.Evals(citygml_filepath)
    
    time1 = time.clock()
    print "#==================================="
    print "EVALUATING MODEL ... ...", citygml_filepath
    print "#==================================="
    res_dict = evaluations.rdi(rdi_threshold = 0.6)
    
    
    print "AVG_RDI", res_dict["average"]
    print "RDI PERCENTAGE", res_dict["percent"]
    print "ROAD LENGTH", res_dict["road_length"]
    time2 = time.clock()
    print "TOTAL TIME TAKEN", (time2-time1)/60
    
    d_str = " AVG_RDI: " + str(res_dict["average"]) + "\n" + "RDI PERCENTAGE: " + str(res_dict["percent"]) + "\n" + "ROAD LENGTH: " + str(res_dict["road_length"])
            
    py3dmodel.export_collada.write_2_collada_falsecolour(res_dict["plots"], res_dict["rdi_list"] , "RDI", dae_filepath, description_str = d_str,
                                                   minval = 0.0, maxval = 1.0 )