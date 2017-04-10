import pyliburo

livexmlfile =  "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\live.xml"
deadxmlfile =  "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\dead.xml"
overallxmlfile = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\overall.xml"
pyliburo.pyoptimise.analyse_xml.combine_xml_files(livexmlfile, deadxmlfile,overallxmlfile)
pyliburo.pyoptimise.analyse_xml.rmv_unevaluated_inds(overallxmlfile)