import os

from py4design import py3dmodel
from laspy.file import File

#specify the pt cloud directory
pt_cloud_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las2"
bdry_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\las_bdry\\las_bdry.shp"
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
    
olist = []
cnt1 = 0
for f in bdry_face_list:
    bdry_list2 = bdry_face_list[:]
    area1 = py3dmodel.calculate.face_area(f)
    cnt2 = 0
    for f2 in bdry_list2:
        if cnt2 != cnt1:
            common = py3dmodel.construct.boolean_common(f, f2)
            is_null = py3dmodel.fetch.is_compound_null(common)
            if not is_null:
                common = py3dmodel.modify.move([0,0,0], [0,0,20], common)
                f2 = py3dmodel.modify.move([0,0,0], [0,0,10], f2)
                f3 = py3dmodel.fetch.topo_explorer(common, "face")
                if f3:
                    area2 = py3dmodel.calculate.face_area(f3[0])
                    if area2 >= area1:
                        file1 = list_dir[cnt1]
                        file2 = list_dir[cnt2]
                        print "********************* Overlap file1", file1
                        print "********************* Overlap file2", file2
                        olist.append([])
                        if file1 not in olist:
                            olist[-1].append(list_dir[cnt1])
                        if file2 not in olist:
                            olist[-1].append(list_dir[cnt2])
                        #py3dmodel.utility.visualise([[common], [f], [f2]], ["RED", "GREEN", "BLUE"])
                
        cnt2+=1
    cnt1+=1

print len(olist)
for x in olist:
    print x