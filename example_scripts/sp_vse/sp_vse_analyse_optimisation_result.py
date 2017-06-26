import pyliburo

livexmlfile =  "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2_performance\\xml\\live.xml"
deadxmlfile =  "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2_performance\\xml\\dead.xml"
overallxmlfile = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2_performance\\xml\\overall.xml"
pyliburo.pyoptimise.analyse_xml.combine_xml_files(livexmlfile, deadxmlfile,overallxmlfile)
pyliburo.pyoptimise.analyse_xml.rmv_unevaluated_inds(overallxmlfile)

print "READING XML ..."
pareto_file =  "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2_performance\\xml\\pareto.xml"
npareto_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2_performance\\xml\\nonpareto.xml"
res_img_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower2_performance\\xml\\pareto.png"

inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
print "EXTRACTING PARETO ..."
pfront, nonpfront = pyliburo.pyoptimise.analyse_xml.extract_pareto_front(inds, [1,1])
print len(pfront)
pyliburo.pyoptimise.analyse_xml.write_inds_2_xml(pfront, pareto_file)
pyliburo.pyoptimise.analyse_xml.write_inds_2_xml(nonpfront, npareto_file)


pts = []
labellist =[]
arealist = []
colourlist = []

np_inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(npareto_file)
p_inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(pareto_file)


for ind in np_inds:
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    pts.append(score_list)
    labellist.append("")
    arealist.append(30)
    colourlist.append("blue")
    
for ind in p_inds:
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    pts.append(score_list)
    labellist.append("")
    arealist.append(30)
    colourlist.append("red")
        
pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=24, labellist = labellist,
                                            xlabel = "NSHFFAI", ylabel = "PVEFAI", savefile = res_img_filepath)