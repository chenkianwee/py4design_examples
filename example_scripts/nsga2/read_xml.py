import os
from pyliburo import pyoptimise

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

xml_filepath = os.path.join(parent_path, "example_files", "xml", "dead.xml")
inds = pyoptimise.analyse_xml.get_inds_frm_xml(xml_filepath)

far_list = []
usffai_list = []
for ind in inds:
    score_list = pyoptimise.analyse_xml.get_score(ind)
    far = score_list[1]
    usffai = score_list[0]
    far_list.append(far)
    usffai_list.append(usffai)


#far_list.extend([4.2,7.6,2.9,7.7])
#usffai_list.extend([0.01,0.0,0.02,0.06])
far_min = min(far_list)
far_max = max(far_list)

usffai_min = min(usffai_list)
usffai_max = max(usffai_list)


print far_min, far_max
print usffai_max, usffai_min