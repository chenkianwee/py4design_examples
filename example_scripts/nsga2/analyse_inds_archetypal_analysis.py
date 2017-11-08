import os
from pyliburo import pyoptimise
#specify the xml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
overallxmlfile = os.path.join(parent_path, "example_files", "xml", "live.xml")
#extract the invdividuals from teh file
inds = pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
#archetypal analyse the individuals
archetypes = pyoptimise.analyse_xml.archetypal_analysis_inds(inds, "inputparam", 5)
#generate the graph showing the archetypes
res_img_filepath = os.path.join(parent_path, "example_files", "xml", "results", "inputs.png")

style_list = ["black", "red","black","red", "blue"]
pyoptimise.draw_graph.parallel_coordinates([archetypes[0],archetypes[1]], ["x", "y", "z", "z", "z", "z", "z", "z"],
                                                    savefile = res_img_filepath, style = style_list)
print archetypes[0]