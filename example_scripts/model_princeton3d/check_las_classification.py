import os

import numpy as np
from py4design import py3dmodel
from laspy.file import File

#specify the pt cloud directory
pt_cloud_dir = "E:\\kianwee_work_data\\lidar_campus_as_lab\\lidar"
#============================================================================================================
#FUNCTION
#============================================================================================================
def find_las_file(folder_dirs):
    lasfile = ""
    for dirx in folder_dirs:
        split_dir = dirx.split(".")
        if len(split_dir) > 1:
            filetype = split_dir[1]
            if filetype == "las":
              lasfile = dirx
    return lasfile

def get_las_file_bdry(las_filepath):
    lasfile = File(las_filepath, mode='r')
    mx = lasfile.header.max
    mn = lasfile.header.min
    #lasfile.close()
    mn.extend(mx)
    return mn, lasfile

def check_classification(las_filepath):
    lasfile = File(las_filepath, mode='r')
    # print('Total number of points:',len(lasfile.x))
    clfy_d = {}
    try:
        clfy = lasfile.raw_classification
        unqs = np.unique(clfy)
        for unq in unqs:
            where = np.where(clfy == unq)[0]
            clfy_d[unq] = len(where)
        lasfile.close()
        
    except:
        print("not classified")
    
    return clfy_d

def extract_las_pts(las_filepath, classify_no_list):
    lasfile = File(las_filepath, mode='r')
    try:       
        clfy = lasfile.raw_classification
        clfy_list = []
        for no in classify_no_list:
            clfy_list.append(clfy == no)
            
        chosen_pts = np.logical_or(*clfy_list)
        # chosen_pts = np.logical_or(clfy == 1, clfy == 2)
        take_idx = np.where(chosen_pts)
        coords = np.vstack((lasfile.x, lasfile.y, lasfile.z)).transpose()
        valid_pts = np.take(coords, take_idx, axis = 0)[0]
        lasfile.close()
        return valid_pts       
    except:
        return None    

def make_bdry_face2d(mn_mx_list):
    xmin = mn_mx_list[0]
    ymin = mn_mx_list[1]
    xmax = mn_mx_list[3]
    ymax = mn_mx_list[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face

#============================================================================================================
#FUNCTION
#============================================================================================================
list_dir = os.listdir(pt_cloud_dir)
for dirx in list_dir:    
    las_folder = os.path.join(pt_cloud_dir, dirx)
    folder_dirs = os.listdir(las_folder)
    lasfilename = find_las_file(folder_dirs)
    las_filepath = os.path.join(pt_cloud_dir, dirx, lasfilename)
    d = check_classification(las_filepath)
    extract_pts = extract_las_pts(las_filepath, [1, 2, 3])
    print(d)
    if extract_pts is not None:
        print(len(extract_pts))