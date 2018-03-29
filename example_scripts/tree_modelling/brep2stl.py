from py4design import py3dmodel

def calc_topo_edge_min_max_length(occtopo):
    edges = py3dmodel.fetch.topo_explorer(occtopo, "edge")
    min_l = float("inf")
    max_l = float("inf")*-1
    for e in edges:
        lb, ub = py3dmodel.fetch.edge_domain(e)
        length = py3dmodel.calculate.edgelength(lb, ub, e)
        if length > max_l: max_l = length
        if length < min_l: min_l = length
        
    return min_l, max_l

brep_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree8\\result\\tree_interim40.brep"
stl_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\result\\tree_interim40.stl"
occtopo = py3dmodel.utility.read_brep(brep_filepath)
solids = py3dmodel.fetch.topo_explorer(occtopo, "solid")
print len(solids)
'''
minl, maxl = calc_topo_edge_min_max_length(occtopo)
py3dmodel.utility.write_2_stl_gmsh(occtopo, stl_filepath, mesh_dim = 2, min_length = minl, max_length = maxl)
display_2dlist = []
colour_list = []

display_2dlist.append([occtopo])
colour_list.append("BLUE")
#py3dmodel.utility.visualise(display_2dlist, colour_list)
print "DONE"
'''