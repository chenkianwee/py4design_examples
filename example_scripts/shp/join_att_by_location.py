import time
import argparse

import numpy as np
import shpfile_utils
from py4design import py3dmodel
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def retrieve_arg():
    parser = argparse.ArgumentParser(description='Inherit attributes based on overlap. If two polygons overlaps more than 50%.')
    
    parser.add_argument('inputpath1',
                        help='the shpfile to process')
    
    parser.add_argument('inputpath2',
                        help='the shpfile attribute to inherit')
    
    parser.add_argument('outputpath',
                        help='the result shpfile')
    
    parser.add_argument('-a','--attlist', nargs='+', 
                        help='attributes to inherit', required=True)
    
    args = parser.parse_args()
    arg_list = ['', args.inputpath1, args.inputpath2, args.outputpath,
                args.attlist]
    return arg_list

def secs2hrsmins_str(seconds):
    taken_mins = seconds/60
    taken_hrs_mins = divmod(taken_mins, 60)
    hr = str(int(taken_hrs_mins[0]))
    mins = str(int(taken_hrs_mins[1]))
    strx = 'Elapsed Time:'+hr+' hr ' + mins + ' mins'
    return strx

def get_bboxes(shpatts):
    bbox_list = []
    for att in shpatts:
        face = att.shape
        xmn,ymn,zmn,xmx,ymx,zmx = py3dmodel.calculate.get_bounding_box(face)
        bbox = [xmn,ymn,zmn,xmx,ymx,zmx]
        bbox_list.append(bbox)
        
    return bbox_list

def calc_faces_areas(faces):
    area = 0
    for face in faces:
        area = py3dmodel.calculate.face_area(face)
        area+=area
    return area

def compare_faces_areas(common_face_area, face1_area, face2_area):
    ratio1 = common_face_area/face1_area
    ratio2 = common_face_area/face2_area
    if ratio1 > ratio2:
        return ratio1
    else:
        return ratio2

def id_face_overlap(face, overlap_faces):
    face_area = py3dmodel.calculate.face_area(face)
    indices= []
    for cnt, of in enumerate(overlap_faces):
        face_area2 = py3dmodel.calculate.face_area(of)
        common = py3dmodel.construct.boolean_common(face, of)
        common_faces = py3dmodel.fetch.topo_explorer(common, 'face')
        common_area = calc_faces_areas(common_faces) 
        ratio = compare_faces_areas(common_area, face_area, face_area2)
        if ratio >= 0.5:
            indices.append(cnt)
    return indices

def inherit_att(shpatt, shps2inherit, att_names):
    d = shpatt.dictionary
    keys = d.keys()
    for shp in shps2inherit:
        d2inherit = shp.dictionary
        for att_name in att_names:
            val = str(d2inherit[att_name])
            if att_name in keys:
                ex_val = str(d[att_name])
                if ex_val == '':
                    shpatt.set_key_value(att_name, val)
                elif ex_val != val:
                    new_val = ex_val +':'+ val
                    shpatt.set_key_value(att_name, new_val)
            else:
                shpatt.set_key_value(att_name, val)

def inherit_empty_none(shpatt, att_names):
    for att_name in att_names:
        shpatt.set_key_value(att_name, '')
        
#===========================================================================================
#MAIN
#===========================================================================================
if __name__ == '__main__':
    t1 = time.perf_counter()
    #===========================================================================================
    #RETRIEVE ARG
    #===========================================================================================
    # args = retrieve_arg()
    args = [None, 
            'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_ftprt\\pu_main_ftprt.shp', 
            'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_osm_ftprt\\pu_main_osm_ftprt.shp',
            'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_main\\shp\\pu_main_ftprt\\pu_main_ftprt1.shp',
            ['name', 'building', 'amenity']]
    
    input_path1 = args[1]
    input_path2 = args[2]
    output_path = args[3]
    att_list = args[4]
        
    shpatts1 = shpfile_utils.read_sf_poly(input_path1)
    # shpatts1 = shpatts1[900:910]
    shpatts2 = shpfile_utils.read_sf_poly(input_path2)
    faces2 = [att.shape for att in shpatts2]
    bboxes = get_bboxes(shpatts2)
    for shpatt in shpatts1:
        face = shpatt.shape
        pyptlist = py3dmodel.fetch.points_frm_occface(face)
        bbox_inds = py3dmodel.calculate.id_bboxes_contain_pts(bboxes, 
                                                              pyptlist)
        chosen_shpatts = np.take(shpatts2, bbox_inds, axis=0)
        chosen_faces = [att.shape for att in chosen_shpatts]
        indices = id_face_overlap(face, chosen_faces)
        if len(indices) > 0:
            chosen_shpatts = np.take(chosen_shpatts, indices, axis=0)
            chosen_faces = [att.shape for att in chosen_shpatts]
            inherit_att(shpatt, chosen_shpatts, att_list)
        else:
            chosen_faces = []
            inherit_empty_none(shpatt, att_list)
            
        # #==============================================================
        # #for checking the results
        # #==============================================================
        # val_list = []
        # for att in att_list:
        #     val = shpatt.get_value(att)
        #     val_list.append(val)
            
        # print(val_list)
        # py3dmodel.utility.visualise([[face], faces2], 
        #                             ['RED','GREEN'])
        # #==============================================================
        # #==============================================================
    
    shpfile_utils.write_poly_shpfile(shpatts1, output_path)
    t2 = time.perf_counter()
    taken_secs = t2-t1
    time_str = secs2hrsmins_str(taken_secs)
    print(time_str)