from py4design import py3dmodel

vals = [3,6,9,12,15,18,21,24,27,30]
minx = 10
maxx = 25
fc = py3dmodel.utility.falsecolour(vals, minx, maxx)

dae = "F:\\kianwee_work\\princeton\\2018_06_to_2018_12\\coldtube\\model3d\\dae\\falsecolour.dae"
box = py3dmodel.construct.make_box(10,10,10) 
faces = py3dmodel.fetch.topo_explorer(box, "face")
py3dmodel.export_collada.write_2_collada_falsecolour(faces,[20,25,30,33,22,28], 
                                                     "Temp(C)", dae,
                                                     minval = minx, maxval = maxx)
print "done"