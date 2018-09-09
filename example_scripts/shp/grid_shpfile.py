from py4design import py3dmodel, shp2citygml, urbangeom, shapeattributes
import shapefile
shpfile = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\brief\\shp\\site_bdry\\site_bdry.shp"
shpfile_res = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\brief\\shp\\site_bdry_grid\\site_bdry5_5.shp"
shpfile_res2 = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\brief\\shp\\site_bdry_offset\\site_bdry_10.shp"
xdim = 5 #metres
ydim = 5 #metres
offset = 10 #metres
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def read_shpfile(shp_filepath, att2get_list=None):
    sf = shapefile.Reader(shp_filepath)
    shapeRecs=sf.shapeRecords()
    if att2get_list!=None:
        att_name_list = shp2citygml.get_field_name_list(sf)
        att_index_list = []
        for att in att2get_list:
            att_index = att_name_list.index(att)-1
            att_index_list.append(att_index)
            
    poly_list = []
    
    print "READING SHPFILE ... ..."
    
    for rec in shapeRecs:
        poly_attribs=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            shp_att = shapeattributes.ShapeAttributes()
            if att2get_list!=None:
                att_cnt=0
                for att_index in att_index_list:
                    att = poly_attribs[att_index]
                    att_name = att2get_list[att_cnt]
                    shp_att.set_key_value(att_name, att)
                    att_cnt+=1
                
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            if len(occface_list) == 1:
                shp_att.set_shape(occface_list[0])
            else:
                cmpd = py3dmodel.construct.make_compound(occface_list)
                shp_att.set_shape(cmpd)
                
            poly_list.append(shp_att)
    
    return poly_list

def write_poly_shpfile(occface_list, shp_filepath):
    w = shapefile.Writer(shapeType = 5)
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
        w.poly(parts = [pyptlist2d])
        w.record(cnt)
        cnt+=1
    w.save(shp_filepath)
#===========================================================================================
#FUNCTIONS
#===========================================================================================
poly_list = read_shpfile(shpfile)
site_boundary_face = poly_list[0].dictionary["shape"]
site_boundary_face =py3dmodel.construct.make_offset(site_boundary_face, offset*-1)
write_poly_shpfile([site_boundary_face], shpfile_res2)
grid_pts, grid_faces = urbangeom.landuse_2_grid(site_boundary_face, xdim, ydim)
py3dmodel.utility.visualise([grid_faces])
write_poly_shpfile(grid_faces, shpfile_res)
print "DONE"