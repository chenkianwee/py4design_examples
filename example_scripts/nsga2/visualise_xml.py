import os
from py4design import pyoptimise
#====================================================================================================================
#INPUTS
#====================================================================================================================
xmlfile =  "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\hdb\\result2\\xml\\archive\\1\\pareto.xml"
xmlfile2 =  "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\hdb\\result3\\xml\\archive\\1\\pareto.xml"
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
    non_unique = []
    unique = []
    for ind in inds:
        idx = pyoptimise.analyse_xml.get_id(ind)
        score_list = pyoptimise.analyse_xml.get_score(ind)
        score1 = score_list[0]
        score2 = score_list[1]
        score3 = score_list[2]
        score_list = [score2, score3]
        
#        cnt = 0
#        cnt2 = 0
#        if score2 == 10 and score1 > 0.45:
#            params = pyoptimise.analyse_xml.get_inputparam(ind)
#            non_unique.append(ind)
#            if params not in params_list:
#                unique.append(ind)
#                params_list.append(params)
#                #print idx, params
#                #print cnt
#                cnt+=1
#            cnt2+=1
        pts.append(score_list)
        if idx == "78":
            print "FOUND IT", idx
            labellist.append(str(idx))
        else:
            labellist.append("")
        arealist.append(60)
        colourlist.append(colour)
    
    print len(unique), len(non_unique)
    return pts, colourlist, arealist, labellist

def xml23dplot(xmlfile, colour):
    inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)

    pts = []
    labellist =[]
    arealist = []
    colourlist = []
    params_list = []
    for ind in inds:
        idx = pyoptimise.analyse_xml.get_id(ind)
        score_list = pyoptimise.analyse_xml.get_score(ind)
        score1 = score_list[0]
        score2 = score_list[1]
        score3 = score_list[2]
        score_list = [score1, score2, score3]

#        if score3 < 0.35:
#            params = pyoptimise.analyse_xml.get_inputparam(ind)
#            if params not in params_list:
#                params_list.append(params)
#                print idx, params
        pts.append(score_list)
        #labellist.append(str(idx))
        arealist.append(60)
        colourlist.append(colour)
        
    return pts, colourlist, arealist, labellist

def p_coord(xmlfile, colour):
    inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
    score_list = []
    style_list = []
    for ind in inds:
        idx = pyoptimise.analyse_xml.get_id(ind)
        scores = pyoptimise.analyse_xml.get_score(ind)
        score_list.append(scores)
        style_list.append(colour)
        if scores[2] < 0.28:
            print idx, scores[2]
    return score_list, style_list
#====================================================================================================================
#THE MAIN SCRIPT
#====================================================================================================================
parent_path = os.path.abspath(os.path.join(xmlfile, os.pardir))

print "READING XML ..."
res_img_filepath = os.path.join(parent_path, "125labelled_diffai_fai_result_img.png")
#res_img_filepath = os.path.join(parent_path, "diffai_fai_result_img.png")
pts1, colourlist1, arealist1, labellist1 = xml2plot(xmlfile, "black")
pts2, colourlist2, arealist2, labellist2 = xml2plot(xmlfile2, "red")
print labellist2
pts = pts1+pts2
arealist = arealist1 + arealist2
colourlist = colourlist1 + colourlist2
labellist = labellist1 + labellist2
#pyoptimise.draw_graph.scatter_plot(pts, colourlist, arealist, label_size=14, labellist = labellist,
#                                            xlabel = "diffai", ylabel = "fai", savefile = res_img_filepath)

#pts3d, colourlist, arealist, labellist = xml23dplot(xmlfile, "black")
#
#pyoptimise.draw_graph.scatter_plot_surface3d(pts3d, colourlist, arealist, 
#                                             labellist = [], xlabel = "diff", 
#                                             ylabel = "dffai", zlabel = "fai", 
#                                             title = "", 
#                                             savefile = res_img_filepath, 
#                                             elev=30, azim = 150)

#generate the graph showing the archetypes
res_img_filepath_p = os.path.join(parent_path, "parallel_coord3.png")
score_list, style_list = p_coord(xmlfile, "grey")
score_list2, style_list2 = p_coord(xmlfile2, "red")
score_list3 = score_list+score_list2
style_list3 = style_list+style_list2

score_list3.append((4221.0, 0.86, 0.55))
score_list3.append((560.0, 0.6, 0.12))
style_list3.append("white")
style_list3.append("white")

score_list3.append((560.0, 0.86, 0.12))
style_list3.append("blue")

#score_list3.append((2390.0, 0.664, 0.275))
#style_list3.append("red")

pyoptimise.draw_graph.parallel_coordinates(score_list3, ["diff", "dffai", "fai"],
                                                    savefile = res_img_filepath_p, style = style_list3)
