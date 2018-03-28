import os 
import time
import math
import subprocess

#import trimesh

from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE NODE LIST FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
#mtg_file = os.path.join(parent_path, "example_files","mtg", "tree9.txt" )

tree_name = "tree8"
mtg_file = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\mtg\\" + tree_name + ".txt"
result_dir = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\" + tree_name + "\\result"
'''mtg_file = "C://file2analyse.txt"'''

#================================================================================
#HARD CODED PARAMETERS
#================================================================================ 
angle_threshold = 60
rad_extension_factor = 0.1
circle_division = 10
vol_percent = 0.000000005
max_branch_order = 10
linear_deflection = 5
angle_deflection = 5
time1 = time.time()
#================================================================================
#FUNCTIONS 
#================================================================================    
def find_mtg_pt_row(edge_lines_list, pt_name):
    for ell in edge_lines_list:
        if pt_name == ell[0]:
            srow = ell
            break
    return srow

def find_mtg_row_of_parent_pt(edge_lines_list, parent_pt_name):
    row = []
    for ell in edge_lines_list:
        if parent_pt_name == ell[1]:
            row.append(ell)
    return row

def get_start_end_pt(mtg_row, edge_lines_list):
    start_pt_name = mtg_row[1]
    end_pt = (float(mtg_row[3]), float(mtg_row[4]), float(mtg_row[5]))
    radius = float(mtg_row[6])

    #find the start point row
    srow = find_mtg_pt_row(edge_lines_list, start_pt_name)
    start_pt = (float(srow[3]), float(srow[4]), float(srow[5]))
    return start_pt, end_pt, radius, srow

def choose_next_branch(erows):
    if erows:
        rads = []
    
        for erow in erows:
            rads.append(float(erow[6]))
            if erow[2] == "<":
                chosen_erow = erow
                return chosen_erow
            
        max_rad = max(rads)
        max_index = rads.index(max_rad)
        chosen_erow = erows[max_index]
        return chosen_erow
    else:
        return []
    
def extrude_branch(start_pt, end_pt, radius, cap = False):
    if start_pt != end_pt:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec1, radius, division = circle_division)
        extrude = py3dmodel.construct.make_loft([bottom_pipe,top_pipe])
        loft_face_list = py3dmodel.construct.simple_mesh(extrude, linear_deflection = linear_deflection, angle_deflection =angle_deflection)
        #loft_face_list = py3dmodel.fetch.topo_explorer(extrude, "face")
        loft_face_list.append(top_pipe)
        if cap == True:
            loft_face_list.append(bottom_pipe)
            extrude = py3dmodel.construct.sew_faces(loft_face_list)
            if len(extrude) >1:
                print "something went wrong at the construction of branches"
            solid = py3dmodel.construct.make_solid(extrude[0])
            solid = py3dmodel.modify.fix_close_solid(solid)
            return solid
        else:
            extrude = py3dmodel.construct.sew_faces(loft_face_list)
            if len(extrude) >1:
                print "something went wrong at the construction of branches"
            return extrude[0]
    else:
        return None
    
def loft_with_consc_branches(start_pt, end_pt, end_pt2, radius, radius2, cap = False):
    if start_pt != end_pt and end_pt != end_pt2:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        vec2 = py3dmodel.construct.make_vector(end_pt, end_pt2)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        pyvec2 = py3dmodel.modify.normalise_vec(vec2)
    
        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec2, radius2, division = circle_division)
        
        loft = py3dmodel.construct.make_loft([bottom_pipe,top_pipe], rule_face=True)
        face_list = py3dmodel.construct.simple_mesh(loft, linear_deflection = linear_deflection, angle_deflection =angle_deflection)
        #face_list = py3dmodel.fetch.topo_explorer(loft, "face")
        if cap == True:
            face_list.append(bottom_pipe)
            face_list.append(top_pipe)
            loft = py3dmodel.construct.sew_faces(face_list)
            if len(loft) >1:
                print "something went wrong at the construction of branches lofting function"
            loft = py3dmodel.construct.make_solid(loft[0])
            loft = py3dmodel.modify.fix_close_solid(loft)
            
            return loft
        else:
            loft = py3dmodel.construct.sew_faces(face_list)
            if len(loft) >1:
                print "something went wrong at the construction of branches lofting function"
            return loft[0]
    else:
        return None
    
def trace_2_root(mtg_row, edge_lines_list):
    lineage_list = []
    branching_order = 0
    curr_row = mtg_row
    start_pt_name = curr_row[1]
    while start_pt_name != "":
        parent_row = find_mtg_pt_row(edge_lines_list, start_pt_name)
        sibling_rows = find_mtg_row_of_parent_pt(edge_lines_list, parent_row[0])
        chosen_row = choose_next_branch(sibling_rows)
        if chosen_row != curr_row: branching_order +=1
        lineage_list.append(parent_row)
        curr_row = parent_row
        start_pt_name = curr_row[1]
        
    return branching_order
    
def construct_cylinder_frm_mtg_row(mtg_row, edge_lines_list):
    branch_dict = {}
    end_pt_name = mtg_row[0]
    start_pt_name = mtg_row[1]
    start_pt, end_pt, radius, srow = get_start_end_pt(mtg_row, edge_lines_list)
    
    branching_order = trace_2_root(mtg_row, edge_lines_list)
    
    #from the end point find the number of edges connected to this branch
    erows = find_mtg_row_of_parent_pt(edge_lines_list, end_pt_name)
    children_list = []
    for erow in erows:
        children_list.append(erow[0])
    #choose the next row 
    chosen_row = choose_next_branch(erows)
    #measure the angle of bending for the branches
    if chosen_row:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)
        radius2 = float(chosen_row[6])
        end_pt2 = (float(chosen_row[3]), float(chosen_row[4]), float(chosen_row[5]))
        vec2 = py3dmodel.construct.make_vector(end_pt, end_pt2)
        pyvec2 = py3dmodel.modify.normalise_vec(vec2)
        angle = py3dmodel.calculate.angle_bw_2_vecs(pyvec1, pyvec2)
        if angle < angle_threshold:
            ext_b = loft_with_consc_branches(start_pt, end_pt, end_pt2, radius, radius2, cap = False)
            cut_geom = loft_with_consc_branches(start_pt, end_pt, end_pt2, radius, radius2, cap = True)
        else:
            new_end_pt = py3dmodel.modify.move_pt(end_pt, pyvec1, radius + (rad_extension_factor*radius))
            ext_b = extrude_branch(start_pt, new_end_pt, radius)
            cut_geom = extrude_branch(start_pt, new_end_pt, radius, cap = True)
    else:
        angle = 180
        ext_b = extrude_branch(start_pt, end_pt, radius)
        cut_geom = extrude_branch(start_pt, end_pt, radius, cap = True)
    
    #find all the branches that share the same starting point as this branch 
    sibling_list = []
    sibling_rows = find_mtg_row_of_parent_pt(edge_lines_list, start_pt_name)
    for sibling in sibling_rows:
        if sibling[0] != end_pt_name:
            sibling_list.append(sibling[0])
    
    #find the parent branch     
    branch_dict["end_pt_name"] = end_pt_name
    branch_dict["children"] = children_list
    branch_dict["siblings"] = sibling_list
    branch_dict["parent"] = start_pt_name
    branch_dict["geometry"] = ext_b
    branch_dict["cut_geometry"] = cut_geom
    branch_dict["start_pt"] = start_pt
    branch_dict["end_pt"] = end_pt
    branch_dict["radius"] = radius
    branch_dict["is_split"] = mtg_row[2]
    branch_dict["angle"] = angle
    branch_dict["order"] = branching_order
    
    if chosen_row:
        branch_dict["connection"] = chosen_row[0]
    else:
        branch_dict["connection"] = None
    return branch_dict

def get_branch_dict(end_pt_name_list, dict_list):
    get_list = []
    for bdict in dict_list:
        end_pt_name = bdict["end_pt_name"]
        if end_pt_name in end_pt_name_list:
            get_list.append(bdict)
            if len(get_list) == len(end_pt_name_list):
                break
    return get_list

def redraw_occfaces(occfaces):
    recon_faces = []
    for face in occfaces:
        wires = py3dmodel.fetch.wires_frm_face(face)
        if len(wires) > 1:
            recon_faces_tri = py3dmodel.construct.simple_mesh(face, linear_deflection = linear_deflection, angle_deflection =angle_deflection)
            recon_faces.extend(recon_faces_tri)  
        else:
            pyptlist = py3dmodel.fetch.points_frm_occface(face)
            #recon_face = py3dmodel.construct.make_polygon(pyptlist)
            #recon_faces.append(recon_face)  
            if len(pyptlist) >= 3:
               recon_face = py3dmodel.construct.make_polygon(pyptlist)
               recon_faces.append(recon_face)  
    return recon_faces

def create_base_polygon(branch_dict):
    start_pt = branch_dict["start_pt"]
    end_pt = branch_dict["end_pt"]
    vec = py3dmodel.construct.make_vector(start_pt, end_pt)
    pyvec = py3dmodel.modify.normalise_vec(vec)
    radius = branch_dict["radius"]
    base_polygon = py3dmodel.construct.make_polygon_circle(start_pt, pyvec, radius, division = circle_division )
    return base_polygon

def face2solids(geom_list):
    cmpd = py3dmodel.construct.make_compound(geom_list)
    face_list = py3dmodel.fetch.topo_explorer(cmpd, "face")
    face_list = redraw_occfaces(face_list)
    shell_list = py3dmodel.construct.sew_faces(face_list)
    solid_list = []
    non_solid_list = []
    scnt = 0
    for shell in shell_list:
        shell = py3dmodel.modify.fix_shell_orientation(shell)
        is_closed = py3dmodel.calculate.is_shell_closed(shell)
        if is_closed:
            solid = py3dmodel.construct.make_solid(shell)
            solid = py3dmodel.modify.fix_close_solid(solid)
            solid_list.append(solid)
        else:
            sfaces = py3dmodel.fetch.topo_explorer(shell, "face")
            hole_faces = py3dmodel.construct.merge_faces(sfaces)
            
            sfaces.extend(hole_faces)
            shell_list2 = py3dmodel.construct.sew_faces(sfaces)
            py3dmodel.utility.visualise([sfaces, hole_faces], ["BLUE", "RED"])
            if len(shell_list2) == 1:
                is_closed2 = py3dmodel.calculate.is_shell_closed(shell_list2[0])
                print is_closed2
                if is_closed2:
                    solid = py3dmodel.construct.make_solid(shell)
                    solid = py3dmodel.modify.fix_close_solid(solid)
                    solid_list.append(solid)
                else:
                    non_solid_list.append(shell)
                    
            else:
                non_solid_list.append(shell)
        scnt+=1
    return solid_list, non_solid_list

def multiple_bool_fuse(solid_list, progress_filepath = None, result_dir = None):
    fused = solid_list[0]
    solid_list2 = solid_list[:]
    del solid_list2[0]
    nsolids = len(solid_list2)
    interim_cnt = int(math.ceil((nsolids/20.0)/10))*10
    bool_list = []
    non_bool_list = []
    if progress_filepath != None:
        progress_file = open(progress_filepath, "w")
        progress_file.write("")
        progress_file.close()
    s2cnt = 0
    for solid2 in solid_list2:
        if progress_filepath != None:
            progress_file = open(progress_filepath, "a")
            str0 = str(s2cnt) + "\n"
            str1 = "FUSED:" +  str(len(bool_list))  +  "/" +  str(nsolids) + "\n"
            str2 = "NON_FUSABLE " +  str(len(non_bool_list)) + "\n"
            progress_file = open(progress_filepath, "a")
            progress_file.write(str0 + str1 +str2)
            progress_file.close()

        if s2cnt not in bool_list:
            #py3dmodel.utility.visualise([[fused],[solid2]], ["RED","GREEN"])
            fused2 = py3dmodel.construct.boolean_fuse(fused, solid2)
            #shell_list2 = py3dmodel.fetch.topo_explorer(fused2, "shell")
            #nshells = len(shell_list2)
            face_list = py3dmodel.fetch.topo_explorer(fused2, "face")
            face_list = redraw_occfaces(face_list)
            shell_list2 = py3dmodel.construct.sew_faces(face_list)
            nshells = len(shell_list2)
            
            if nshells > 1:
                print "MORE THAN 1 SHELL IS PRODUCED"
                if solid2 not in non_bool_list: non_bool_list.append(solid2)
                s2cnt+=1
                continue

            shell2 = shell_list2[0]
            is_closed2 = py3dmodel.calculate.is_shell_closed(shell2)
            #py3dmodel.utility.visualise([[shell2]], ["RED","GREEN"])
            
            if is_closed2:
                vol1 = py3dmodel.calculate.solid_volume(fused)
                solid_vol = py3dmodel.construct.make_solid(shell2)
                solid_vol = py3dmodel.modify.fix_close_solid(solid_vol)
                vol2 = py3dmodel.calculate.solid_volume(solid_vol)
                
                if vol2 >= vol1:
                    fused = solid_vol
                    if solid2 in non_bool_list: non_bool_list.remove(solid2)
                    bool_list.append(s2cnt)
                    
                if vol2<vol1:
                    if solid2 not in non_bool_list: non_bool_list.append(solid2)
                    
                if result_dir!=None:
                    if s2cnt%interim_cnt == 0 or s2cnt == nsolids-1:
                            #tri_faces = py3dmodel.fetch.topo_explorer(fused, "face")
                            #shell_list = py3dmodel.construct.sew_faces(tri_faces)
                            #is_closed1 = py3dmodel.calculate.is_shell_closed(shell_list[0])
                            #print "to check if the written geoms are closed", is_closed1, "numshells", len(shell_list)                    
                            # Export to STL
                            interim_file = os.path.join(result_dir, "tree_interim" + str(s2cnt) + ".stl")
                            py3dmodel.utility.write_2_stl(fused, interim_file)
                    
            else:
                print "THE FUSED SHELL IS NOT CLOSED"
                if solid2 not in non_bool_list: non_bool_list.append(solid2)
                #py3dmodel.utility.visualise([[fused2]])
                
        s2cnt+=1
        
    solid_list3 = py3dmodel.fetch.topo_explorer(fused, "solid")
    return solid_list3, non_bool_list

def multiple_bool_fuse2(solid_list1, solid_list2):
    tip_solids = solid_list1
    tip_solids2 = tip_solids[:]
    
    tip_parent_solids = solid_list2[:]
    
    tip_cnt = 0
    for tip in tip_solids:
        tp_cnt = 0
        for tp in tip_parent_solids:
            fused = py3dmodel.construct.boolean_fuse(tp, tip)
            solids = py3dmodel.fetch.topo_explorer(fused, "solid")
            if len(solids) == 1:
                face_list = py3dmodel.fetch.topo_explorer(solids[0], "face")
                face_list = redraw_occfaces(face_list)
                shells = py3dmodel.construct.sew_faces(face_list)
                
                if len(shells) > 1:
                    #print "something is wrong at multiple bool fuse 2"
                    chosen_shell, other_shells = choose_bigger_shell(shells)
                    #py3dmodel.utility.visualise([[chosen_shell], other_shells], ["BLUE", "RED"])
                else:
                    chosen_shell = shells[0]
                    
                is_shell_closed = py3dmodel.calculate.is_shell_closed(chosen_shell)
                if not is_shell_closed:
                    
                    print "something is wrong at multiple bool fuse 2, the resultant shells are not closed"
                    break
                
                fused_solid = py3dmodel.construct.make_solid(chosen_shell)
                fused_solid = py3dmodel.modify.fix_close_solid(fused_solid)
                tip_parent_solids[tp_cnt] = fused_solid
                tip_solids2.remove(tip)
                break
            tp_cnt+=1
        tip_cnt+=1
        
    return tip_parent_solids, tip_solids2

def choose_bigger_shell(shell_list):
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

def get_cut_geom_from_dict(dict_list):
    get_geom_list = []
    for bdict in dict_list:
        geom = bdict["cut_geometry"]
        get_geom_list.append(geom)
    return get_geom_list

def multiple_bool_diff(geom2cutfrom, cut_geom):
    cuted_geom = geom2cutfrom
    if cuted_geom != None:
        cface_list = py3dmodel.fetch.topo_explorer(cuted_geom, "face")
        #cface_list = redraw_occfaces(cface_list)
        cface_list2 = []
        cnt = 0
        for cface in cface_list:
            cface2 = py3dmodel.construct.boolean_difference(cface, cut_geom)
            cfaces2 = py3dmodel.fetch.topo_explorer(cface2, "face")
            if cfaces2:
                cfaces2 = redraw_occfaces(cfaces2)
                cface_list2.extend(cfaces2)
            cnt+=1

        if cface_list2:
            shell_list = py3dmodel.construct.sew_faces(cface_list2)
            cuted_geom = py3dmodel.construct.make_compound(shell_list)
        else:
            cuted_geom = None
                
    return cuted_geom

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
    
#========================================================================================
#FUNCTIONS 
#========================================================================================
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
    
#stl_file_simplified = os.path.join(result_dir, "tree_volume_simplified.stl")
#meshlabserver_dir = "C:\\Program Files\\VCG\\MeshLab"

dae_file = os.path.join(result_dir, "tree_volume.dae")
stl_file = os.path.join(result_dir, "tree_volume.stl")
stl_file_non_bool = os.path.join(result_dir, "tree_volume_stray.stl")
progress_filepath = os.path.join(result_dir, "progress.txt")
    
print "#========================="
print "READING THE MTG FILE ..." 
print "#========================="
display_2dlist = []
colour_list = []
mf = open(mtg_file, "r")
lines = mf.readlines()
edge_lines = lines[3:]
edge_lines_list = []
minz = float("inf")
for el in edge_lines:
    el = el.replace("\n","")
    el_list = el.split("\t")
    z = float(el_list[5])
    if z<minz:
        minz = z
    edge_lines_list.append(el_list)
    
print "#=========================================="
print "CONSTRUCTING THE BRANCHING DICTIONARY ..." 
print "#=========================================="
#a list of dictionaries that documents the tree architecture
branch_dict_list = []
edge_list = []
max_order = float("inf")*-1 
for ell in edge_lines_list:
    #check if it is an edge
    if ell[1] !="":
        branch_dict = construct_cylinder_frm_mtg_row(ell, edge_lines_list)
        ext_b = branch_dict["geometry"] 
        edge = py3dmodel.construct.make_edge(branch_dict["start_pt"], branch_dict["end_pt"])
        order = branch_dict["order"]
        radius = branch_dict["radius"]
        
        if order > max_order: max_order = order
        
        edge_list.append(edge)
        branch_dict_list.append(branch_dict)

print "#==================================="
print "CONSTRUCTING THE BRANCH SOLIDS ..." 
print "#==================================="
bool_geom_list = []
branch_dict_list2 = branch_dict_list[:]

order_list = []
for _ in range(max_order+1):
    order_list.append([])
    
for branch_dict in branch_dict_list2:
    end_pt_name = branch_dict["end_pt_name"]
    bgeom = branch_dict["geometry"]
    parent = branch_dict["parent"]
    parent_dict = get_branch_dict([parent], branch_dict_list)
    
    angle = branch_dict["angle"]
    order = branch_dict["order"]
    
    connection = branch_dict["connection"]
    if parent_dict == []:
        #this must be the root trunk 
        base_polygon = create_base_polygon(branch_dict)
        order_list[order].append(base_polygon)
        
    if parent_dict:
        parent_dict = parent_dict[0]
        parent_angle = parent_dict["angle"]
        parent_connection = parent_dict["connection"]
        if parent_connection != end_pt_name:
            #this means this branch and the parent branch is at a 90 degree bend
            base_polygon = create_base_polygon(branch_dict)
            order_list[order].append(base_polygon)
        if parent_connection == end_pt_name and parent_angle >= angle_threshold:
            cut_geom = get_cut_geom_from_dict([parent_dict])[0]
            base_polygon = create_base_polygon(branch_dict)
            bgeom_faces = py3dmodel.fetch.topo_explorer(bgeom, "face")
            bgeom_faces.append(base_polygon)
            bgeom_list = py3dmodel.construct.sew_faces(bgeom_faces)
            
            if len(bgeom_list) > 1:
                print "THE BRANCHES WITH ANGLE MORE THAN THRESHOLD IS NOT FORMING A GOOD SHELL"
            bgeom = bgeom_list[0]

            bgeom = multiple_bool_diff(bgeom, cut_geom)
            
    if angle >= angle_threshold:
        connection_dict_list = get_branch_dict([connection], branch_dict_list)
        
        if connection_dict_list:
            cut_geom = get_cut_geom_from_dict(connection_dict_list)[0]
            bgeom = multiple_bool_diff(bgeom, cut_geom)
            
            connection2 = connection_dict_list[0]["connection"]
            connection_dict_list2 = get_branch_dict([connection2], branch_dict_list)
            if connection_dict_list2:
                cut_geom2 = get_cut_geom_from_dict(connection_dict_list2)[0]
                bgeom = multiple_bool_diff(bgeom, cut_geom2)
            
    if bgeom != None:
        order_list[order].append(bgeom)
print "#============================================="
print "FILTERING THE BRANCHES ACCORDING TO ORDER ..." 
print "#============================================="
non_bool_list = []

order_list = order_list[0:max_branch_order]

f_order_list = []
o_cnt = 0
for o in order_list:
    order_solids, non_solid_list = face2solids(o)
    f_order_list.append(order_solids)
    non_bool_list.extend(non_solid_list)
    print "NUMBER OF SOLIDS IN ORDER" + str(o_cnt), ":", len(order_solids), ", OPEN SOLIDS:", len(non_solid_list)
    o_cnt+=1
    
'''
##========================================================================================
#print "FUSING THE TRUNK..." 
##========================================================================================
##first get the main trunk
trunk_solids = f_order_list[0]
del f_order_list[0]

print "#==========================================="
print "FUSING THE BRANCHES IN DESCENDING ORDER..." 
print "#==========================================="
f_order_list2 = f_order_list
fused_2dlist = []
f_order_list2.reverse()
fused_list = f_order_list2[0]
n_f_order_list = len(f_order_list2)

for fcnt in range(n_f_order_list):
    if  fcnt != n_f_order_list-1:
        fused_list, non_bools = multiple_bool_fuse2(fused_list, f_order_list2[fcnt+1])
        fused_2dlist.append(fused_list)
        non_bool_list.extend(non_bools)
        order_cnt = str(n_f_order_list-fcnt-1)
        print "NUMBER OF FUSED SOLIDS IN ORDER" + order_cnt, ":", len(fused_list), ", STRAY SOLIDS:", len(non_bool_list)

print "#====================================="
print "FUSING THE BRANCHES TO THE TRUNK ..." 
print "#====================================="
#find the maximum solid volume
max_vol = float("inf")*-1
svol_list = []
cnt = 0
for s in fused_list:
    svol = py3dmodel.calculate.solid_volume(s)
    svol_list.append(svol)
    if svol > max_vol: max_vol = svol
    cnt+=1

vol_thres = max_vol*vol_percent
vf_fused_list = []
scnt=0
for s in fused_list:
    svol = svol_list[scnt]
    if svol >= vol_thres: 
        vf_fused_list.append(s)
    else:
        non_bool_list.append(s)
    scnt+=1
    
print "MAXIMUM VOLUME OF A BRANCH (m3):", max_vol
print "VOLUME THRESHOLD (m3):", vol_thres
print "NUMBER OF SOLIDS AFTER VOL FILTER:", len(vf_fused_list)

#trunk_solid = trunk_solid[0]
trunk_solid = trunk_solids[0]
fused_list2 = []
fused_list2.append(trunk_solid)
fused_list2.extend(vf_fused_list)

tree_solid, non_bools = multiple_bool_fuse(fused_list2, progress_filepath = progress_filepath, result_dir = result_dir)
non_bool_list.extend(non_bools)
trunk_face_list = py3dmodel.fetch.topo_explorer(tree_solid[0], "face")
trunk_face_list = redraw_occfaces(trunk_face_list)
tree_shell_list = py3dmodel.construct.sew_faces(trunk_face_list)
n_tree_shells = len(tree_shell_list)
print "NUMBER OF TREE SHELL FROM FUSING", n_tree_shells
if n_tree_shells == 1:
    tree_shell = tree_shell_list[0]
else:
    tree_shell, non_selected_shell_list = choose_bigger_shell(tree_shell_list)
    non_bool_list.extend(non_selected_shell_list)
    
is_shell_closed = py3dmodel.calculate.is_shell_closed(tree_shell)
tree_shell = py3dmodel.modify.simplify_shell(tree_shell)
tree_solid = py3dmodel.construct.make_solid(tree_shell)
tree_solid = py3dmodel.modify.fix_close_solid(tree_solid)

print "IS THE TREE SOLID CLOSED?", is_shell_closed
print "STRAY SOLIDS FOR THE TREE:", len(non_bool_list)

print "#============================================"
print "WRITING THE GEOMETRY TO STL AND COLLADA ..." 
print "#============================================"
py3dmodel.utility.write_2_stl(tree_solid, stl_file, linear_deflection = 0.01, angle_deflection = 0.3)
py3dmodel.export_collada.write_2_collada(dae_file, occface_list = [tree_solid] )
#mesh = trimesh.load(stl_file)
#iswatertight =  mesh.is_watertight
#print "IS STL FILE WATERTIGHT:", iswatertight
#if not iswatertight:
#    print trimesh.repair.fill_holes(mesh)
#    trimesh.repair.fix_normals(mesh)
#    
#    if not iswatertight:
#        trimesh.repair.fill_holes(mesh)
#        trimesh.io.export.export_mesh(mesh, stl_file)
#    if iswatertight:
#        trimesh.io.export.export_mesh(mesh, stl_file)

#filter_script_path = create_tmp_filter_file(result_dir)
#reduce_faces(stl_file, stl_file_simplified, filter_script_path, meshlabserver_dir)

nb_cmpd = py3dmodel.construct.make_compound(non_bool_list)
py3dmodel.utility.write_2_stl(nb_cmpd, stl_file_non_bool, linear_deflection = 0.01, angle_deflection = 0.3)
#========================================================================================================
#visualise
#========================================================================================================
display_2dlist.append([tree_shell])
colour_list.append("BLUE")

display_2dlist.append(non_bool_list)
colour_list.append("RED")
'''

time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
py3dmodel.utility.visualise(display_2dlist, colour_list)