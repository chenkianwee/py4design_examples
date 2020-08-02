import os

from py4design import py3dmodel
import las_utils

if __name__ == '__main__':
    #specify the pt cloud directory
    pt_cloud_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\las2"
    bdry_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\las_bdry\\las_bdry.shp"
    
    lasfiles = las_utils.get_lasfiles2(pt_cloud_dir)
    bdry_face_list = []
    
    for laspath in lasfiles:
        mn = las_utils.get_las_file_bdry(laspath)
        lasfilename = os.path.split(laspath)[-1].split('.')[-2]
        face = las_utils.make_bdry_face2d(mn)
        shpatt = shpfile_utils.shp2shpatt(face, {'lasfile':lasfilename})
        shpatt_list.append(shpatt)
        bdry_face_list.append(face)
        
    olist = []
    
    for cnt1,f in enumerate(bdry_face_list):
        bdry_list2 = bdry_face_list[:]
        area1 = py3dmodel.calculate.face_area(f)
        for cnt2,f2 in enumerate(bdry_list2):
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
                            print("********************* Overlap file1", file1)
                            print("********************* Overlap file2", file2)
                            olist.append([])
                            if file1 not in olist:
                                olist[-1].append(list_dir[cnt1])
                            if file2 not in olist:
                                olist[-1].append(list_dir[cnt2])
                            #py3dmodel.utility.visualise([[common], [f], [f2]], ["RED", "GREEN", "BLUE"])
    print(len(olist))
    for x in olist:
        print(x)