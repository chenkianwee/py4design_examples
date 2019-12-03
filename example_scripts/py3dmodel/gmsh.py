from py4design import py3dmodel
#TODO FIX
# First example, a simple torus
#aShape = py3dmodel.utility.read_stl("C:\\Users\\chenkianwee\\Desktop\\ring.stl")
c1 = py3dmodel.construct.make_polygon_circle((0,0,0),(0,0,1), 0.003)
extrude = py3dmodel.construct.extrude(c1, (0,1,1), 0.03)
extrude2 = py3dmodel.construct.extrude(c1, (0,-1,1), 0.01)
extrude3 = py3dmodel.construct.extrude(c1, (-1,-1,1), 0.01)
aShape = py3dmodel.construct.boolean_fuse(extrude, extrude3)
cmpd = py3dmodel.construct.make_compound([extrude2, extrude3])

stl_filepath = "C:\\Users\\chenkianwee\\Desktop\\test.stl"
meshed = py3dmodel.utility.write_2_stl_gmsh(cmpd, stl_filepath)
cmpd = py3dmodel.utility.read_brep("C:\\Users\\chenkianwee\\Desktop\\test.brep")
py3dmodel.utility.visualise([[cmpd]], ["BLUE"])