import os
import math

from py4design import py3dmodel

brep_fused_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree8\\result\\tree_interim23.brep"
brep2be_fused_filepath = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree8\\result\\descending.brep"
result_dir = "F:\\kianwee_work\\smart\\may2017-oct2017\\tree_modelling\\pts\\tree8\\result"

def make_fix_solid_from_face(occface_list):
    shell_list = py3dmodel.construct.sew_faces(occface_list)
    shell, shell_list2 = choose_bigger_shell(shell_list)
    solid = py3dmodel.construct.make_solid(shell)
    fixed_solid = py3dmodel.modify.fix_close_solid(solid)
    return fixed_solid

def check_face_planar(occface_list):
    for f in occface_list:
        planar = py3dmodel.calculate.is_face_planar(f)
        if not planar:
            print "not planar"

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
        if s2cnt >23:
            if progress_dir != None:
                progress_file = open(progress_filepath, "a")
                str0 = str(s2cnt+1) + "\n"
                str1 = "FUSED:" +  str(len(bool_list))  +  "/" +  str(nsolids) + "\n"
                str2 = "NON_FUSABLE " +  str(len(non_bool_list)) + "\n"
                progress_file = open(progress_filepath, "a")
                progress_file.write(str0 + str1 +str2)
                progress_file.close()
            
            shell_faces = py3dmodel.construct.simple_mesh(solid2)
            solid2 = make_fix_solid_from_face(shell_faces)
            
            fused_faces = py3dmodel.construct.simple_mesh(fused)
            fused = make_fix_solid_from_face(fused_faces)
            py3dmodel.utility.write_brep(fused, os.path.join(progress_dir, "tree_interim_tri" + str(s2cnt) + ".brep"))
            py3dmodel.utility.visualise([[fused], [solid2]], ["BLUE", "RED"])
            
            fused2 = py3dmodel.construct.boolean_fuse(fused, solid2)
            
            solid_list3 = py3dmodel.fetch.topo_explorer(fused2, "solid")
            nsolids3 = len(solid_list3)
            
            if nsolids3 > 1:
                print "IN multiple_bool_fuse FUNCTION ... "
                print "MORE THAN 1 SOLID IS PRODUCED, INSTEAD", nsolids3, "SOLIDS ARE PRODUCED"
                
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
                
        s2cnt+=1
        
    return fused, non_bool_list

fused = py3dmodel.utility.read_brep(brep_fused_filepath)
befused = py3dmodel.utility.read_brep(brep2be_fused_filepath)
fused_solids = py3dmodel.fetch.topo_explorer(fused, "solid")
befused_solids = py3dmodel.fetch.topo_explorer(befused, "solid")
print len(fused_solids), len(befused_solids)
fused_solids.extend(befused_solids)
multiple_bool_fuse(fused_solids, progress_dir = result_dir)