import os
from pyliburo import pyoptimise

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

xmlfile = os.path.join(parent_path, "example_files", "xml", "pareto.xml")
xmlfile2 = os.path.join(parent_path, "example_files", "xml", "npareto.xml")
res_img_filepath = os.path.join(parent_path, "example_files", "xml", "results", "pareto_front2.png")

inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
inds2 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)

print "DRAWING GRAPH ..."
pt3d_list = []
label_list = []
area_list = []
colour_list = []

for ind in inds:
    score_list = pyoptimise.analyse_xml.get_score(ind)
    input_list = pyoptimise.analyse_xml.get_inputparam(ind)
    idx = pyoptimise.analyse_xml.get_id(ind)
    pt3d_list.append(input_list[0:3])
    label_list.append("")
    area_list.append(10)
    colour_list.append("red")

for ind in inds2:
    score_list = pyoptimise.analyse_xml.get_score(ind)
    input_list = pyoptimise.analyse_xml.get_inputparam(ind)
    idx = pyoptimise.analyse_xml.get_id(ind)
    pt3d_list.append(input_list[0:3])
    label_list.append("")
    area_list.append(10)
    colour_list.append("black")
   
pyoptimise.draw_graph.scatter_plot3d(pt3d_list, colour_list, area_list, labellist = [], xlabel = "shgfai", ylabel = "dfai", zlabel = "far", title = "", 
                                              savefile = res_img_filepath, elev=60, azim = 240)

pyoptimise.draw_graph.scatter_plot_surface3d(pt3d_list, colour_list, area_list, labellist = [], xlabel = "shgfai", ylabel = "dfai", zlabel = "far", title = "", 
                                              savefile = res_img_filepath, elev=60, azim = 240)