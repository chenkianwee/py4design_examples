import os 
import time
import math

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

vol_percent = 0.0000000005
max_branch_order = 10

#================================================================================
#HARD CODED PARAMETERS
#================================================================================ 
angle_threshold = 60
rad_extension_factor = 0.2
circle_division = 10
linr_dfl = 0.8
angle_dfl = 0.5
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
    
def place_interim_pipes(start_pt, end_pt, pyvec1, pyvec2, radius1, radius2):
    c1 = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius1, division = circle_division)
    edge = py3dmodel.construct.make_edge(start_pt, end_pt)
    lb,ub = py3dmodel.fetch.edge_domain(edge)
    length = py3dmodel.calculate.edgelength(lb,ub,edge)
    nsegments = int((length/(radius1*2))/20) +1
    e_range = ub-lb
    e_interval = e_range/nsegments
    
    if pyvec1 != pyvec2:
        r_range = radius2-radius1
        r_interval = r_range/nsegments
        
        a_range = py3dmodel.calculate.angle_bw_2_vecs(pyvec1, pyvec2)
        a_interval = math.floor(a_range/nsegments)
        
        rot_axis = py3dmodel.calculate.cross_product(pyvec1, pyvec2)
        c_list = []
        for i in range(nsegments-1):
            i = i+1
            parm = (i*e_interval) + lb
            pypt = py3dmodel.calculate.edgeparameter2pt(parm, edge)
            angle = (i*a_interval)
            radius = (i*r_interval) + radius1
            c2 = py3dmodel.modify.rotate(c1,start_pt,rot_axis,angle)
            c2 = py3dmodel.fetch.topo2topotype(c2)
            n = py3dmodel.calculate.face_normal(c2)
            c3 = py3dmodel.construct.make_polygon_circle(pypt,n,radius,division = circle_division)
            c_list.append(c3)
    else:
        c_list = []
        for i in range(nsegments-1):
            i = i+1
            parm = (i*e_interval) + lb
            pypt = py3dmodel.calculate.edgeparameter2pt(parm, edge)
            c3 = py3dmodel.construct.make_polygon_circle(pypt,pyvec1,radius1,division = circle_division)
            c_list.append(c3)
    return c_list
    
def extrude_branch(start_pt, end_pt, radius, cap = False):
    if start_pt != end_pt:
        vec1 = py3dmodel.construct.make_vector(start_pt, end_pt)
        pyvec1 = py3dmodel.modify.normalise_vec(vec1)

        bottom_pipe = py3dmodel.construct.make_polygon_circle(start_pt, pyvec1, radius, division = circle_division)
        top_pipe = py3dmodel.construct.make_polygon_circle(end_pt, pyvec1, radius, division = circle_division)
        dist = py3dmodel.calculate.distance_between_2_pts(start_pt, end_pt)
        dia = radius*2
        if dist/dia >20:
            pipe_list = place_interim_pipes(start_pt, end_pt, pyvec1, pyvec1, radius, radius)
            l_face_list = []
            l_face_list.append(bottom_pipe)
            l_face_list.extend(pipe_list)
            l_face_list.append(top_pipe)
        else:
            l_face_list = [bottom_pipe,top_pipe]

        extrude = py3dmodel.construct.make_loft(l_face_list)
        loft_face_list = py3dmodel.construct.simple_mesh(extrude, linear_deflection = linr_dfl, angle_deflection=angle_dfl)
        loft_face_list.append(top_pipe)
        if cap == True:
            loft_face_list.append(bottom_pipe)
            #mesh the solid
            #l_cmpd = py3dmodel.construct.make_compound(loft_face_list)
            #tri_faces = py3dmodel.construct.simple_mesh(l_cmpd, linear_deflection = linr_dfl, angle_deflection = angle_dfl)
            extrude_meshed = py3dmodel.construct.sew_faces(loft_face_list)
            if len(extrude_meshed) >1:
                print "something went wrong at the construction of branches"
            solid_meshed = py3dmodel.construct.make_solid(extrude_meshed[0])
            solid_meshed = py3dmodel.modify.fix_close_solid(solid_meshed)
            return solid_meshed
        else:
            #mesh the shell
            #l_cmpd = py3dmodel.construct.make_compound(loft_face_list)
            #tri_faces = py3dmodel.construct.simple_mesh(l_cmpd, linear_deflection = linr_dfl, angle_deflection = angle_dfl)
            extrude_meshed = py3dmodel.construct.sew_faces(loft_face_list)
            if len(extrude_meshed) >1:
                print "something went wrong at the construction of branches"
            return extrude_meshed[0]
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
        dist = py3dmodel.calculate.distance_between_2_pts(start_pt, end_pt)
        dia = radius*2
        if dist/dia >20:
            pipe_list = place_interim_pipes(start_pt, end_pt, pyvec1, pyvec2, radius, radius2)
            l_face_list = []
            l_face_list.append(bottom_pipe)
            l_face_list.extend(pipe_list)
            l_face_list.append(top_pipe)
        else:
            l_face_list = [bottom_pipe, top_pipe]
        
        loft = py3dmodel.construct.make_loft(l_face_list, rule_face=True)
        face_list = py3dmodel.construct.simple_mesh(loft, linear_deflection = linr_dfl, angle_deflection = angle_dfl)
        if cap == True:
            face_list.append(bottom_pipe)
            face_list.append(top_pipe)
            #mesh the loft 
            #l_cmpd = py3dmodel.construct.make_compound(face_list)
            #tri_faces = py3dmodel.construct.simple_mesh(l_cmpd, linear_deflection = linr_dfl, angle_deflection =angle_dfl)
            loft_tri = py3dmodel.construct.sew_faces(face_list)
            if len(loft_tri) >1:
                print "something went wrong at the construction of branches"
            loft_tri = py3dmodel.construct.make_solid(loft_tri[0])
            loft_tri = py3dmodel.modify.fix_close_solid(loft_tri)
            return loft_tri
        else:
            #mesh the loft
            #l_cmpd = py3dmodel.construct.make_compound(face_list)
            #tri_faces = py3dmodel.construct.simple_mesh(l_cmpd, linear_deflection = linr_dfl, angle_deflection =angle_dfl)
            loft_tri = py3dmodel.construct.sew_faces(face_list)
            if len(loft_tri) >1:
                print "something went wrong at the construction of branches"
                
            return loft_tri[0]
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

def trace_2_tip(mtg_row, edge_lines_list):
    connection_list = []
    curr_row = mtg_row
    end_pt_name = curr_row[0]
    #need to look for next branch that starts with my end point
    while end_pt_name != "":
        connect_row_list = find_mtg_row_of_parent_pt(edge_lines_list, end_pt_name)
        if connect_row_list:
            chosen_row = choose_next_branch(connect_row_list)
            end_pt_name = chosen_row[0]
            connection_list.append(end_pt_name)
        else:
            end_pt_name = ""
            
    return connection_list
    
def construct_cylinder_frm_mtg_row(mtg_row, edge_lines_list, max_branch_order):
    branch_dict = {}
    end_pt_name = mtg_row[0]
    start_pt_name = mtg_row[1]
    start_pt, end_pt, radius, srow = get_start_end_pt(mtg_row, edge_lines_list)
    
    branching_order = trace_2_root(mtg_row, edge_lines_list)
    if branching_order <max_branch_order: 
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
        branch_dict["mtg_row"] = mtg_row
        
        if chosen_row:
            branch_dict["connection"] = chosen_row[0]
        else:
            branch_dict["connection"] = None
        return branch_dict
    else:
        return None

def get_branch_dict(end_pt_name_list, dict_list):
    get_list = []
    for bdict in dict_list:
        end_pt_name = bdict["end_pt_name"]
        if end_pt_name in end_pt_name_list:
            get_list.append(bdict)
            if len(get_list) == len(end_pt_name_list):
                break
    return get_list

def create_base_polygon(branch_dict):
    start_pt = branch_dict["start_pt"]
    end_pt = branch_dict["end_pt"]
    vec = py3dmodel.construct.make_vector(start_pt, end_pt)
    pyvec = py3dmodel.modify.normalise_vec(vec)
    radius = branch_dict["radius"]
    base_polygon = py3dmodel.construct.make_polygon_circle(start_pt, pyvec, radius, division = circle_division )
    #tri_list = py3dmodel.construct.simple_mesh(base_polygon, linear_deflection = linr_dfl, angle_deflection = angle_dfl)
    return base_polygon

def multiple_bool_fuse(solid_list, progress_dir = None):
    fused = solid_list[0]
    solid_list2 = solid_list[:]
    del solid_list2[0]
    nsolids = len(solid_list2)
    
    bool_list = []
    non_bool_list = []
    
    if progress_dir != None:
        interim_cnt = int(math.ceil((nsolids/20.0)/10))*10
        progress_filepath = os.path.join(progress_dir, "progress.txt")
        progress_file = open(progress_filepath, "w")
        progress_file.write("")
        progress_file.close()
        
    s2cnt = 0
    for solid2 in solid_list2:
        if progress_dir != None:
            progress_file = open(progress_filepath, "a")
            str0 = str(s2cnt+1) + "\n"
            str1 = "FUSED:" +  str(len(bool_list))  +  "/" +  str(nsolids) + "\n"
            str2 = "NON_FUSABLE " +  str(len(non_bool_list)) + "\n"
            progress_file = open(progress_filepath, "a")
            progress_file.write(str0 + str1 +str2)
            progress_file.close()

        fused2 = py3dmodel.construct.boolean_fuse(fused, solid2)
        solid_list3 = py3dmodel.fetch.topo_explorer(fused2, "solid")
        nsolids3 = len(solid_list3)
        
        if nsolids3 > 1:
            print "IN multiple_bool_fuse FUNCTION ... "
            print "MORE THAN 1 SOLID IS PRODUCED, INSTEAD", nsolids3, "SOLIDS ARE PRODUCED"
            #py3dmodel.utility.visualise([solid_list3, solid_list], ["BLUE", "RED"])
            
            if solid2 not in non_bool_list: non_bool_list.append(solid2)
            s2cnt+=1
            continue
        
        vol1 = py3dmodel.calculate.solid_volume(fused)
        solid3 = solid_list3[0]
        solid3 = py3dmodel.modify.fix_close_solid(solid3)
        vol2 = py3dmodel.calculate.solid_volume(solid3)
        
        if vol2 >= vol1:
            fused = solid3
            bool_list.append(s2cnt)
            if solid2 in non_bool_list: non_bool_list.remove(solid2)
            
        if vol2<vol1:
            if solid2 not in non_bool_list: non_bool_list.append(solid2)
            
        if progress_dir!=None:
            if s2cnt%interim_cnt == 0 or s2cnt == nsolids-1:                 
                # Export to brep
                interim_file = os.path.join(progress_dir, "tree_interim" + str(s2cnt) + ".brep")
                py3dmodel.utility.write_brep(fused, interim_file)
                
                interim_file_non_bool = os.path.join(progress_dir, "tree_interim_non_bool" + str(s2cnt) + ".brep")
                nb_cmpd = py3dmodel.construct.make_compound(non_bool_list)
                py3dmodel.utility.write_brep(nb_cmpd, interim_file_non_bool)
                
        s2cnt+=1
        
    return fused, non_bool_list

def multiple_bool_fuse2(solid_list1, solid_list2):
    tip_solids = solid_list1
    tip_solids2 = tip_solids[:]
    
    tip_parent_solids = solid_list2[:]
    
    for tip in tip_solids:
        tp_cnt = 0
        for tp in tip_parent_solids:
            fused = py3dmodel.construct.boolean_fuse(tp, tip)
            fused_solid_list = py3dmodel.fetch.topo_explorer(fused, "solid")
            if len(fused_solid_list) == 1:
                tip_parent_solids[tp_cnt] = fused_solid_list[0]
                tip_solids2.remove(tip)
                break
            tp_cnt+=1

    return tip_parent_solids, tip_solids2

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

def rmv_degenerate_faces_from_solid(occsolid):
    face_list = py3dmodel.fetch.topo_explorer(occsolid, "face")
    new_face_list = []
    for face in face_list:
        pts = py3dmodel.fetch.points_frm_occface(face)
        npts = len(pts)
        face_area = py3dmodel.calculate.face_area(face)
        if npts >= 3 or face_area > 1e-012:
            new_face_list.append(face)
            
    shell_list = py3dmodel.construct.sew_faces(new_face_list)
    chosen_shell, non_chosen_shell_list = choose_bigger_shell(shell_list)
    closed = py3dmodel.calculate.is_shell_closed(chosen_shell)
    
    if closed:
        fixed_solid = make_fix_solid(chosen_shell)
    else:
        fixed_shell_info = fill_holes(chosen_shell)
        fixed_shell = fixed_shell_info[0]
        fixed_solid = make_fix_solid(fixed_shell)
    return fixed_solid

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
#========================================================================================
#FUNCTIONS 
#========================================================================================
if not os.path.exists(result_dir):
    os.mkdir(result_dir)
    
print "#========================="
print "READING THE MTG FILE ..." 
print "#========================="
display_2dlist = []
colour_list = []
mf = open(mtg_file, "r")
lines = mf.readlines()
branch_lines = lines[3:]
bl_2dlist = []
for bl in branch_lines:
    bl = bl.replace("\n","")
    bl_list = bl.split("\t")
    bl_2dlist.append(bl_list)
    
print "#=========================================="
print "CONSTRUCTING THE BRANCHING DICTIONARY ..." 
print "#=========================================="
#a list of dictionaries that documents the tree architecture
branch_dict_list = []
max_order = float("inf")*-1 

for bll in bl_2dlist:
    #check if it is an edge
    if bll[1] !="":
        branch_dict = construct_cylinder_frm_mtg_row(bll, bl_2dlist, max_branch_order)
        if branch_dict != None:
            order = branch_dict["order"]
            if order > max_order: max_order = order
            branch_dict_list.append(branch_dict)
    
print "#==================================="
print "CONSTRUCTING THE BRANCH SOLIDS ..." 
print "#==================================="
order_list = []
for _ in range(max_order+1):
    order_list.append([])
  
end_pt_name_list = []
for branch_dict in branch_dict_list:
    end_pt_name = branch_dict["end_pt_name"]
    if end_pt_name not in end_pt_name_list:
        b_solid_list = []
        
        order = branch_dict["order"]
        geom = branch_dict["geometry"]
        base_polygon = create_base_polygon(branch_dict)
        b_solid_list.append(geom)
        b_solid_list.append(base_polygon)
            
        #trace branches that is directly connected to this branch
        direct_connection_names = trace_2_tip(branch_dict["mtg_row"], bl_2dlist)
        end_pt_name_list.append(end_pt_name)
        end_pt_name_list.extend(direct_connection_names)
        direct_connection_dict_list = get_branch_dict(direct_connection_names, branch_dict_list)

        for direct_connection_dict in direct_connection_dict_list:
            end_pt_name2 = direct_connection_dict["end_pt_name"]
            geom2 = direct_connection_dict["geometry"]
            parent = direct_connection_dict["parent"]
            angle = direct_connection_dict["angle"]
            b_solid_list.append(geom2)
            
            parent_dict_list = get_branch_dict([parent], branch_dict_list)
            parent_dict = parent_dict_list[0]
            parent_angle = parent_dict["angle"]
            parent_connection = parent_dict["connection"]
                
            if parent_angle >= angle_threshold:
                #this means this branch and the parent branch is at a 90 degree bend
                base_polygon = create_base_polygon(direct_connection_dict)
                b_solid_list.append(base_polygon)
                    
        b_shell_cmpd = py3dmodel.construct.make_compound(b_solid_list)
        b_face_list = py3dmodel.fetch.topo_explorer(b_shell_cmpd, "face")
        b_shell_list = py3dmodel.construct.sew_faces(b_face_list)

        b_solid_list2 = []
        for b_shell in b_shell_list:
            closed = py3dmodel.calculate.is_shell_closed(b_shell)
            if closed:
                b_solid2 = make_fix_solid(b_shell)
                b_solid_list2.append(b_solid2)
            else:
                #py3dmodel.utility.visualise([[b_shell]], ["BLUE"])
                print "IS IT CLOSED", closed
                
        order_list[order].append(b_solid_list2)
        
print "#============================================="
print "FILTERING THE BRANCHES ACCORDING TO ORDER ..." 
print "#============================================="
non_bool_list = []

order_list = order_list[0:max_branch_order]

f_order_list = []
o_cnt = 0
for o in order_list:
    order_solid_list = []
    print "NUMBER OF BRANCHES IN ORDER"+ str(o_cnt), ":", len(o)
    for solid_list in o:
        order_solid, non_bools = multiple_bool_fuse(solid_list)
        order_solid_list.append(order_solid)
        non_bool_list.extend(non_bools)
        
    f_order_list.append(order_solid_list)
    print "NUMBER OF SOLIDS IN ORDER" + str(o_cnt), ":", len(order_solid_list), ", STRAY SOLIDS:", len(non_bool_list)
    cmpd = py3dmodel.construct.make_compound(order_solid_list)
    py3dmodel.utility.write_brep(cmpd, os.path.join(result_dir, "order"+ str(o_cnt)+".brep"))
    
    nb_cmpd = py3dmodel.construct.make_compound(non_bool_list)
    py3dmodel.utility.write_brep(nb_cmpd, os.path.join(result_dir, "order"+ str(o_cnt)+"_strays.brep"))
    #py3dmodel.utility.visualise([order_solid_list], ["BLUE"])
    o_cnt+=1
    
print "#==========================================="
print "FUSING THE BRANCHES IN DESCENDING ORDER..." 
print "#==========================================="
##delete the main trunk
trunk_solid = f_order_list[0][0]
del f_order_list[0]

f_order_list2 = f_order_list
fused_2dlist = []
f_order_list2.reverse()
fused_list = f_order_list2[0]
n_f_order_list = len(f_order_list2)

for fcnt in range(n_f_order_list):
    if  fcnt != n_f_order_list-1:
        fused_list, non_bools = multiple_bool_fuse2(fused_list, f_order_list2[fcnt+1])
        non_bool_list.extend(non_bools)
        order_cnt = str(n_f_order_list-fcnt-1)
        print "NUMBER OF FUSED SOLIDS IN ORDER" + order_cnt, ":", len(fused_list), ", STRAY SOLIDS:", len(non_bool_list)
        
cmpd = py3dmodel.construct.make_compound(fused_list)
py3dmodel.utility.write_brep(cmpd, os.path.join(result_dir, "descending.brep"))

nb_cmpd = py3dmodel.construct.make_compound(non_bool_list)
py3dmodel.utility.write_brep(nb_cmpd, os.path.join(result_dir, "descending_strays.brep"))
    
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

#filter the branches according to the vol threshold
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

#fuse the branches to the trunk
mb_solid_list = []
mb_solid_list.append(trunk_solid)
mb_solid_list.extend(vf_fused_list)
tree_solid, non_bools = multiple_bool_fuse(mb_solid_list, progress_dir = result_dir)
#tree_solid = rmv_degenerate_faces_from_solid(tree_solid)
non_bool_list.extend(non_bools)

print "#============================================"
print "WRITING THE GEOMETRY TO BREP ..." 
print "#============================================"
print "WRITING THE TREE TO BREP ..." 

min_l, max_l = calc_topo_edge_min_max_length(tree_solid)
nb_cmpd = py3dmodel.construct.make_compound(non_bool_list)

brep_file = os.path.join(result_dir, "tree.brep")
brep_file_non_bool = os.path.join(result_dir, "tree_strays.brep")

py3dmodel.utility.write_brep(tree_solid, brep_file)
py3dmodel.utility.write_brep(nb_cmpd, brep_file_non_bool)

print "WRITING THE TREE TO STL ..." 
stl_file = os.path.join(result_dir, "tree.stl")
stl_file_non_bool = os.path.join(result_dir, "tree_strays.stl")

py3dmodel.utility.write_2_stl_gmsh(tree_solid, stl_file, mesh_dim = 2, min_length = min_l, max_length = max_l)
py3dmodel.utility.write_2_stl_gmsh(nb_cmpd, stl_file_non_bool, mesh_dim = 2, min_length = min_l, max_length = max_l)
#========================================================================================================
#visualise
#========================================================================================================
display_2dlist.append([tree_solid])
colour_list.append("BLUE")

display_2dlist.append(non_bool_list)
colour_list.append("RED")

time2 = time.time()
total_time = (time2-time1)/60.0
print "TIME TAKEN:", total_time
py3dmodel.utility.visualise(display_2dlist, colour_list)