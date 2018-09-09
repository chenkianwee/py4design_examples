import os
from py4design import pyoptimise
#====================================================================================================================
#INPUTS
#====================================================================================================================
xmlfile =  "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_2\\xml\\archive\\1\\npareto.xml"
xmlfile2 =  "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_2\\xml\\archive\\1\\pareto.xml"
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
        score_list = [score1, score2]
        
        cnt = 0
        cnt2 = 0
        if score2 == 10 and score1 > 0.45:
            params = pyoptimise.analyse_xml.get_inputparam(ind)
            non_unique.append(ind)
            if params not in params_list:
                unique.append(ind)
                params_list.append(params)
                #print idx, params
                #print cnt
                cnt+=1
            cnt2+=1
        pts.append(score_list)
        #labellist.append(str(idx))
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
                                            xlabel = "view", ylabel = "built", savefile = res_img_filepath)

#pts3d, colourlist, arealist, labellist = xml23dplot(xmlfile, "black")

#pyoptimise.draw_graph.scatter_plot_surface3d(pts3d, colourlist, arealist, 
#                                             labellist = [], xlabel = "diff", 
#                                             ylabel = "dffai", zlabel = "fai", 
#                                             title = "", 
#                                             savefile = res_img_filepath, 
#                                             elev=45, azim = 240)