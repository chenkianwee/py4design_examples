from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.Core.gp import gp_Pnt
from OCC.Core.SMESH import SMESH_Gen, SMESH_MeshVSLink
from OCC.Core.StdMeshers import StdMeshers_MaxElementVolume, StdMeshers_QuadrangleParams, StdMeshers_MaxElementArea, StdMeshers_LengthFromEdges, StdMeshers_Propagation, StdMeshers_ProjectionSource2D, StdMeshers_AutomaticLength, StdMeshers_Quadrangle_2D, StdMeshers_Projection_2D, StdMeshers_QuadraticMesh, StdMeshers_UseExisting_2D, StdMeshers_Prism_3D, StdMeshers_Arithmetic1D, StdMeshers_TrianglePreference, StdMeshers_Regular_1D, StdMeshers_Projection_3D,StdMeshers_MEFISTO_2D
from OCC.Core.MeshVS import MeshVS_Mesh, MeshVS_MeshPrsBuilder
from OCC.Core.SMDSAbs import SMDSAbs_Face
from py4design import py3dmodel
from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

# First create a 'complex' shape (actually a boolean op between a box and a cylinder)
print('Creating geometry ...')
#c1 = py3dmodel.construct.make_polygon_circle((0,0,0),(0,0,1), 0.003)
#extrude = py3dmodel.construct.extrude(c1, (0,1,1), 0.03)
#extrude2 = py3dmodel.construct.extrude(c1, (0,-1,1), 0.01)
#extrude3 = py3dmodel.construct.extrude(c1, (-1,-1,1), 0.01)
#aShape = py3dmodel.construct.boolean_fuse(extrude, extrude3)
#tri_faces = py3dmodel.construct.simple_mesh(aShape)
#aShape = py3dmodel.construct.sew_faces(tri_faces)[0]

aShape = py3dmodel.utility.read_stl("F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree2\\result\\order0.stl")
#aShape = py3dmodel.construct.make_compound([aShape,extrude3])
#py3dmodel.utility.visualise([[aShape]], ["BLUE"])
print ('Done.')

# Create the Mesh
print('Creating mesh ...')
aMeshGen = SMESH_Gen()
aMesh = aMeshGen.CreateMesh(0, True)

print('Done.')

print('Adding hypothesis and algorithms ...')
# 1D
an1DHypothesis = StdMeshers_Arithmetic1D(0, 0, aMeshGen)#discretization of the wire
an1DHypothesis.SetLength(0.05, False) #the smallest distance between 2 points
an1DHypothesis.SetLength(1, True) # the longest distance between 2 points

#an1DHypothesis = StdMeshers_AutomaticLength(0, 0, aMeshGen)
#an1DHypothesis.SetFineness(0.0)
an1DAlgo = StdMeshers_Regular_1D(1, 0, aMeshGen) # interpolation

# 2D
#a2dHypothseis = StdMeshers_QuadraticMesh(2, 0, aMeshGen)
#a2dHypothseis = StdMeshers_TrianglePreference(2, 0, aMeshGen)  # define the boundary
#a2dHypothseis = StdMeshers_ProjectionSource2D(2, 0, aMeshGen)
#a2dHypothseis = StdMeshers_LengthFromEdges(2,0,aMeshGen)
a2dHypothseis = StdMeshers_MaxElementArea(2,0,aMeshGen)
#a2dHypothseis = StdMeshers_QuadrangleParams(2,0,aMeshGen)

#a2dAlgo = StdMeshers_Quadrangle_2D(3, 0, aMeshGen)
a2dAlgo = StdMeshers_MEFISTO_2D(3, 0, aMeshGen)
#a2dAlgo = StdMeshers_Projection_2D(3, 0, aMeshGen)

# 3D: Just uncomment the line to use the volumic mesher you want

a3dHypothesis = StdMeshers_MaxElementVolume(4, 0, aMeshGen)
a3dAlgo = StdMeshers_Projection_3D(5, 0, aMeshGen)

#Calculate mesh
aMesh.ShapeToMesh(aShape)

#Assign hyptothesis to mesh
#aMesh.AddHypothesis(aShape, 0)
#aMesh.AddHypothesis(aShape, 1)
#aMesh.AddHypothesis(aShape, 2)
#aMesh.AddHypothesis(aShape, 3)
aMesh.AddHypothesis(aShape, 4)
aMesh.AddHypothesis(aShape, 5)
print('Done.')

#Compute the data
print('Computing mesh ...')
aMeshGen.Compute(aMesh,aMesh.GetShapeToMesh())
print('Done.')

print(aMesh.NbNodes())
print(aMesh.NbEdges())
print(aMesh.NbFaces())

aMesh.ExportSTL("F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\test.stl", True)
# Display the data
aDS = SMESH_MeshVSLink(aMesh)
aMeshVS = MeshVS_Mesh(True)
DMF = 1 # to wrap!
MeshVS_BP_Mesh1 =  5 # To wrap!

aPrsBuilder = MeshVS_MeshPrsBuilder(aMeshVS.GetHandle(), DMF, aDS.GetHandle(), 0, MeshVS_BP_Mesh1)
aMeshVS.SetDataSource(aDS.GetHandle())
aMeshVS.AddBuilder(aPrsBuilder.GetHandle(), True)

context = display.Context
context.Display(aMeshVS.GetHandle())
context.Deactivate(aMeshVS.GetHandle())
display.FitAll()
start_display()