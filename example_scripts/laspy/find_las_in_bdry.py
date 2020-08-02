import las_utils
from shp import shpfile_utils
from py4design import py3dmodel

bdry_shppath = 'F:\\kianwee_work\\princeton\\2020_01_to_2020_06\\database\\example\\pu_part\\shp\\boundary\\boundary.shp'
las_dir = 'E:\\kianwee_work_data\\lidar_campus_as_lab\\lidar'

def make_bbox_face2d(bbox):
    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[3]
    ymax = bbox[4]
    pyptlist = [[xmin,ymin, 0], [xmax,ymin, 0], [xmax,ymax, 0], [xmin,ymax, 0]]
    bdry_face = py3dmodel.construct.make_polygon(pyptlist)
    return bdry_face

shpatts = shpfile_utils.read_sf_poly(bdry_shppath)
bdry_poly = shpatts[0].shape
bbox = py3dmodel.calculate.get_bounding_box(bdry_poly)
face = make_bbox_face2d(bbox)

laspaths = las_utils.get_lasfiles2(las_dir)

face_list = []
for laspath in laspaths:
    lbbox = las_utils.get_las_file_bdry(laspath)
    lface = make_bbox_face2d(lbbox)
    common = py3dmodel.construct.boolean_common(face, lface)
    is_null = py3dmodel.fetch.is_compound_null(common)
    if is_null == False:
        print(laspath)
        face_list.append(lface)
        
# py3dmodel.utility.visualise([face_list, [face]], ['RED', 'GREEN'])