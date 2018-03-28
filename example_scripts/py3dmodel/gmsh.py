from py4design import py3dmodel

# First example, a simple torus
aShape = py3dmodel.utility.read_stl("F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree2\\result\\order0.stl")
c1 = py3dmodel.construct.make_polygon_circle((0,0,0),(0,0,1), 0.003)
extrude = py3dmodel.construct.extrude(c1, (0,1,1), 0.03)
extrude2 = py3dmodel.construct.extrude(c1, (0,-1,1), 0.01)
extrude3 = py3dmodel.construct.extrude(c1, (-1,-1,1), 0.01)
aShape = py3dmodel.construct.boolean_fuse(extrude, extrude3)
cmpd = py3dmodel.construct.make_compound([extrude2, extrude3])

stl_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree2\\result\\tree_volume_test.stl"
meshed = py3dmodel.utility.write_2_stl_gmsh(cmpd, stl_filepath)
print meshed
py3dmodel.utility.visualise([[meshed]], ["BLUE"])