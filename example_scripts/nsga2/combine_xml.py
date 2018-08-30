import os
from py4design import pyoptimise

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

livexmlfile =  os.path.join(parent_path, "example_files", "xml", "live.xml")
deadxmlfile =  os.path.join(parent_path, "example_files", "xml", "dead.xml")
overallxmlfile = os.path.join(parent_path, "example_files", "xml", "results", "overall.xml")

result_directory = "F:\\kianwee_work\\nus\\201804-201810\\farm\\result_1"
livexmlfile =  os.path.join(result_directory, "xml", "live.xml")
deadxmlfile =  os.path.join(result_directory, "xml", "dead.xml")
overallxmlfile = os.path.join(result_directory,"xml", "overall.xml")

pyoptimise.analyse_xml.combine_xml_files(livexmlfile, deadxmlfile,overallxmlfile)
pyoptimise.analyse_xml.rmv_unevaluated_inds(overallxmlfile)