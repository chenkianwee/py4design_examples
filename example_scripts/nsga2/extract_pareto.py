import pyliburo

print "READING XML ..."
overallxmlfile = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\overall.xml"
pareto_file =  "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\pareto.xml"
npareto_file = "F:\\kianwee_work\\case_study\\auto_parm_example\\nsga2_xml\\archive\\npareto.xml"
inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)

print "EXTRACTING PARETO ..."
pfront, nonpfront = pyliburo.pyoptimise.analyse_xml.extract_pareto_front(inds, [1,0])
pyliburo.pyoptimise.analyse_xml.write_inds_2_xml(pfront, pareto_file)
pyliburo.pyoptimise.analyse_xml.write_inds_2_xml(nonpfront, npareto_file)