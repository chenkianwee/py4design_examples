import pyliburo
xmlfile = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\pareto.xml"
xmlfile2 = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\npareto.xml"
res_img_filepath = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\pareto_front.png"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
inds2 = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)

pts = []
labellist =[]
arealist = []
colourlist = []
for ind in inds:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    print idx, score_list
    pts.append(score_list)
    labellist.append("")
    arealist.append(30)
    colourlist.append("red")
    
for ind in inds2:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    nshfai = score_list[0]
    fai = score_list[1]
    if fai <= 0.48 and fai >= 0.45:
        print idx, score_list
        pts.append(score_list)
        labellist.append("")
        arealist.append(10)
        colourlist.append("black")
    else:
        pts.append(score_list)
        labellist.append("")
        arealist.append(10)
        colourlist.append("black")
    
base_nshfai = 0.0712174412239
base_fai = 0.471696895423

pts.append([base_nshfai,base_fai])
labellist.append("")
arealist.append(20)
colourlist.append("blue")

print "DRAWING GRAPH ..."
pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=24, labellist = labellist,
                                            xlabel = "NSHFAI", ylabel = "FAI", savefile = res_img_filepath )