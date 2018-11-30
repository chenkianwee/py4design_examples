import os
from py4design import pyoptimise

xmlfile =  "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\hdb\\result2\\xml\\archive\\1\\pareto.xml"
xmlfile2 =  "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\hdb\\result3\\xml\\archive\\1\\pareto.xml"

def c_measure(xmlfile1, xmlfile2, min_max_list):
    inds1 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile1)
    score_2d_list1 = pyoptimise.analyse_xml.inds_2_score_2dlist(inds1)
    
    inds2 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)
    score_2d_list2 = pyoptimise.analyse_xml.inds_2_score_2dlist(inds2)
    
    c_measure1 = pyoptimise.analyse_xml.c_measures(score_2d_list1, score_2d_list2, min_max_list)
    c_measure2 = pyoptimise.analyse_xml.c_measures(score_2d_list2, score_2d_list1, min_max_list)
    
    print c_measure1, c_measure2
    
def s_measure(xmlfile1, xmlfile2, ref_pt, min_max_list):
    inds1 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile1)
    score_2d_list1 = pyoptimise.analyse_xml.inds_2_score_2dlist(inds1)
    s_measure = pyoptimise.analyse_xml.hyper_volume(score_2d_list1, ref_pt, min_max_list)

    inds2 = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile2)
    score_2d_list2 = pyoptimise.analyse_xml.inds_2_score_2dlist(inds2)
    s_measure2 = pyoptimise.analyse_xml.hyper_volume(score_2d_list2, ref_pt, min_max_list)
    print s_measure, s_measure2
#    c_measure1 = pyoptimise.analyse_xml.c_measures(score_2d_list1, score_2d_list2, [0,1,0])
#    c_measure2 = pyoptimise.analyse_xml.c_measures(score_2d_list2, score_2d_list1, [0,1,0])
#    
#    print c_measure1, c_measure2

min_max_list = [0,1,0]
c_measure(xmlfile, xmlfile2, min_max_list)
ref_pt = [4221,-0.6,0.55]
s_measure(xmlfile, xmlfile2, ref_pt, min_max_list)