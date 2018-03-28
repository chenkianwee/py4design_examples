from py4design import py3dmodel

def choose_bigger_shell(shell_list):
    if len(shell_list) > 1:
        shell_area_list = []
        for ts in shell_list:
            ts_face_list = py3dmodel.fetch.topo_explorer(ts, "face")
            shell_area = 0
            for tsf in ts_face_list:
                farea = py3dmodel.calculate.face_area(tsf)
                shell_area = shell_area + farea
            shell_area_list.append(shell_area)
        
        max_s_area = max(shell_area_list)
        s_area_index = shell_area_list.index(max_s_area)
        shell = shell_list[s_area_index]
        del shell_list[s_area_index]
        return shell, shell_list
    else:
        return shell_list[0], []
    
def fill_holes(occshell):
    face_list = py3dmodel.fetch.topo_explorer(occshell, "face")
    hole_faces = py3dmodel.construct.merge_faces(face_list)
    print "looking for holes in the shell ... ...", len(hole_faces), "found"
    print "... ...", len(hole_faces), "faces created"
    
    #py3dmodel.utility.visualise([edges,hole_faces, shell_edges], ["BLACK", "BLUE", "BLACK"])
    face_list.extend(hole_faces)
    shell_list = py3dmodel.construct.sew_faces(face_list)
    if len(shell_list) == 1:
        fixed_shell = shell_list[0]
        is_shell_closed = py3dmodel.calculate.is_shell_closed(fixed_shell)
        if is_shell_closed:
            print "the shell is closed"
            face_list2 = py3dmodel.fetch.topo_explorer(fixed_shell, "face")
            return [fixed_shell, face_list2, hole_faces]
        else:
            print "the shell is not closed, fixing the shell ... failed: cant close shell"
            return None
    else:
        return None
    
def make_fix_solid(occshell):
    solid = py3dmodel.construct.make_solid(occshell)
    fixed_solid = py3dmodel.modify.fix_close_solid(solid)
    return fixed_solid
    
stl_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\result\\tree.stl"
stl_filepath2 = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree9\\result\\tree_fixed.stl"

occtopo = py3dmodel.utility.read_stl(stl_filepath)
face_list = py3dmodel.fetch.topo_explorer(occtopo, "face")
print len(face_list)
new_face_list = []
for f in face_list:
    pyptlist = py3dmodel.fetch.points_frm_occface(f)
    npts = len(pyptlist)
    #face_area = py3dmodel.calculate.face_area(f)
    if npts <3:
        print npts
    else:
        new_face_list.append(f)

cmpd = py3dmodel.construct.make_compound(new_face_list)
py3dmodel.utility.write_2_stl2(cmpd, stl_filepath2)
print "DONE"
'''
shell_list = py3dmodel.construct.sew_faces(new_face_list)
print len(shell_list)
shell, shell_list2 = choose_bigger_shell(shell_list)
closed = py3dmodel.calculate.is_shell_closed(shell)
if closed:
    solid = make_fix_solid(shell)
    

    py3dmodel.utility.visualise([[solid]], ["BLUE"])


import trimesh
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
'''