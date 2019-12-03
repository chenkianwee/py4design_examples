from OCC.Core.TopTools import TopTools_HSequenceOfShape, Handle_TopTools_HSequenceOfShape_Create, TopTools_SequenceOfShape
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

edge1_pts = [gp_Pnt(50.0, 0.0, 0.0), gp_Pnt(0.0, 50.0, 5.0)]
edge1 = BRepBuilderAPI_MakeEdge(edge1_pts[0], edge1_pts[1]).Edge()
edge2_pts = [gp_Pnt(0.0, 50.0, 5.0), gp_Pnt(0.0, 50.0, 0.0)]
edge2 = BRepBuilderAPI_MakeEdge(edge2_pts[0], edge2_pts[1]).Edge()
edge3_pts = [gp_Pnt(50.0, 0.0, 0.0), gp_Pnt(0.0, 50.0, 0.0)]
edge3 = BRepBuilderAPI_MakeEdge(edge3_pts[0], edge3_pts[1]).Edge()

edge_list = [edge1, edge2,edge3]

toptool_seq_shape = TopTools_SequenceOfShape()
for edge in edge_list: 
    toptool_seq_shape.Append(edge)  

edges = TopTools_HSequenceOfShape(toptool_seq_shape)
edges_handle = Handle_TopTools_HSequenceOfShape_Create() #? is this how I can get the handle?