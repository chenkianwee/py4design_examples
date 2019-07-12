from py4design import py3dmodel

c = py3dmodel.construct.make_polygon_circle([0,0,0], [1,0,0], 0.0358421906617, division = 10)
py3dmodel.utility.visualise([[c]])