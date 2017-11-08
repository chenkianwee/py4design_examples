import os
import collada
from collada import polylist, triangleset, lineset
from pyliburo import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "dae", "example1.dae")
#dae_file = os.path.join(parent_path, "example_files","5x5ptblks", "dae", "5x5ptblks.dae")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display_2dlist = []
colour_list = []
display_list = []
dae_list = [dae_file]
for dae_file in dae_list:     
    display_list2 = []
    mesh = collada.Collada(dae_file)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    g_cnt = 0
    #print len(geoms)
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist:     
            if primlist:
                #display_list.append([])
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                        is_face_null = py3dmodel.fetch.is_face_null(occpolygon)
                        if not is_face_null:
                            display_list.append(occpolygon)
                            display_list2.append(occpolygon)
                        g_cnt +=1
                    elif type(prim) == lineset.Line:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                        #display_list.append(occpolygon)
                        g_cnt +=1
    print len(display_list2)

display_2dlist.append(display_list)
colour_list.append("WHITE")
py3dmodel.utility.visualise(display_2dlist, colour_list)
