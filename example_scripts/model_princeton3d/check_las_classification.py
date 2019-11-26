import os

import shapefile
import numpy as np
from py4design import py3dmodel
from laspy.file import File

#specify the pt cloud directory
pt_cloud_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las"
bdry_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\las_bdry\\las_bdry.shp"
#============================================================================================================
#FUNCTION
#============================================================================================================
def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('index','N',10)
    cnt=0
    for occface in occface_list:
        wires = py3dmodel.fetch.topo_explorer(occface, "wire")
        nwires = len(wires)
        
        if nwires > 1:
            nrml = py3dmodel.calculate.face_normal(occface)
            poly_shp_list = []
            for wire in wires:
                pyptlist = py3dmodel.fetch.points_frm_wire(wire)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, nrml)
                is_anticlockwise2 = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise: #means its a face not a hole
                    if is_anticlockwise2:
                        pyptlist.reverse()
                else: #means its a hole not a face
                    if not is_anticlockwise2:
                        pyptlist.reverse()
                
                pyptlist2d = []
                for pypt in pyptlist:
                    x = pypt[0]
                    y = pypt[1]
                    pypt2d = [x,y]
                    pyptlist2d.append(pypt2d)
                poly_shp_list.append(pyptlist2d)
                
            w.poly(poly_shp_list)
            w.record(cnt)
                    
        else:
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
    w.close()

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

def extract_trees(las_filepath):
    lasfile = File(las_filepath, mode='r')
    #filter all single return points of classes 3, 4, or 5 (vegetation)
    try:
        #tree_pts = np.logical_or(lasfile.raw_classification == 3, lasfile.raw_classification == 4, lasfile.raw_classification == 5)
        veg = np.where(lasfile.raw_classification == 6)
        coords = np.vstack((lasfile.x, lasfile.y, lasfile.z)).transpose()
        valid_pts = np.take(coords, veg, axis = 0)[0]
        print len(valid_pts)
        lasfile.close()
    except:
        print "not classified"

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
    extract_trees(las_filepath)
    
#write_poly_shpfile(bdry_face_list, bdry_shp_file)
