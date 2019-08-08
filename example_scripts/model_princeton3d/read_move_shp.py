import os
import time
from py4design import py3dmodel, shp2citygml, shapeattributes
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
#specify the shp file to be moved
shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\bldg_tree_facilities\\bldg_other_facilities.shp"
#specify the orig reference point
origpt_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\points\\orig_pt.shp"

#specify the directory to store the results which includes
result_directory = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\bldg_tree_facilities"
filename = "bldg_other_moved.shp"
#===========================================================================================
#THE REQUIRED SHP FILES
#===========================================================================================
#specify the target pt file
targetpt_shp_file = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\model3d\\shp\\points\\target_pt.shp"
#===========================================================================================
#FUNCTION
#===========================================================================================
def read_sf_lines(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    #shapeRecs=sf.shapeRecords()[40598:]
    #nshp = 81195
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    rcnt = 0
    for rec in shapeRecs:
        poly_atts=rec.record
        part_list = shp2citygml.get_geometry(rec)
        for part in part_list:
            part3d = shp2citygml.pypt_list2d_2_3d(part, 0.0)
            wire = py3dmodel.construct.make_wire(part3d)
            shpatt = shapeattributes.ShapeAttributes()
            shpatt.set_shape(wire)
            att2shpatt(shpatt, attrib_name_list, poly_atts)
            shpatt_list.append(shpatt)
            
        rcnt+=1
                
    return shpatt_list

def read_sf_poly(sf_filepath):
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

def read_sf_pt(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pts = shp2citygml.get_geometry(rec)
        if pts:
            for pt in pts:
                pypt = (pt[0], pt[1], 0.0)
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(pypt)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)

def write_polylines_shpfile(occwire_list, shp_filepath):
    w = shapefile.Writer(shp_filepath, shapeType = 3)
    w.field('index','N',10)
    cnt=0
    for wire in occwire_list:
        #pyptlist = py3dmodel.fetch.points_frm_wire(wire)
        vlist = py3dmodel.fetch.topo_explorer(wire, "vertex")
        occpts = py3dmodel.modify.occvertex_list_2_occpt_list(vlist)
        pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(occpts)
        pyptlist2d = []
        for pypt in pyptlist:
            x = pypt[0]
            y = pypt[1]
            pypt2d = [x,y]
            pyptlist2d.append(pypt2d)
    
        w.line([pyptlist2d])
        w.record(cnt)
        cnt+=1
    w.close()
    
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
    
def extract_shape_from_shapatt(shpatt_list):
    shape_list = []
    for att in shpatt_list:
        shape = att.shape
        shape_list.append(shape)
    return shape_list

#===========================================================================================
#READ THE SHAPEFILE
#===========================================================================================
time1 = time.clock()
print "*******Reading the Shp File 2be Moved***************"
bmoved_list = read_sf_lines(shp_file)
#bmoved_list = read_sf_poly(shp_file)
shps = extract_shape_from_shapatt(bmoved_list)
cmpd = py3dmodel.construct.make_compound(shps)
#py3dmodel.utility.visualise([shps], ["BLACK"])
orig_pt_shp = read_sf_pt(origpt_shp_file)
orig_pt = extract_shape_from_shapatt(orig_pt_shp)[0]

print orig_pt
print "*******Reading the Target Shp File***************"
target_pt_shp = read_sf_pt(targetpt_shp_file)
target_pt = extract_shape_from_shapatt(target_pt_shp)[0]
print target_pt

print "*******Moving and Writing the Shp File***************"
moved_cmpd = py3dmodel.modify.move(orig_pt, target_pt, cmpd)
res_filepath = os.path.join(result_directory, filename)

wire_list = py3dmodel.fetch.topo_explorer(moved_cmpd, "wire")
write_polylines_shpfile(wire_list, res_filepath)

#face_list = py3dmodel.fetch.topo_explorer(moved_cmpd, "face")
#write_poly_shpfile(face_list, res_filepath)

print "Completed"
#py3dmodel.utility.visualise([wire_list], ["GREEN"])
