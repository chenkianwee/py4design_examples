from py4design import py3dmodel
pt1 = (0,0,0)
pt2 = (1,1,1)
pt3 = (2,2,2)
pt4 = (1,2,2)
pt5 = (5,5,6)
is_collinear = py3dmodel.calculate.is_collinear([pt1,pt2,pt3, pt5])
is_coplanar = py3dmodel.calculate.is_coplanar([pt1,pt2,pt3, pt4, pt5])
print("IS COLLINEAR", is_collinear, "IS COPLANAR", is_coplanar)