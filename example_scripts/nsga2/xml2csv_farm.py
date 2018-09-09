import os
from py4design import pyoptimise
#====================================================================================================================
#INPUTS
#====================================================================================================================
xmlfile =  "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_2\\xml\\archive\\1\\overall.xml"
csv_file = "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_2\\xml\\archive\\1\\overall.csv"
#====================================================================================================================
#INPUTS
#====================================================================================================================
inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
csv = open(csv_file, "w")
csv_str = "id,view,num_ward,num_green,corridor_length,recreate_corridor_length\n"
parm_list = []
print len(inds)
for ind in inds:
    parms = pyoptimise.analyse_xml.get_inputparam(ind)
    if parms not in parm_list:
        idx = pyoptimise.analyse_xml.get_id(ind)
        scores = pyoptimise.analyse_xml.get_score(ind)
        dp = pyoptimise.analyse_xml.get_derivedparam(ind)
    
        ind_str = str(idx) + "," + str(scores[0]) + "," + str(scores[1]) + "," +\
                    str(dp[0]) + "," + str(dp[1]) + "," + str(dp[2]) + "\n"
                    
        csv_str = csv_str + ind_str
        parm_list.append(parms)

csv.write(csv_str)
csv.close()