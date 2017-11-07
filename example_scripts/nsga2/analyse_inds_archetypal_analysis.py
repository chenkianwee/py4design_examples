from pyliburo import pyoptimise
overallxmlfile = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\pareto.xml"
inds = pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
archetypes = pyoptimise.analyse_xml.archetypal_analysis_inds(inds, "inputparam", 5)

res_img_filepath = "F:\\kianwee_work\\case_study\\five_storey_office_example\\xml\\archive\\inputs.png"
style_list = ["black", "red","black","red", "blue"]
pyoptimise.draw_graph.parallel_coordinates([archetypes[0],archetypes[1]], ["x", "y", "z", "z", "z", "z", "z", "z"],
                                                    savefile = res_img_filepath, style = style_list)
print archetypes[0]