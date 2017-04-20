import pyliburo

livexmlfile =  "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\live.xml"
deadxmlfile =  "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\dead.xml"
overallxmlfile = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\overall.xml"
pyliburo.pyoptimise.analyse_xml.combine_xml_files(livexmlfile, deadxmlfile,overallxmlfile)
pyliburo.pyoptimise.analyse_xml.rmv_unevaluated_inds(overallxmlfile)