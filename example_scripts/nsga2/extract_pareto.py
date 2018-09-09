import os
from py4design import pyoptimise

print "READING XML ..."
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

overallxmlfile = os.path.join(parent_path, "example_files", "xml", "dead.xml")

pareto_file =  os.path.join(parent_path, "example_files", "xml", "results", "pareto.xml")
npareto_file = os.path.join(parent_path, "example_files", "xml", "results", "npareto.xml")

result_directory = "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_2"
overallxmlfile = os.path.join(result_directory,"xml","archive", "1", "overall.xml")
pareto_file =  os.path.join(result_directory, "xml", "archive", "1", "pareto.xml")
npareto_file = os.path.join(result_directory, "xml", "archive", "1", "npareto.xml")

inds = pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)

print "EXTRACTING PARETO ..."
pfront, nonpfront = pyoptimise.analyse_xml.extract_pareto_front_inds(inds, [1,1])
print len(pfront)
pyoptimise.analyse_xml.write_inds_2_xml(pfront, pareto_file)
pyoptimise.analyse_xml.write_inds_2_xml(nonpfront, npareto_file)
print "DONE"