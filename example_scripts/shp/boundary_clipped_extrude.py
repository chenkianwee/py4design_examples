from py4design import py3dmodel, shp2citygml
import shapefile
import time
#specify all the shpfiles
shpfile = "F:\\kianwee_work\\smart\\DeliveryHeightDTM\\extracted_info\\punggol_primary\\shp\\punggol_primary_clipped_svy21\\punggol_primary_clipped_svy21.shp"
#the shpfile_pt should only have one single point
shpfile_pt = "F:\\kianwee_work\\smart\\DeliveryHeightDTM\\extracted_info\\punggol_primary\\shp\\punggol_primary_pt_svy21\\punggol_primary_pt_svy21.shp"
time1 = time.clock()
#specify the resultant collada file
collada_filepath = "F:\\kianwee_work\\smart\\DeliveryHeightDTM\\extracted_info\\punggol_primary\\collada\\punggol_primary_extruded.dae"
#dimensions of boundary 
bdimx = 1000
bdimy = 1000
#specify the name of the height attribute
height_attrib = "heightmedi"

#options to keep the geo reference or move the model to the origin
geo_ref = False
#===========================================================================================
#GENERATE THE 1000X1000 BOUNDARY AROUND THE SHPFILE_PT FILE
#===========================================================================================
sf_pt = shapefile.Reader(shpfile_pt)
shapeRecs_pt=sf_pt.shapeRecords()
for rec_pt in shapeRecs_pt:
    pypt_list2d = shp2citygml.get_geometry(rec_pt)
    
pypt2d = pypt_list2d[0]
pypt3d = (pypt2d[0], pypt2d[1], 0.0)

#create a rectangle boundary 
occrec = py3dmodel.construct.make_rectangle(bdimx,bdimy)
#move the rec to pypt3d
m_occrec = py3dmodel.modify.move((0,0,0),pypt3d, occrec)
m_occrec = py3dmodel.fetch.topo2topotype(m_occrec)

#===========================================================================================
#GET ALL THE SHAPES WITHIN THIS BOUNDARY
#===========================================================================================
sf = shapefile.Reader(shpfile)
shapeRecs=sf.shapeRecords()
attrib_name_list = shp2citygml.get_field_name_list(sf)
height_index = attrib_name_list.index(height_attrib) - 1
solid_list = []
for rec in shapeRecs:
    poly_attribs=rec.record
    #print poly_attribs
    height = poly_attribs[height_index]
    pypolygon_list2d = shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
        for occface in occface_list:
            if height >0:
                occsolid = py3dmodel.construct.extrude(occface, (0,0,1), height)
                solid_list.append(occsolid)
                
#extrude the boundary to get the shp inside the boundary
extrude_m_occrec = py3dmodel.construct.extrude(m_occrec, (0,0,1),1000)
#boolean the boundary and clipped out the rest of the bldgs
shp_in_boundary_cmpd = py3dmodel.construct.make_compound(solid_list)
shp_in_boundary_cmpd = py3dmodel.construct.boolean_common(shp_in_boundary_cmpd, extrude_m_occrec)

if geo_ref == True:
    b_solid_list = py3dmodel.fetch.topo_explorer(shp_in_boundary_cmpd, "solid")
    boundary_shell = py3dmodel.construct.make_shell([m_occrec])
    b_solid_list.append(boundary_shell)
    
if geo_ref == False:
    shp_in_boundary_cmpd = py3dmodel.modify.move(pypt3d, (0,0,0), shp_in_boundary_cmpd)
    b_solid_list = py3dmodel.fetch.topo_explorer(shp_in_boundary_cmpd, "solid")
    boundary_shell = py3dmodel.construct.make_shell([occrec])
    b_solid_list.append(boundary_shell)
    
time2 = time.clock()
time_spent = (time2-time1)/60.0
print time_spent
py3dmodel.export_collada.write_2_collada(b_solid_list, collada_filepath)