import trimesh

stl_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree2\\result\\tree_volume.stl"
stl_filepath2 = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree2\\result\\tree_volume_fixed.stl"
mesh = trimesh.load(stl_filepath)
iswatertight =  mesh.is_watertight
print "IS STL FILE WATERTIGHT:", iswatertight
if not iswatertight:
    print trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    
    if not iswatertight:
        trimesh.repair.fill_holes(mesh)
        trimesh.io.export.export_mesh(mesh, stl_filepath2)
    if iswatertight:
        trimesh.io.export.export_mesh(mesh, stl_filepath2)


