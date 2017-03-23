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
    dae_filepath = os.path.join(parent_path, "example_files","dae", "example1_rdi.dae" )
    
    #citygml_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\citygml\\example" + str(cnt+1) + ".gml"
    #dae_filepath = "F:\\kianwee_work\\case_study\\form_eval_example\\dae\\example" + str(cnt+1) + "_rdi.dae"
        
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
    avg_rdi,rdi_per,plts,pass_plts,fail_plts,rdi_list,edges,peri_pts, road_length = evaluations.rdi(rdi_threshold = 0.6)
    
    
    print "AVG_RDI", avg_rdi
    print "RDI PERCENTAGE", rdi_per
    print "ROAD LENGTH", road_length
    time2 = time.clock()
    print "TOTAL TIME TAKEN", (time2-time1)/60
    
    d_str = " AVG_RDI: " + str(avg_rdi) + "\n" + "RDI PERCENTAGE: " + str(rdi_per) + "\n" +  "ROAD LENGTH: " + str(road_length)
    pyliburo.utility3d.write_2_collada_falsecolour(plts, rdi_list , "RDI", dae_filepath, description_str = d_str,
                                                   minval = 0.0, maxval = 1.0,  other_occedge_list =edges )
    
    '''
    buildings = evaluations.building_occsolids
    bcompund = pyliburo.py3dmodel.construct.make_compound(buildings)
    building_edges = pyliburo.py3dmodel.fetch.geom_explorer(bcompund, "edge")
    
    display2dlist = []
    colourlist = []
    display2dlist.append(peri_pts)
    display2dlist.append(edges)
    display2dlist.append(building_edges)
    colourlist.append("WHITE")
    colourlist.append("WHITE")
    colourlist.append("BLACK")
    pyliburo.py3dmodel.construct.visualise_falsecolour_topo(rdi_list,plts,
                                                            other_topo2dlist = display2dlist, 
                                                            other_colourlist = colourlist)
    '''