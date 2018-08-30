import os
from py4design import pyoptimise
#====================================================================================================================
#INPUTS
#====================================================================================================================
xmlfile =  "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_1\\xml\\npareto.xml"
xmlfile2 =  "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_1\\xml\\pareto.xml"
#====================================================================================================================
#INPUTS
#====================================================================================================================
def xml2plot(xmlfile, colour):
    inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)

    pts = []
    labellist =[]
    arealist = []
    colourlist = []
    params_list = []
    for ind in inds:
        idx = pyoptimise.analyse_xml.get_id(ind)
        score_list = pyoptimise.analyse_xml.get_score(ind)
        view = score_list[0]
        built = score_list[1]
        score_list = [built, view]
        
        if built == 11:
            params = pyoptimise.analyse_xml.get_inputparam(ind)
            if params not in params_list:
                params_list.append(params)
                print idx, params
        pts.append(score_list)
        #labellist.append(str(idx))
        arealist.append(60)
        colourlist.append(colour)
        
    return pts, colourlist, arealist, labellist
#====================================================================================================================
#THE MAIN SCRIPT
#====================================================================================================================
parent_path = os.path.abspath(os.path.join(xmlfile, os.pardir))

print "READING XML ..."
res_img_filepath = os.path.join(parent_path, "result_img.png")
pts1, colourlist1, arealist1, labellist1 = xml2plot(xmlfile, "black")
pts2, colourlist2, arealist2, labellist2 = xml2plot(xmlfile2, "red")
pts = pts1+pts2
arealist = arealist1 + arealist2
colourlist = colourlist1 + colourlist2
labellist = labellist1 + labellist2
pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=14, labellist = labellist,
                                            xlabel = "built", ylabel = "view", savefile = res_img_filepath)