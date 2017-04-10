import pyliburo
xmlfile = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\pareto.xml"
xmlfile2 = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\npareto.xml"
res_img_filepath = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\pareto_front.png"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
inds2 = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)

print "DRAWING GRAPH ..."
pt3d_list = []
label_list = []
area_list = []
colour_list = []

for ind in inds:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    pt3d_list.append(score_list)
    label_list.append("")
    area_list.append(10)
    colour_list.append("red")

for ind in inds2:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    pt3d_list.append(score_list)
    label_list.append("")
    area_list.append(10)
    colour_list.append("black")


#pyliburo.pyoptimise.draw_graph.scatter_plot_surface3d(pt3d_list, colour_list, area_list, labellist = [], xlabel = "", ylabel = "", zlabel = "", title = "", 
#                 savefile = "", elev=30, azim = -90)

   
pyliburo.pyoptimise.draw_graph.scatter_plot3d(pt3d_list, colour_list, area_list, labellist = [], xlabel = "shgfai", ylabel = "dfai", zlabel = "far", title = "", 
                                              savefile = res_img_filepath, elev=60, azim = 240)