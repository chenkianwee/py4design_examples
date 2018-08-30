from py4design import py3dmodel, shp2citygml
import shapefile

bdry_shp_file = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\shp\\site_bdry\\site_bdry.shp"
bdry_dae_file = "F:\\kianwee_work\\nus\\201804-201810\\hdb\\result\\dae\\site_bdry.dae"
#===========================================================================================
#GET THE SHAPEFILE BOUNDARY
#===========================================================================================
display_2dlist = []
colour_list = []

sf = shapefile.Reader(bdry_shp_file)
shapeRecs=sf.shapeRecords()

poly_list = []

print "READING SHPFILE ... ..."
for rec in shapeRecs:
    poly_attribs=rec.record
    pop = poly_attribs[2]
    pypolygon_list2d = shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
        poly_list.extend(occface_list)
        
py3dmodel.export_collada.write_2_collada(bdry_dae_file, occface_list = poly_list)
print "DONE"
#py3dmodel.utility.visualise([poly_list])