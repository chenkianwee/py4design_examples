import pyliburo
xmlfile = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\pareto.xml"
xmlfile2 = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\npareto.xml"
res_img_filepath = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\overall.png"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
inds2 = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)

pts = []
labellist =[]
arealist = []
colourlist = []
for ind in inds:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    if score_list[0] > 73:
        if idx == "209":
            print idx, score_list
            labellist.append(idx)
        else:
            print "MORE THAN 73", idx, score_list
            labellist.append("")
    elif score_list[0] < 58:
        if idx == "547":
            print idx, score_list
            labellist.append(idx)
        else:
            print "LESS THAN 58", idx, score_list
            labellist.append("")
    elif score_list[0] > 65 and score_list[0] < 70 :
        #print "MORE BETWEEN 65 AND 70", idx
        print type(idx)
        if idx == "999":
            print idx, score_list
            labellist.append(idx)
            
        else:
            #print "BETWEEN 65 BETWEEN 70", idx, score_list
            labellist.append("")
    else:
        labellist.append("") 
    pts.append(score_list)
    #pareto_labellist.append(idx)
    arealist.append(30)
    colourlist.append("red")
    
for ind in inds2:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    pts.append(score_list)
    labellist.append("")
    arealist.append(10)
    colourlist.append("black")
    
    
print "DRAWING GRAPH ..."
pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=24, labellist = labellist,
                                            xlabel = "SHGFAI(%)", ylabel = "FAI(%)", savefile = res_img_filepath )