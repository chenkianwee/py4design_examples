import os
import time
from py4design import py3dmodel, urbangeom, shp2citygml
import shapefile

#===========================================================================================
#INPUTS
#===========================================================================================
pln_shp_file = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\shp\\planning_area_age_gender_2016_svy21\\planning_area_age_gender_2016.shp"
park_shp_file = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\shp\\parks_spore_svy21\\parks_spore.shp"
sport_shp_file = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\shp\\sports_centre_svy21\\sports_centre3.shp"
#specify the directory to store the results which includes
#north_facade, south_facade, east_facade, west_facade, roof, footprint and terrain collada file 
result_directory = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\shp\\proximity2parks"
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def write2shp(pyptlist2d_list, height_list, height_list2, height_list3, shp_filepath):
    w = shapefile.Writer(shapeType = 5)
    w.field('prox2park','F',20, 5)
    w.field('prox2sport','F',20, 5)
    w.field('pop_d','F',20, 5)
    cnt = 0
    for pyptlist2d in pyptlist2d_list:
        w.poly(parts = [pyptlist2d])
        height = height_list[cnt]
        height2 = height_list2[cnt]
        height3 = height_list3[cnt]

        w.record(height, height2, height3)
        cnt+=1
    w.save(shp_filepath)
#===========================================================================================
#GET THE PLANNING AREAS
#===========================================================================================
time1 = time.clock()
display_2dlist = []
colour_list = []

sf = shapefile.Reader(pln_shp_file)
shapeRecs=sf.shapeRecords()
attrib_name_list = shp2citygml.get_field_name_list(sf)


grid_list = []
pop_d_list = []
print "GRID THE PLANNING AREAS ... ..."
for rec in shapeRecs:
    poly_attribs=rec.record
    pop = poly_attribs[2]
    pypolygon_list2d = shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
        for occface in occface_list:
            larea = py3dmodel.calculate.face_area(occface)
            if pop !=0:
                pop_d = larea/pop
            else:
                pop_d = 10000
            grids = py3dmodel.construct.grid_face(occface, 1000, 1000)
            ngrid = len(grids)
            grid_list.extend(grids)
            for _ in range(ngrid):
                pop_d_list.append(pop_d)
    
print "GET ALL THE PARKS ... ..."
sf2 = shapefile.Reader(park_shp_file)
shapeRecs2=sf2.shapeRecords()
attrib_name_list2 = shp2citygml.get_field_name_list(sf2)

park_list = []
for rec in shapeRecs2:
    poly_attribs=rec.record
    point_list = shp2citygml.get_geometry(rec)
    park_list.extend(point_list)
    
print "GET ALL THE SPORT CENTRE ... ..."
sf3 = shapefile.Reader(sport_shp_file)
shapeRecs3=sf3.shapeRecords()
attrib_name_list3 = shp2citygml.get_field_name_list(sf3)

sport_list = []
for rec in shapeRecs3:
    poly_attribs=rec.record
    pypolygon_list2d = shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
        for occface in occface_list:
            c_pt = py3dmodel.calculate.face_midpt(occface)
            v = py3dmodel.construct.make_vertex(c_pt)
            sport_list.append(c_pt)    

print "MEASURE THE DISTANCE TO ... ..."
min_dist_list = []
min_dist_list2 = []
pyptlist_2dlist = []
for grid in grid_list:
    c_pt = py3dmodel.calculate.face_midpt(grid)
    pyptlist = py3dmodel.fetch.points_frm_occface(grid)
    pyptlist_2dlist.append(pyptlist)
    
    min_dist = float("inf")
    for park in park_list:
        park.append(0.0)
        dist = py3dmodel.calculate.distance_between_2_pts(c_pt, park)
        if dist < min_dist:
            min_dist = dist
    min_dist_list.append(min_dist)
    
    min_dist2 = float("inf")
    for sport in sport_list:
        dist = py3dmodel.calculate.distance_between_2_pts(c_pt, sport)
        if dist < min_dist2:
            min_dist2 = dist
    min_dist_list2.append(min_dist2)
    
res_shp = os.path.join(result_directory, "prox2park.shp")
write2shp(pyptlist_2dlist, min_dist_list, min_dist_list2, pop_d_list, res_shp)
py3dmodel.utility.visualise_falsecolour_topo(grid_list, pop_d_list)