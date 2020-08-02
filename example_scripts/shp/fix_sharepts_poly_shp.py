import time
import argparse

import numpy as np
import shpfile_utils
from py4design import py3dmodel
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def mv_apart(pyptlist):
    indices = py3dmodel.modify.id_dup_pts_indices(pyptlist)
    
    del_list = []
    for dups in indices:
        dups.sort()
        
        for cnt, dup in enumerate(dups):
            if cnt != 0:
                if dup - dups[cnt-1] == 1:
                    #just remove the point
                    #because they are right next to each other
                    del_list.append(dup)
                else:
                    #move the point backwards alittle
                    prev_indx = dup - 1
                    orig_pt = pyptlist[dup]
                    prev_pt = pyptlist[prev_indx]
                    pydir = orig_pt - prev_pt
                    vec = py3dmodel.construct.make_vector(orig_pt, 
                                                           prev_pt)
                    pydir = py3dmodel.modify.normalise_vec(vec)
                    mv_pt = py3dmodel.modify.move_pt(orig_pt, pydir, 
                                                     1e-04)
                    pyptlist[dup] = mv_pt
    
    if len(del_list) > 0: 
        pyptlist= np.delete(pyptlist, del_list, axis=0)
    return pyptlist
        
def fix_face_w_same_pts(face):
    #FIRST CHECK IF THE FACE HAS ANY POINTS THAT IS THE SAME
    wires = py3dmodel.fetch.wires_frm_face(face)
    is_dup = []
    for wire in wires:
        pyptlist = py3dmodel.fetch.points_frm_wire(wire)
        indices = py3dmodel.modify.id_dup_pts_indices(pyptlist)
        if len(indices) > 0:
            is_dup.append(True)
        else:
            is_dup.append(False)
            
    #IF THERE IS MV THE POINTS APART
    if True in is_dup:
        wire_indx = np.where(is_dup)[0]
        nrml = py3dmodel.calculate.face_normal(face)
        face_list = []
        hole_list = []
        for cnt, wire in enumerate(wires):
            pyptlist = py3dmodel.fetch.points_frm_wire(wire)
            pyptlist = np.array(pyptlist)
            is_acwise = py3dmodel.calculate.is_anticlockwise(pyptlist, 
                                                             nrml)
            if cnt in wire_indx:
                pyptlist = mv_apart(pyptlist)
                
            if is_acwise:
                #that means its a face
                face_list.append(list(pyptlist))
            else:
                #that means its a hole
                new_pyptlist = []
                for pypt in pyptlist:
                    new_pyptlist.append(list(pypt))
                hole_list.append(new_pyptlist)
            
        face = py3dmodel.construct.make_polygon_w_holes(face_list[0], hole_list)
        # py3dmodel.utility.visualise([[face]], ['RED'])
        return face, 1
    else:
        return face, 0
    
def fix_faces_w_same_pts(faces):
    fixed_faces = []
    fixed_face_cnt = 0
    for face in faces:
        fixed_face, cnt = fix_face_w_same_pts(face)
        fixed_face_cnt+=cnt
        fixed_faces.append(fixed_face)
    return fixed_faces, fixed_face_cnt

def secs2hrsmins_str(seconds):
    taken_mins = seconds/60
    taken_hrs_mins = divmod(taken_mins, 60)
    hr = str(int(taken_hrs_mins[0]))
    mins = str(int(taken_hrs_mins[1]))
    strx = 'Elapsed Time:'+hr+' hr ' + mins + ' mins'
    return strx

def retrieve_arg():
    parser = argparse.ArgumentParser(description='Find polygons with shared points and move the points apart.')
    
    parser.add_argument('inputpath',
                        help='the shpfile to process')
    
    parser.add_argument('outputpath',
                        help='the result shpfile')
    
    args = parser.parse_args()
    arg_list = ['', args.inputpath, args.outputpath]
    return arg_list
#===========================================================================================
#MAIN
#===========================================================================================
if __name__ == '__main__':
    t1 = int(time.perf_counter())
    #===========================================================================================
    #RETRIEVE ARG
    #===========================================================================================
    # args = retrieve_arg()
    
    args = ['', 
            'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_luse\\pu_main_luse.shp', 
            'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_luse\\pu_main_luse1.shp']
    
    input_path = args[1]
    output_path = args[2]
    
    shpatts = shpfile_utils.read_sf_poly(input_path)
    faces = [att.shape for att in shpatts]
    fixed_list, fixed_cnt = fix_faces_w_same_pts(faces)
    for cnt,shpatt in enumerate(shpatts):
        shpatt.set_shape(fixed_list[cnt])
    
    shpfile_utils.write_poly_shpfile(shpatts, output_path)
    t2 = int(time.perf_counter())
    taken_secs = t2-t1
    time_str = secs2hrsmins_str(taken_secs)
    print('I have found ' + str(fixed_cnt) + ' polygons have shared points and fixed it.')
    print(time_str)
    