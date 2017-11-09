from py4design import py3dmodel
angle = py3dmodel.calculate.angle_bw_2_vecs((0,1,0), (-1,0,0))
angle = py3dmodel.calculate.angle_bw_2_vecs_w_ref((0,1,0), (-1,-1,0),(0,0,1))
print angle