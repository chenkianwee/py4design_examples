import pyliburo
import shapefile
import time
#specify all the shpfiles
shpfile = "F:\\kianwee_work\\case_study\\telok_kurau\\shp\\telok_kurau_polygon_svy21\\telok_kurau_polygon_svy21.shp"
#the shpfile_pt should only have one single point
shpfile_pt = "F:\\kianwee_work\\case_study\\telok_kurau\\shp\\408_joo_chiat_pl_svy21\\408_joo_chiat_pl_svy21.shp"
time1 = time.clock()

collada_filepath = "F:\\kianwee_work\\case_study\\telok_kurau\\collada\\telok_kurau_footprint_35.dae"
txt_filepath = "F:\\kianwee_work\\case_study\\telok_kurau\\txt\\telok_kurau_footprint_35.txt"
xdim = 35.0
ydim = 35.0
#===========================================================================================
#GENERATE THE 1000X1000 BOUNDARY AROUND THE SHPFILE_PT FILE
#===========================================================================================
sf_pt = shapefile.Reader(shpfile_pt)
shapeRecs_pt=sf_pt.shapeRecords()
for rec_pt in shapeRecs_pt:
    pypt_list2d = pyliburo.shp2citygml.get_geometry(rec_pt)
    
pypt2d = pypt_list2d[0]
pypt3d = (pypt2d[0], pypt2d[1], 0.0)

#create a rectangle boundary 
occrec = pyliburo.py3dmodel.construct.make_rectangle(1000,1000)
#move the rec to pypt3d
m_occrec = pyliburo.py3dmodel.modify.move((0,0,0),pypt3d, occrec)
m_occrec = pyliburo.py3dmodel.fetch.shape2shapetype(m_occrec)

#===========================================================================================
#GET ALL THE SHAPES WITHIN THIS BOUNDARY
#===========================================================================================
sf = shapefile.Reader(shpfile)
shapeRecs=sf.shapeRecords()
attrib_name_list = pyliburo.shp2citygml.get_field_name_list(sf)
total_occface_list = []
for rec in shapeRecs:
    poly_attribs=rec.record
    height = poly_attribs[0]
    pypolygon_list2d = pyliburo.shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = pyliburo.shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = pyliburo.py3dmodel.construct.make_occfaces_frm_pypolygons(pypolygon_list3d)
        total_occface_list.extend(occface_list)
        
#extrude the boundary to get the shp inside the boundary
extrude_m_occrec = pyliburo.py3dmodel.construct.extrude(m_occrec, (0,0,1),1000)
#all the faces as a compound 
shp_in_boundary_cmpd = pyliburo.py3dmodel.construct.make_compound(total_occface_list)
shp_in_boundary_cmpd = pyliburo.py3dmodel.construct.boolean_common(shp_in_boundary_cmpd, extrude_m_occrec)

#===========================================================================================
#GRID THE BOUNDARY AND CALCULATE THE FOOTPRINT SURFACE AREA
#===========================================================================================
grid_face_list = pyliburo.py3dmodel.construct.grid_face(m_occrec, xdim, ydim)
#pyliburo.py3dmodel.construct.visualise([grid_face_list[0:35]], ["WHITE"])

grid_footprint_2dlist = []
total_grid_footprint_list = []
for grid_face in grid_face_list:
    #extrude each grid face
    grid_footprint_2dlist.append([])
    grid_extruded = pyliburo.py3dmodel.construct.extrude(grid_face, (0,0,1), 1000)
    grid_footprint_cmpd = pyliburo.py3dmodel.construct.boolean_common(shp_in_boundary_cmpd, grid_extruded)
    is_cmpd_null = pyliburo.py3dmodel.fetch.is_compound_null(grid_footprint_cmpd)
    if not is_cmpd_null:
        grid_footprint_list = pyliburo.py3dmodel.fetch.geom_explorer(grid_footprint_cmpd, "face")
        grid_footprint_2dlist[-1].extend(grid_footprint_list)
        total_grid_footprint_list.extend(grid_footprint_list)
            
area_list = []
for grid_footprint_list in grid_footprint_2dlist:
    area = 0
    for grid_footprint in grid_footprint_list:
        area = area +  pyliburo.py3dmodel.calculate.face_area(grid_footprint)
    area_list.append(area)
    

f = open(txt_filepath,"w")
acnt = 0
for area in area_list:
    if acnt == len(area_list)-1:
        f.write(str(area))
    else:
        f.write(str(area)+"\n")
    acnt+=1
    
f.close()

total_footprint_cmpd = pyliburo.py3dmodel.construct.make_compound(total_grid_footprint_list)
edge_list = pyliburo.py3dmodel.fetch.geom_explorer(total_footprint_cmpd, "edge")
pyliburo.utility3d.write_2_collada_falsecolour(grid_face_list, area_list, "m2", 
                                               collada_filepath,other_occedge_list = edge_list )

print "TOTAL FOOTPRINT AREA:", sum(area_list)
time2 = time.clock()
time_spent = (time2-time1)/60.0
print time_spent
#pyliburo.py3dmodel.construct.visualise([grid_face_list,total_grid_facade_list], ["WHITE", "RED"])


