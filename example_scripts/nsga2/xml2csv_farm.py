import os
from py4design import pyoptimise
#====================================================================================================================
#INPUTS
#====================================================================================================================
xmlfile =  "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\hdb\\result2\\xml\\archive\\1\\overall.xml"
csv_file = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\hdb\\result2\\xml\\archive\\1\\pareto.csv"
#====================================================================================================================
#INPUTS
#====================================================================================================================
inds = pyoptimise.analyse_xml.get_inds_frm_xml(xmlfile)
csv = open(csv_file, "w")
csv_str = "id,diff,diffai,fai,rm2,rm3,rm4,rm5\n"
parm_list = []
print len(inds)
for ind in inds:
    parms = pyoptimise.analyse_xml.get_inputparam(ind)
    if parms not in parm_list:
        idx = pyoptimise.analyse_xml.get_id(ind)
        scores = pyoptimise.analyse_xml.get_score(ind)
        dp = pyoptimise.analyse_xml.get_derivedparam(ind)
    
        ind_str = str(idx) + "," + str(scores[0]) + "," + str(scores[1]) + "," +\
                    str(scores[2]) + "," + str(dp[0]) + "," + str(dp[1]) + "," + str(dp[2]) + "," + str(dp[3]) + "\n"
                    
        csv_str = csv_str + ind_str
        parm_list.append(parms)

csv.write(csv_str)
csv.close()