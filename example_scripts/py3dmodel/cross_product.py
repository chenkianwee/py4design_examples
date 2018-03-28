from py4design import py3dmodel
pyvec1 = (1,0,0)
pyvec2 = (1,0,0)
pyvec3 = py3dmodel.calculate.cross_product(pyvec1, pyvec2)
print pyvec3