import os
from pyliburo import gml3dmodel
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files", "citygml", "punggol_luse101.gml")
dae_filepath = os.path.join(parent_path, "example_files", "dae", "punggol_luse101.dae")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"
citygml_filepath = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
gml3dmodel.citygml2collada(citygml_filepath, dae_filepath)