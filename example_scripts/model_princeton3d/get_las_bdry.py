import os

from py4design import py3dmodel
import las_utils
import shpfile_utils

if __name__ == '__main__':
    #specify the pt cloud directory
    pt_cloud_dir = "E:\\kianwee_work_data\\lidar_campus_as_lab\\lidar"
    shp_filepath = "E:\\kianwee_work_data\\lidar_campus_as_lab\\shp\\bdry.shp"
    
    lasfiles = las_utils.get_lasfiles2(pt_cloud_dir)
    bdry_face_list = []
    shpatt_list = []
    
    for laspath in lasfiles:
        mn = las_utils.get_las_file_bdry(laspath)
        lasfilename = os.path.split(laspath)[-1].split('.')[-2]
        face = las_utils.make_bdry_face2d(mn)
        shpatt = shpfile_utils.shp2shpatt(face, {'lasfile':lasfilename})
        shpatt_list.append(shpatt)
        bdry_face_list.append(face)
    
    py3dmodel.utility.visualise([bdry_face_list])
    shpfile_utils.write_poly_shpfile(shpatt_list, shp_filepath)