import os
import time
import pyliburo
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
for cnt in range(1):
    citygml_filepath = os.path.join(parent_path, "example_files","citygml", "example1.gml" )
    dae_filepath = os.path.join(parent_path, "example_files","dae", "example1_fai.dae" )
        
    #citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\example" + str(cnt+1) + ".gml"
    #dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+1) + "_fai.dae"

    #or just insert a citygml file you would like to analyse here 
    '''citygml_filepath = "C://file2analyse.gml"'''
    #================================================================================
    #INSTRUCTION: SPECIFY THE CITYGML FILE
    #================================================================================
    
    displaylist2 = []
    evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
    
    time1 = time.clock()
    print "#==================================="
    print "EVALUATING MODEL ... ...", citygml_filepath
    print "#==================================="
    wind_dir = (1,1,0)
    avg_fai, gridded_boundary,fai_list, fs_list, wp_list, os_list = evaluations.fai(wind_dir)
    time2 = time.clock()
    print "TIME TAKEN", (time2-time1)/60
    
    print "AVERAGE FAI", avg_fai
    d_str = "AVERAGE FAI: " + str(avg_fai)
    pyliburo.utility3d.write_2_collada_falsecolour(gridded_boundary, fai_list, "FAI", dae_filepath, 
                                                   description_str = d_str, other_occface_list = os_list) 