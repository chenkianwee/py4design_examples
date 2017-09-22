import pyliburo

xml_filepath = "F:\\kianwee_work\\smart\\journal\\enabling_evo_design\\data1\\processed\\24\\Assignment_3\\xml\\overall.xml"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(xml_filepath)

far_list = []
usffai_list = []
for ind in inds:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(ind)
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

