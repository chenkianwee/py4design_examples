import os

from py4design import py3dmodel

#specify the pt cloud directory
file_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\brep\\main_campus"
filename = "impervious_surface.brep"
#============================================================================================================
#FUNCTION
#============================================================================================================
def flatten_faces(face_list):
    flatten_list = []
    for f in face_list:
        flatten = py3dmodel.modify.flatten_face_z_value(f)
        flatten_list.append(flatten)
    return flatten_list

def calc_faces_area(face_list):
    area = 0
    for f in face_list:
        area = area + py3dmodel.calculate.face_area(f)
    return area
#============================================================================================================
#FUNCTION
#============================================================================================================
list_dir = os.listdir(file_dir)
ndir = len(list_dir)
face_list = []
cnt = 0
for dirx in list_dir:    
    print "**********Processing ... ", cnt+1, "/", ndir, "folder", dirx
    folder = os.path.join(file_dir, dirx)
    filepath = os.path.join(file_dir, dirx, filename)
    if os.path.isfile(filepath):
        cmpd = py3dmodel.utility.read_brep(filepath)
        faces = py3dmodel.construct.simple_mesh(cmpd)
        face_list.extend(faces)
    cnt+=1

proj_area = calc_faces_area(face_list)

flatten_list = flatten_faces(face_list)
flatten_area = calc_faces_area(flatten_list)
diff = proj_area-flatten_area
percent = diff/flatten_area * 100
print "PROJECTED AREA", proj_area, "FLAT AREA", flatten_area, "DIFF", diff, "%", percent 

py3dmodel.utility.visualise([face_list, flatten_list], ["RED", "BLUE"])