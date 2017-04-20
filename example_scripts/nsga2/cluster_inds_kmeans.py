import pyliburo
overallxmlfile = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\overall.xml"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
result_dict = pyliburo.pyoptimise.analyse_xml.kmeans_inds(inds,"score", n_clusters = 4)
cluster_list = result_dict["cluster_list"]
res_img_filepath = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\clusters.png"

pts = []
labellist =[]
arealist = []
colourlist = []

cluster_cnt = 0
for cluster in cluster_list:
    for ind in cluster:
        score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
        idx = pyliburo.pyoptimise.analyse_xml.get_id(ind)
        pts.append(score_list)
        labellist.append("")
        arealist.append(10)
        if cluster_cnt ==0:
            colourlist.append("black")
        if cluster_cnt ==1:
            colourlist.append("red")
        if cluster_cnt ==2:
            colourlist.append("blue")
        if cluster_cnt ==3:
            colourlist.append("magenta")
        if cluster_cnt ==4:
            colourlist.append("yellow")
            
    cluster_cnt+=1
        
print "DRAWING GRAPH ..."
#pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=12, labellist = labellist,
#                                            xlabel = "cooling", ylabel = "daylight", savefile = res_img_filepath )

