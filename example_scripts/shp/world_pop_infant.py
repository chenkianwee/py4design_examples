import time
import csv

import shapefile
from py4design import py3dmodel
from py4design import shp2citygml

#===========================================================================================
#INPUTS
#===========================================================================================
world_shp_filepath = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\shp\\TM_WORLD_BORDERS_SIMPL-0.3\\TM_WORLD_BORDERS_SIMPL-0.3.shp"
csv_filepath = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\csv\\indicator gapminder population.csv"
csv_filepath2 = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\csv\\Indicator_Average age.csv"
#specify the directory to store the results which includes
#north_facade, south_facade, east_facade, west_facade, roof, footprint and terrain collada file 
result_directory = "F:\\kianwee_work\\nus\\201804-201810\\beijing_workshop\\shp\\world_pop"
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

with open(csv_filepath) as f:
    reader = csv.DictReader(f)
    data = [r for r in reader]

with open(csv_filepath2) as f2:
    reader2 = csv.DictReader(f2)
    data2 = [r for r in reader2]
    
print len(data)
print len(data2)

'''
print data[259]
sf = shapefile.Reader(world_shp_filepath)
shapeRecs=sf.shapeRecords()
attrib_name_list = shp2citygml.get_field_name_list(sf)
name_index = attrib_name_list.index("NAME")


match = 0
non_match_ctries = []
for rec in shapeRecs:
    match_status = False
    poly_attribs=rec.record
    ctry_name1 = poly_attribs[name_index-1]
    for d in data:
        ctry_name2 = d["Total population"]
        if ctry_name2 == ctry_name1:
            match+=1
            match_status = True
            break
            #print "MATCH"
    if match_status == False:
        non_match_ctries.append(ctry_name1)
        
print match, "/", len(shapeRecs)
print non_match_ctries


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
'''