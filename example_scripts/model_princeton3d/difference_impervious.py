import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile
from laspy.file import File
import numpy as np

#===========================================================================================
#INPUTS
#===========================================================================================
imp_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\mercer_impervious2015_clipped\\mercer_impervious2015_clipped3.shp"
bdry_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\princeton_bdry2\\bdry_grid.shp"

#specify the directory to store the results which includes
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d"

#specify if you want to view the result interactively
viewer = True
#===========================================================================================
#THE RESULT FILES
#===========================================================================================
diff_filepath = os.path.join(result_directory, "shp", "mercer_impervious2015_clipped", "mercer_impervious2015_clipped2.shp")
#===========================================================================================
#FUNCTION
#===========================================================================================
def read_sf(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occfaces = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            for occface in occfaces:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(occface)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list
        
def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)

def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 5)
    w.field('index','N',10)
    cnt=0
    for occface in occface_list:
        #nwires = 
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
    
def triangulate_faces(occface_list):
    tri_list = []
    for face in occface_list:
        tri_faces = py3dmodel.construct.simple_mesh(face)
        tri_list.extend(tri_faces)
    return tri_list
    
#===========================================================================================
#READ THE SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading the file 1***************"
shpatt_list = read_sf(imp_shp_file)
print "*******Reading the file 2***************"
shpatt_bdry = read_sf(bdry_shp_file)
#bdry_face = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move([0,0,0], [0,0,-3], bdry_face))
#extrude_bdry= py3dmodel.construct.extrude(bdry_face, [0,0,1], 10)
#===========================================================================================
#DIFFERENCE THE IMPERVIOUS SURFACES
#===========================================================================================
print "*******Looping through the file***************"
shp_list = []
for shpatt in shpatt_list:
    shp = shpatt.shape
    shp_list.append(shp)

cmpd = py3dmodel.construct.make_compound(shp_list)
py3dmodel.utility.visualise([[cmpd]])
diff_list = []
for b in shpatt_bdry:
    shp = b.shape
    diff = py3dmodel.construct.boolean_difference(shp, cmpd)
    diffs = py3dmodel.fetch.topo_explorer(diff, "face")
    diff_list.extend(diffs)
    
write_poly_shpfile(diff_list, diff_filepath)
cmpd = py3dmodel.construct.make_compound(diff_list)
time2 = time.clock()
total_time = time2-time1
print "*******Total Time Take:", total_time/60, "mins***************"

if viewer == True:
    py3dmodel.utility.visualise([[cmpd]])
    
