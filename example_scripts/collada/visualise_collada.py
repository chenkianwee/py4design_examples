import os
import pyliburo
from collada import *

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "collada2citygml_example",  "dae", "example4_4_part.dae")
dae_file = os.path.join(parent_path, "example_files", "form_eval_example",  "dae", "example4_4_part.dae")
dae_file1 = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\test_tower.dae"
dae_file2 = "F:\\kianwee_work\\smart\\may2017-oct2017\\sp_workshop\\dae\\site.dae"
#dae_file = os.path.join(parent_path, "example_files","5x5ptblks", "dae", "5x5ptblks.dae")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display_2dlist = []
colour_list = []
display_list = []
dae_list = [dae_file1, dae_file2]
for dae_file in dae_list:        
    mesh = Collada(dae_file)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    g_cnt = 0
    print len(geoms)
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist:     
            if primlist:
                #display_list.append([])
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = pyliburo.py3dmodel.construct.make_polygon(pyptlist)
                        is_face_null = pyliburo.py3dmodel.fetch.is_face_null(occpolygon)
                        if not is_face_null:
                            display_list.append(occpolygon)
                        g_cnt +=1
                    elif type(prim) == lineset.Line:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = pyliburo.py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                        display_list.append(occpolygon)
                        g_cnt +=1

#print display_list
display_2dlist.append(display_list)
colour_list.append("WHITE")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)
