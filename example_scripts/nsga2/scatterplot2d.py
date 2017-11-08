import os
from pyliburo import pyoptimise

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

xmlfile = os.path.join(parent_path, "example_files", "xml", "pareto.xml")
xmlfile2 = os.path.join(parent_path, "example_files", "xml", "npareto.xml")
xmlfile3 = os.path.join(parent_path, "example_files", "xml", "dead.xml")

res_img_filepath = os.path.join(parent_path, "example_files", "xml", "results", "filtered.png")
res_img_filepath2 = os.path.join(parent_path, "example_files", "xml", "results", "pcp.png")
inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
inds2 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)
inds3 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile3)

pts = []
labellist =[]
arealist = []
colourlist = []
print "NUMBER OF PARETO:", len(inds)
print "NUMBER OF NPARETO", len(inds2)

plot2dlist = []
style_list = []

max_plot_list = [107.0, 0.8, 4.0, 4.0, 4.0, 4.0, 0.7, 1.0, 3.0, 3.0]
min_plot_list = [39.0, 0.05, -1.0, -1.0, -1.0, -1.0, 0.2, 0.0, -1.0, -1.0]
plot2dlist.append(max_plot_list)
plot2dlist.append(min_plot_list)
style_list.append("black")
style_list.append("black")
plot_axes_label_list = ["cool", "day", "cy", "wwr", "shd", "win"]
plot_axes_label_list = ["cool", "day", "suptemp"]
plot_axes_label_list = ["cooling", "daylight","ettv", "shp_f", "sens"]
plot_axes_label_list = ["cool", "day","pt1", "pt2", "pt3", "pt4", "cy", "wwr", "shd", "win"]
   
shapes = [[1.0, 0.0, 0.0, 0.0, 0.6], [0.0, 1.0, 0.0, 0.0, 0.6],[0.0, 0.0, 0.0, 0.0, 0.6],
          [0.0, 0.0, 0.0, 1.0, 0.6], [0.0, 0.0, 1.0, 0.0, 0.6]]

unique_inputs = []
cnt1 = 0
cnt2=0
cnt3 = 0
minx = float("inf")
maxx = 0

for ind in inds3:
    idx = pyoptimise.analyse_xml.get_id(ind)
    score_list = pyoptimise.analyse_xml.get_score(ind)
    cooling = score_list[0]
    daylight = score_list[1]
    
    input_list = pyoptimise.analyse_xml.get_inputparam(ind)
    
    dparm_list = pyoptimise.analyse_xml.get_derivedparam(ind)
    ettv = float(dparm_list[0])
    shape_factor = float(dparm_list[1])
    sens_load = float(dparm_list[2])/1000
    flr_area = float(dparm_list[3])
    cooling_system =  dparm_list[4]
    supply_temp = float(dparm_list[5])-273.15
    panel_srf_area = float(dparm_list[6])
    ndvus = int(dparm_list[7])
    
    plot_list = score_list + input_list #[ettv, shape_factor, sens_load]#[ettv, shape_factor, sens_load, supply_temp]# +  #+ [ettv, shape_factor, sens_load, supply_temp]
    
    
    if cooling <42 and daylight>0.62:
        #print idx
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("green")
        #if input_list not in unique_inputs:
        #    unique_inputs.append(input_list)
        #if daylight >= 0.7:
            #if input_list not in unique_inputs:
            #    print idx
            #    unique_inputs.append(input_list)
 
            #plot2dlist.append(plot_list)
            #style_list.append("green")
        cnt1+=1
        
    elif cooling <42 and daylight<0.62:
        #print idx
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("blue")
        if score_list[0] > maxx:
            maxx = score_list[0]
        #if daylight > 0.55:
        #    if input_list not in unique_inputs:
        #        print idx
        #        unique_inputs.append(input_list)
        #    plot2dlist.append(plot_list)
        #    style_list.append("blue")
        #if input_list[0:4] in shapes:
        #plot2dlist.append(plot_list)
        #style_list.append("blue")
        cnt2+=1
    
    elif cooling<50 and cooling >42:
        #print idx
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("grey")
        #if input_list[0:5] in shapes:
        #plot2dlist.append(plot_list)
        #style_list.append("grey")
        if score_list[0]<minx:
            minx = score_list[0]
        cnt3+=1
        #if daylight > 0.601: #and daylight <0.642:
        #if daylight > 0.7:
        #    if input_list not in unique_inputs:
        #        print idx
        #        unique_inputs.append(input_list)
        #    plot2dlist.append(plot_list)
        #    style_list.append("grey")
        
    else:
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("orange")
        
        if daylight >= 0.7:
            #plot_list.pop(-1)
            #plot_list.append(8.0)
            if input_list not in unique_inputs:
                print idx
                unique_inputs.append(input_list)
            plot2dlist.append(plot_list)
            style_list.append("orange")


for ind in inds:
    idx = pyoptimise.analyse_xml.get_id(ind)
    score_list = pyoptimise.analyse_xml.get_score(ind)
    cooling = score_list[0]
    daylight = score_list[1]
    input_list = pyoptimise.analyse_xml.get_inputparam(ind)
    plot_list = score_list + input_list
    if cooling <42 and daylight>0.62:
        #print idx
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("red")
        
    elif cooling <42 and daylight<0.62:
        #print idx
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("red")
        #if daylight > 0.5:
        #    if input_list not in unique_inputs:
        #        print idx
        #        print plot_list
        #        unique_inputs.append(input_list)
        #    plot2dlist.append(plot_list)
        #    style_list.append("blue")

    elif cooling<50 and cooling >42:
        #print idx, score_list
        #if input_list not in unique_inputs:
        #    print idx, score_list
        #    unique_inputs.append(input_list)
        pts.append(score_list)
        labellist.append("")
        arealist.append(30)
        colourlist.append("red")

    else:
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
print maxx, minx
print len(plot2dlist)
print len(unique_inputs)
print "DRAWING GRAPH ..."
#pyliburo.pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=24, labellist = labellist,
#                                            xlabel = "Cooling", ylabel = "Daylight", savefile = res_img_filepath)

pyoptimise.draw_graph.parallel_coordinates(plot2dlist, plot_axes_label_list,
                                                    savefile = res_img_filepath2, style = style_list)
