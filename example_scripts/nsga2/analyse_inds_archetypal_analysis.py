import pyliburo
overallxmlfile = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\overall.xml"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
archetypes = pyliburo.pyoptimise.analyse_xml.archetypal_analysis_inds(inds, "inputparam", 5)
print archetypes[0]