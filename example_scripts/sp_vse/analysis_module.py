import os
import pyliburo
#====================================================================================================================
#INPUTS
#====================================================================================================================
livexmlfile =  "F:\\kianwee_work\\smart\\journal\\enabling_evo_design\\data\\10\\successful\\TEST_TOWER_2_performance\\xml\\0\\live.xml"
deadxmlfile =  "F:\\kianwee_work\\smart\\journal\\enabling_evo_design\\data\\10\\successful\\TEST_TOWER_2_performance\\xml\\0\\dead.xml"

solar_index_filter = False
solar_index_min_max = [0.08, 0.1]

plot_ratio_filter = False
plot_ratio_min_max = [3.5,6.0]
#====================================================================================================================
#INPUTS
#====================================================================================================================

#====================================================================================================================
#THE MAIN SCRIPT
#====================================================================================================================
parent_path = os.path.abspath(os.path.join(livexmlfile, os.pardir))
overallxmlfile = os.path.join(parent_path, "overall.xml")

pyliburo.pyoptimise.analyse_xml.combine_xml_files(livexmlfile, deadxmlfile,overallxmlfile)
pyliburo.pyoptimise.analyse_xml.rmv_unevaluated_inds(overallxmlfile)

print "READING XML ..."
pareto_file =  os.path.join(parent_path, "pareto.xml")
npareto_file = os.path.join(parent_path, "non_pareto.xml")
res_img_filepath = os.path.join(parent_path, "result_img.png")

inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
print "EXTRACTING PARETO ..."

pfront, nonpfront = pyliburo.pyoptimise.analyse_xml.extract_pareto_front_inds(inds, [1,1])
pyliburo.pyoptimise.analyse_xml.write_inds_2_xml(pfront, pareto_file)
pyliburo.pyoptimise.analyse_xml.write_inds_2_xml(nonpfront, npareto_file)

pts = []
labellist =[]
arealist = []
colourlist = []

np_inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(npareto_file)
p_inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(pareto_file)

for ind in inds:
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    solar = score_list[0]
    plot_ratio = score_list[1]
    if solar_index_filter == True and plot_ratio_filter == False:
        smin = solar_index_min_max[0]
        smax = solar_index_min_max[1]
        if smin<=solar<=smax:
            print "Filtered Design Variant ID:", idx
            pts.append(score_list)
            #labellist.append(str(idx))
            arealist.append(60)
            colourlist.append("green")
            
    if solar_index_filter == False and plot_ratio_filter == True:
        pmin = plot_ratio_min_max[0]
        pmax = plot_ratio_min_max[1]
        if pmin<=plot_ratio<=pmax:
            print "Filtered Design Variant ID:", idx
            pts.append(score_list)
            #labellist.append(str(idx))
            arealist.append(60)
            colourlist.append("green")
            
    if solar_index_filter == True and plot_ratio_filter == True:
        smin = solar_index_min_max[0]
        smax = solar_index_min_max[1]
        
        pmin = plot_ratio_min_max[0]
        pmax = plot_ratio_min_max[1]
        if smin<=solar<=smax:            
            if pmin<=plot_ratio<=pmax:
                print "Filtered Design Variant ID:", idx
                pts.append(score_list)
                #labellist.append(str(idx))
                arealist.append(60)
                colourlist.append("green")
            
for ind in np_inds:
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    pts.append(score_list)
    labellist.append("")
    arealist.append(30)
    colourlist.append("black")
    
for ind in p_inds:
    idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
    print "Pareto Design Variant ID:", idx
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
    pts.append(score_list)
    #labellist.append(str(idx))
    arealist.append(60)
    colourlist.append("red")
        
pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=14, labellist = labellist,
                                            xlabel = "USFFAI", ylabel = "FAR", savefile = res_img_filepath)