import pyliburo
xmlfile = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\pareto.xml"
xmlfile2 = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\npareto.xml"
res_img_filepath = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\pareto_front.png"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
inds2 = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)

pts = []
labellist =[]
arealist = []
colourlist = []
print "NUMBER OF PARETO:", len(inds)

for ind in inds2:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    pts.append(score_list)
    labellist.append("")
    arealist.append(10)
    colourlist.append("black")
    
for ind in inds:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    print idx
    pts.append(score_list)
    labellist.append("")
    arealist.append(30)
    colourlist.append("red")
    

#base_nshfai = 0.0712174412239
#base_fai = 0.471696895423

#pts.append([base_nshfai,base_fai])
#labellist.append("")
#arealist.append(20)
#colourlist.append("blue")

print "DRAWING GRAPH ..."
pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=24, labellist = labellist,
                                            xlabel = "NSHFAI", ylabel = "FAI", savefile = res_img_filepath )