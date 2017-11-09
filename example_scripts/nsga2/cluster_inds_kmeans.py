import os
from py4design import pyoptimise

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
overallxmlfile = os.path.join(parent_path, "example_files", "xml", "dead.xml")

inds = pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
result_dict = pyoptimise.analyse_xml.kmeans_inds(inds,"score", n_clusters = 3)
cluster_list = result_dict["cluster_list"]
res_img_filepath = os.path.join(parent_path, "example_files", "xml", "results", "clusters.png")

pts = []
labellist =[]
arealist = []
colourlist = []

cluster_cnt = 0
for cluster in cluster_list:
    for ind in cluster:
        score_list = pyoptimise.analyse_xml.get_score(ind)
        idx = pyoptimise.analyse_xml.get_id(ind)
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
pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=12, labellist = labellist,
                                   xlabel = "cooling", ylabel = "daylight", savefile = res_img_filepath )

