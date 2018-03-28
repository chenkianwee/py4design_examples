#tree_faces = py3dmodel.construct.simple_mesh(tree_solid)

#tree_shell_list = py3dmodel.construct.sew_faces(tree_faces)
#print len(tree_shell_list)
#tree_shell, smaller_shell = choose_bigger_shell(tree_shell_list)
#
#is_shell_closed = py3dmodel.calculate.is_shell_closed(tree_shell)
#
#py3dmodel.utility.visualise([[tree_shell]], ["BLUE"])
#
#print "IS THE TREE SOLID CLOSED?", is_shell_closed
#
#tree_faces = py3dmodel.fetch.topo_explorer(tree_shell, "face")
#tree_faces2 = []
#for tf in tree_faces:
#    pts = py3dmodel.fetch.points_frm_occface(tf)
#    if len(pts)>3:
#        print "MORE THAN 3 1", len(pts)
#        n1 = py3dmodel.calculate.face_normal(tf)
#        #tf_faces = py3dmodel.construct.simple_mesh(tf)
#        tf_faces = py3dmodel.construct.triangulate_face(tf)
#        for tff in tf_faces:
#            tff_pts = py3dmodel.fetch.points_frm_occface(tff)
#            n_tff_pts = len(tff_pts)
#            print n_tff_pts
#            if n_tff_pts == 3:
#                n2 = py3dmodel.calculate.face_normal(tff)
#                angle = py3dmodel.calculate.angle_bw_2_vecs(n1,n2)
#                if angle > 150:
#                    tff = py3dmodel.modify.reverse_face(tff)
#                    tree_faces2.append(tff)
#                else:
#                    tree_faces2.append(tff)
#    
#    if len(pts) == 3:
#        tree_faces2.append(tf)
#        
#    if len(pts)<3:
#        print "LESS THAN 3"
#        #py3dmodel.utility.visualise([[tf]], ["RED"])
#        
#shell_list2 = py3dmodel.construct.sew_faces(tree_faces2)
#is_shell_closed = py3dmodel.calculate.is_shell_closed(shell_list2[0])

# Script taken from doing the needed operation
# (Filters > Remeshing, Simplification and Reconstruction >
# Quadric Edge Collapse Decimation, with parameters:
# 0.9 percentage reduction (10%), 0.3 Quality threshold (70%)
# Target number of faces is ignored with those parameters
# conserving face normals, planar simplification and
# post-simplimfication cleaning)
# And going to Filter > Show current filter script

filter_script_mlx = """<!DOCTYPE FilterScript>
<FilterScript>
 <filter name="Simplification: Quadric Edge Collapse Decimation">
  <Param type="RichInt" value="1448" name="TargetFaceNum"/>
  <Param type="RichFloat" value="0.6" name="TargetPerc"/>
  <Param type="RichFloat" value="0.3" name="QualityThr"/>
  <Param type="RichBool" value="true" name="PreserveBoundary"/>
  <Param type="RichFloat" value="1" name="BoundaryWeight"/>
  <Param type="RichBool" value="true" name="PreserveNormal"/>
  <Param type="RichBool" value="true" name="PreserveTopology"/>
  <Param type="RichBool" value="true" name="OptimalPlacement"/>
  <Param type="RichBool" value="true" name="PlanarQuadric"/>
  <Param type="RichBool" value="false" name="QualityWeight"/>
  <Param type="RichBool" value="true" name="AutoClean"/>
  <Param type="RichBool" value="false" name="Selected"/>
 </filter>
</FilterScript>

"""

def create_tmp_filter_file(result_dir, filename='filter_file_tmp.mlx'):
    tmp_script = os.path.join(result_dir, filename)
    with open(tmp_script, 'w') as f:
        f.write(filter_script_mlx)
    return tmp_script


def reduce_faces(in_file, out_file, filter_script_path, meshlabserver_dir ):
    # Add input mesh
    mcommand = os.path.join(meshlabserver_dir,"meshlabserver")
    command = mcommand + " -i " + in_file
    # Add the filter script
    command += " -s " + filter_script_path
    # Add the output filename and output flags
    command += " -o " + out_file
    # Execute command
    print "Going to execute: " + command
    #os.chdir(meshlabserver_dir)
    output = subprocess.check_output(command, shell=True)
    last_line = output.splitlines()[-1]
    print
    print "Done:"
    print in_file + " > " + out_file + ": " + last_line
    
stl_file_simplified = os.path.join(result_dir, "tree_volume_simplified.stl")
meshlabserver_dir = "C:\\Program Files\\VCG\\MeshLab"
filter_script_path = create_tmp_filter_file(result_dir)
reduce_faces(stl_file, stl_file_simplified, filter_script_path, meshlabserver_dir)

#for writing out stuff
fused_list2 = []
fs_face_list = []
fs_cnt = 0
for fs in fused_list:
    print "#===================================="
    print "THIS IS SOLID", fs_cnt
    
    fl = py3dmodel.fetch.topo_explorer(fs,"face")
    fl = triangulate_faces(fl)    
    sl_shells = py3dmodel.construct.sew_faces(fl) #sewing changes the individual faces
    sl_shell, other_shells = choose_bigger_shell(sl_shells)
    is_it_closed = py3dmodel.calculate.is_shell_closed(sl_shell)
    
    if is_it_closed == False:
        print "THE SHELL IS NOT CLOSED"
        repaired_shell_info = fill_holes(sl_shell)
        if repaired_shell_info !=None:
            print "THE SHELL HAS BEEN REPAIRED"
            fl2 = repaired_shell_info[1]
            is_3 = check_face_3_sided(fl2)
            print "ARE FACES ALL 3 SIDED AFTER REPAIRING", is_3
            fs_face_list.extend(fl2)
            
            fl_cmpd = py3dmodel.construct.make_compound(fl2)
            py3dmodel.utility.write_2_stl2(fl_cmpd, os.path.join(result_dir, "descending_open_shell" + str(fs_cnt)+".stl"))
            os_cmpd = py3dmodel.construct.make_compound(other_shells)
            py3dmodel.utility.write_2_stl2(os_cmpd, os.path.join(result_dir, "descending_other_shells"+ str(fs_cnt)+".stl"))
            
            repaired_shell = repaired_shell_info[0]
            fs2 = make_fix_solid(repaired_shell)
            fused_list2.append(fs2)
        else:
            non_bool_list.append(fs)
    else:
        fs_face_list.extend(fl)
        fs2 = make_fix_solid(sl_shell)
        fused_list2.append(fs2)
        
    fs_cnt+=1
    
print "#======================"
print "MESHING THE SOLID ..." 
print "#======================"
#tree_faces2 = py3dmodel.construct.simple_mesh(tree_solid, linear_deflection = linr_dfl, angle_deflection = angle_dfl)
#ensure all faces have only 3 vertices 
tree_faces2 = py3dmodel.fetch.topo_explorer(tree_solid, "face")
tree_faces2 = triangulate_faces(tree_faces2)

#just to check if the faces match up again
tree_shell_list2 = py3dmodel.construct.sew_faces(tree_faces2)
n_tree_shells2 = len(tree_shell_list2)
tree_shell2, non_selected_shell_list2 = choose_bigger_shell(tree_shell_list2)
is_shell_closed2 = py3dmodel.calculate.is_shell_closed(tree_shell2)

print "NFACES BEFORE MESHED:", len(tree_faces), "NFACES AFTER MESHED:", len(tree_faces2)
print "NUMBER OF TREE SHELL AFTER MESHING", n_tree_shells2
print "IS THE TREE SOLID STILL CLOSED AFTER MESHING?", is_shell_closed2
print "STRAY SOLIDS FOR THE TREE:", len(non_bool_list)
    
def triangulate_faces(occface_list):
    tri_face_list = []
    for face in occface_list:
        pyptlist = py3dmodel.fetch.points_frm_occface(face)
        npts = len(pyptlist)
        n1 = py3dmodel.calculate.face_normal(face)
        if npts > 3:
            recon_faces_tri = py3dmodel.construct.simple_mesh(face)
            for rft in recon_faces_tri:
                n2 = py3dmodel.calculate.face_normal(rft)
                angle = py3dmodel.calculate.angle_bw_2_vecs(n1,n2)
                if angle > 170:
                    rft = py3dmodel.modify.reverse_face(rft)
                    tri_face_list.append(rft)
                else:
                    tri_face_list.append(rft)
                    
        elif npts == 3:
            new_face = py3dmodel.construct.make_polygon(pyptlist)
            n2 = py3dmodel.calculate.face_normal(new_face)
            angle = py3dmodel.calculate.angle_bw_2_vecs(n1,n2)
            if angle > 170:
                new_face = py3dmodel.modify.reverse_face(new_face)
                tri_face_list.append(new_face)
            else:
                tri_face_list.append(new_face)
            
    return tri_face_list

def check_face_3_sided(occface_list):
    print "TOTAL NUMBER OF FACES:", len(occface_list)
    is_3_sided = True
    for face in occface_list:
        pyptlist = py3dmodel.fetch.points_frm_occface(face)
        npts = len(pyptlist)
        if npts > 3:
            is_3_sided = False
            print "THIS FACE HAS", npts
            
    return is_3_sided

trunk_shell = py3dmodel.fetch.topo_explorer(trunk_solid, "shell")[0]
branch_faces = []
for b in vf_fused_list:
    bshell = py3dmodel.fetch.topo_explorer(b, "shell")[0]
    #first remove the faces from the trunk shell
    diff1 = py3dmodel.construct.boolean_difference(trunk_shell, b)
    #then remove the faces from the bshell
    diff2 = py3dmodel.construct.boolean_difference(bshell, trunk_solid)
    tree_faces = py3dmodel.fetch.topo_explorer(diff1, "face")
    tree_faces2 = py3dmodel.fetch.topo_explorer(diff2, "face")
    tree_faces.extend(tree_faces2)
    tree_shells = py3dmodel.construct.sew_faces(tree_faces)
    n_tree_shells = len(tree_shells)
    if n_tree_shells > 1:
        print "the boolean diff did not work, more than one shell is produced:", n_tree_shells, "produced"
        non_bool_list.append(b)
    else:
        is_shell_closed1 = py3dmodel.calculate.is_shell_closed(tree_shells[0])
        if is_shell_closed1:
            trunk_shell = diff1
            branch_faces.extend(tree_faces2)
        else:
            print "the shell is not closed, fixing the shell ... ..."
            #try to fix the open shell
            closed_shell_list = fill_holes(tree_shells[0])
            if closed_shell_list != None:
                filled_holes = closed_shell_list[2]
                trunk_shell = diff1
                branch_faces.extend(filled_holes)
                branch_faces.extend(tree_faces2)
            else:
                non_bool_list.append(b)
            
            
trunk_faces = py3dmodel.fetch.topo_explorer(trunk_shell, "face")
tree_faces = []
tree_faces.extend(branch_faces)
tree_faces.extend(trunk_faces)

tree_shell_list = py3dmodel.construct.sew_faces(tree_faces)
tree_shell, non_selected_shell_list = choose_bigger_shell(tree_shell_list)
non_bool_list.extend(non_selected_shell_list)

is_shell_closed = py3dmodel.calculate.is_shell_closed(tree_shell)
tree_solid = py3dmodel.construct.make_solid(tree_shell)
tree_solid = py3dmodel.modify.fix_close_solid(tree_solid)