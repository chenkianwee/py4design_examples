import pyliburo
import shapefile
import time
#specify all the shpfiles
shpfile = "F:\\kianwee_work\\case_study\\telok_kurau\\shp\\telok_kurau_polygon_svy21\\telok_kurau_polygon_svy21.shp"
#the shpfile_pt should only have one single point
shpfile_pt = "F:\\kianwee_work\\case_study\\telok_kurau\\shp\\408_joo_chiat_pl_svy21\\408_joo_chiat_pl_svy21.shp"
collada_filepath = "F:\\kianwee_work\\case_study\\telok_kurau\\collada\\telok_kurau.dae"
txt_filepath = "F:\\kianwee_work\\case_study\\telok_kurau\\txt\\telok_kurau.txt"
time1 = time.clock()
#===========================================================================================
#GENERATE THE 500X500 BOUNDARY AROUND THE SHPFILE_PT FILE
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
solid_list = []
for rec in shapeRecs:
    poly_attribs=rec.record
    height = poly_attribs[0]
    pypolygon_list2d = pyliburo.shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = pyliburo.shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = pyliburo.py3dmodel.construct.make_occfaces_frm_pypolygons(pypolygon_list3d)
        for occface in occface_list:
            if height >0:
                occsolid = pyliburo.py3dmodel.construct.extrude(occface, (0,0,1), height)
                solid_list.append(occsolid)
        
#extrude the boundary to get the shp inside the boundary
extrude_m_occrec = pyliburo.py3dmodel.construct.extrude(m_occrec, (0,0,1),1000)
#all the faces as a compound 
shp_in_boundary_cmpd = pyliburo.py3dmodel.construct.make_compound(solid_list)
shp_in_boundary_cmpd = pyliburo.py3dmodel.construct.boolean_common(shp_in_boundary_cmpd, extrude_m_occrec)

#===========================================================================================
#GRID THE BOUNDARY IN 5X5m AND CALCULATE THE VERTICAL SURFACE AREA
#===========================================================================================
#get all the vertical surface
b_solid_list = pyliburo.py3dmodel.fetch.geom_explorer(shp_in_boundary_cmpd, "solid")
total_facade_list = []
for solid in b_solid_list:
    facade_list, roof_list, footprint_list = pyliburo.gml3dmodel.identify_building_surfaces(solid)
    total_facade_list.extend(facade_list)

facade_cmpd = pyliburo.py3dmodel.construct.make_compound(total_facade_list)

grid_face_list = pyliburo.py3dmodel.construct.grid_face(m_occrec, 100.0,100.0)
#pyliburo.py3dmodel.construct.visualise([grid_face_list[0:35]], ["WHITE"])


grid_facade_2dlist = []
total_grid_facade_list = []
for grid_face in grid_face_list:
    #extrude each grid face
    grid_facade_2dlist.append([])
    grid_extruded = pyliburo.py3dmodel.construct.extrude(grid_face, (0,0,1), 1000)
    grid_facade_cmpd = pyliburo.py3dmodel.construct.boolean_common(facade_cmpd, grid_extruded)
    is_cmpd_null = pyliburo.py3dmodel.fetch.is_compound_null(grid_facade_cmpd)
    if not is_cmpd_null:
        grid_facade_list = pyliburo.py3dmodel.fetch.geom_explorer(grid_facade_cmpd, "face")
        gcnt = 0
        for grid_facade in grid_facade_list:
            grid_facade_list2 = grid_facade_list[:]
            del grid_facade_list2[gcnt]
            r_grid_facade_cmpd = pyliburo.py3dmodel.construct.make_compound(grid_facade_list2)
            grid_facade_diff = pyliburo.py3dmodel.construct.boolean_difference(grid_facade, r_grid_facade_cmpd)
            is_diffcmpd_null = pyliburo.py3dmodel.fetch.is_compound_null(grid_facade_diff)
            if not is_diffcmpd_null:
                grid_facade_diff_list = pyliburo.py3dmodel.fetch.geom_explorer(grid_facade_diff, "face")
                grid_facade_2dlist[-1].extend(grid_facade_diff_list)
                total_grid_facade_list.extend(grid_facade_diff_list)
            gcnt+=1
            
area_list = []
for grid_facade_list in grid_facade_2dlist:
    area = 0
    for grid_facade in grid_facade_list:
        area = area +  pyliburo.py3dmodel.calculate.face_area(grid_facade)
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

edge_list = pyliburo.py3dmodel.fetch.geom_explorer(facade_cmpd, "edge")
pyliburo.utility3d.write_2_collada_falsecolour(grid_face_list, area_list, "m2", 
                                               collada_filepath,other_occedge_list = edge_list )
time2 = time.clock()
time_spent = (time2-time1)/60.0
print time_spent
#pyliburo.py3dmodel.construct.visualise([grid_face_list,total_grid_facade_list], ["WHITE", "RED"])
