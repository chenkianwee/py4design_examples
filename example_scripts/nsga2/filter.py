import os
from py4design import pyoptimise

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

xml_filepath = os.path.join(parent_path, "example_files", "xml", "dead.xml")
res1 = os.path.join(parent_path, "example_files", "xml", "results", "filter1.xml")
res2 = os.path.join(parent_path, "example_files", "xml", "results", "filter2.xml")
inds = pyoptimise.analyse_xml.get_inds_frm_xml(xml_filepath)

target1_inds = []
target2_inds = []
for ind in inds:
    score_list = pyoptimise.analyse_xml.get_score(ind)
    cooling = score_list[0]
    daylight = score_list[1]
    if cooling < 80:
        target1_inds.append(ind)
        if daylight>0.5:
            idx = pyoptimise.analyse_xml.get_id(ind)
            target2_inds.append(ind)
            
pyoptimise.analyse_xml.write_inds_2_xml(target1_inds, res1)
pyoptimise.analyse_xml.write_inds_2_xml(target2_inds, res2)