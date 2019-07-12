import os

import shapefile
from py4design import py3dmodel
from laspy.file import File

#specify the pt cloud directory
pt_cloud_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las2"
bdry_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\las_bdry\\las_bdry.shp"
#============================================================================================================
#FUNCTION
#============================================================================================================
def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('index','N',10)
    cnt=0
    for occface in occface_list:
        pyptlist = py3dmodel.fetch.points_frm_occface(occface)
        is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
        if is_anticlockwise:
            pyptlist.reverse()
        pyptlist2d = []
        for pypt in pyptlist:
            x = pypt[0]
            y = pypt[1]
            pypt2d = [x,y]
            pyptlist2d.append(pypt2d)
        w.poly([pyptlist2d])
        w.record(cnt)
        cnt+=1

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
bdry_face_list = []
for dirx in list_dir:    
    las_folder = os.path.join(pt_cloud_dir, dirx)
    folder_dirs = os.listdir(las_folder)
    lasfilename = find_las_file(folder_dirs)
    las_filepath = os.path.join(pt_cloud_dir, dirx, lasfilename)
    las_bdry, lasfile = get_las_file_bdry(las_filepath)
    bdry_face = make_bdry_face2d(las_bdry)
    bdry_face_list.append(bdry_face)
    
write_poly_shpfile(bdry_face_list, bdry_shp_file)