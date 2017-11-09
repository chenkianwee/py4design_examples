import os
import time 
import uuid

import shapefile
from py4design import shp2citygml, py3dmodel, gml3dmodel, pycitygml
#=========================================================================================================================================
#main convert function
#=========================================================================================================================================
def findmedian(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0
        
def perror(building, num_storeys, perror_list, inacc_buildings):
    if "building_l" in building:
        orig_lvl = building["building_l"]
        percentage_error = float(num_storeys)/float(orig_lvl)
        perror_list.append(percentage_error)
        if (percentage_error) > 1.2 or (percentage_error) < 0.8:
            inacc_buildings.append(building)
        
def if_blevel(building, blevel_list):
    if "building_l" in building:
        blevel_list.append(building)
            
def convert_ptshpfile(field_name_list, shapeRecs, citygml):
    name_index = field_name_list.index("name")-1
    station_index = field_name_list.index("station")-1
    highway_index = field_name_list.index("highway")-1
    trpst_bldg_list = []
    for rec in shapeRecs:
        poly_attribs=rec.record
        highway = poly_attribs[highway_index]
        highway.strip()
        station = poly_attribs[station_index]
        station.strip()
        name = poly_attribs[name_index]
        name.strip()
        
        if highway == "bus_stop":
            if name.isspace():
                name = "bus_stop" + str(uuid.uuid1())
            generic_attrib_dict = {"highway":highway}
            #transform to the location of the bus stop
            bus_stop_box = py3dmodel.construct.make_box(5,2,3)
            shp_pts = rec.shape.points
            for pt in shp_pts:
                pt3d = shp2citygml.pypt2d_2_3d(pt,0.0)
                stopbox = shp2citygml.create_transit_stop_geometry(bus_stop_box,pt3d)
                face_list = py3dmodel.fetch.faces_frm_solid(stopbox)
                #get the surfaces from the solid 
                geometry_list = gml3dmodel.write_gml_srf_member(face_list)
                    
            citygml.add_cityfurniture("lod1", name, geometry_list, furn_class = "1000", function = "1110", 
                                      generic_attrib_dict = generic_attrib_dict)
         
        if not station.isspace():
            if name.isspace():
                name = station + str(uuid.uuid1())
            generic_attrib_dict = {"station":station}
            #create a bus stop geometry based on the point
            station_height = 8
            station_storey = 2
            storey_blw_grd = 0
            
            #transform to the location of the bus stop
            transit_station_box = py3dmodel.construct.make_box(5,20,3)
            shp_pts = rec.shape.points
            for pt in shp_pts:
                pt3d = shp2citygml.pypt2d_2_3d(pt, 0.0)
                stationbox = shp2citygml.create_transit_stop_geometry(transit_station_box,pt3d)
                face_list = py3dmodel.fetch.faces_frm_solid(stationbox)
                #get the surfaces from the solid 
                geometry_list = gml3dmodel.write_gml_srf_member(face_list)
                    
            trpst_bldg_list.append(name)                
            citygml.add_building("lod1", name, geometry_list, bldg_class = "1170", function ="2480", 
            usage = "2480", rooftype ="1000", height = str(station_height),
             stry_abv_grd = str(station_storey), stry_blw_grd = str(storey_blw_grd), generic_attrib_dict = generic_attrib_dict)   
             
    return trpst_bldg_list
             
def convert_polylineshpfile(field_name_list, shapeRecs, citygml):
    railway_index = field_name_list.index("railway")-1
    name_index = field_name_list.index("name")-1
    highway_index = field_name_list.index("highway")-1
    count_shapes = 0
    for rec in shapeRecs:
        poly_attribs=rec.record
        railway = poly_attribs[railway_index]
        railway.strip()
        highway = poly_attribs[highway_index]
        highway.strip()
        name = poly_attribs[name_index]
        name.strip()
        
        if not railway.isspace():
            generic_attrib_dict = {"railway":railway}
            shp2citygml.trpst2citygml("Railway", rec, name, railway, generic_attrib_dict, citygml)
            
        if not highway.isspace():
            generic_attrib_dict = {"highway":highway}
            shp2citygml.trpst2citygml("Road", rec, name, highway, generic_attrib_dict, citygml)
        
        count_shapes+=1
        
def convert_apolygon(rec, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list):
    poly_attribs=rec.record
    landuse = poly_attribs[landuse_index]
    landuse.strip()
    building = poly_attribs[building_index]
    building.strip()
    name = poly_attribs[name_index]
    name.strip()
    total_build_up = 0
    perror_list = []
    constr_buildings = []
    inacc_buildings = []
    #=======================================================================================================
    #if the polygon has no building attrib and has a landuse attribute it is a landuse
    #=======================================================================================================               
    if building == "" and landuse != "":
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occface_list = py3dmodel.construct.make_occfaces_frm_pypolygons(pypolygon_list3d)
            geometry_list = gml3dmodel.write_gml_srf_member(occface_list)
                
            if name.isspace():
                name = "plot" + str(count_shapes)
            
            function = shp2citygml.map_osm2citygml_landuse_function(landuse)
            generic_attrib_dict = {"landuse":landuse}
            
            plot_ratio =  poly_attribs[plot_ratio_index]
            if plot_ratio != None:
                generic_attrib_dict["plot_ratio"] = plot_ratio

            plot_area = shp2citygml.get_plot_area(rec)
            generic_attrib_dict["plot_area"] = plot_area
            
            citygml.add_landuse("lod1", name, geometry_list, function = function, generic_attrib_dict = generic_attrib_dict)
            
            #=======================================================================================================
            #find the buildings that belong to this plot
            #=======================================================================================================
            buildings_on_plot_list = shp2citygml.buildings_on_plot(rec, building_list)
            
            in_construction = False
            #check if any of the buildings are under construction 
            for cbuilding in buildings_on_plot_list:
                if cbuilding["building"] == "construction":
                    in_construction = True
                    constr_buildings.append(cbuilding)
                    
            if not in_construction:
                #then separate the buildings that are parkings and usable floor area 
                parking_list = []
                not_parking_list = list(buildings_on_plot_list)
                for building in buildings_on_plot_list:
                    if "amenity" in building:
                        if building["amenity"] == "parking" or building["amenity"] == "carpark" :
                            parking_list.append(building)
                            not_parking_list.remove(building)
                            
                #then measure the total building footprint on this plot
                build_footprint = 0 
                for not_parking in not_parking_list:
                    bgeom_list = not_parking["geometry"]
                    for bgeom in bgeom_list:
                        build_footprint = build_footprint + py3dmodel.calculate.face_area(bgeom)
                        
                #then measure the total parking footprint on this plot
                multi_parking_footprint = 0
                for parking in parking_list:
                    bgeom_list = parking["geometry"]
                    for bgeom in bgeom_list:
                        multi_parking_footprint = multi_parking_footprint + py3dmodel.calculate.face_area(bgeom)
    
                #base on the footprints calculate how many storeys are the buildings
                if build_footprint !=0:
                    residential_height = 3
                    commercial_height = 4
    
                    if plot_ratio != None:
                        total_build_up = total_build_up + (plot_area*plot_ratio)
                        num_storeys = int(round(total_build_up/build_footprint))
                        
                        if landuse == "residential":
                            height = num_storeys*residential_height
                            
                            if multi_parking_footprint !=0:
                                #base on the parking footprint estimate how high the multistorey carpark should be 
                                total_parking_area = shp2citygml.calc_residential_parking_area(total_build_up)
                                parking_storeys = int(round(total_parking_area/multi_parking_footprint))
                                parking_storey_height = 2.5
                                parking_height = parking_storey_height*parking_storeys
                                
                                #write the carparks as buildings
                                for parking in parking_list:
                                    perror(parking, parking_storeys, perror_list, inacc_buildings)
                                    shp2citygml.building2citygml(parking, parking_height, citygml, landuse, parking_storeys)
                                            
                        #TODO: calculate for commercial buildings in terms of parking space too 
                        else:
                            height = num_storeys*commercial_height
                            
                        
                        for not_parking in not_parking_list:
                            perror(not_parking, num_storeys, perror_list, inacc_buildings)
                            shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys)
                        
                    #================================================================================================================
                    #for those plots without plot ratio and might be educational or civic buildings
                    #================================================================================================================
                    else:
                        if landuse == "transport" or landuse == "recreation_ground" or landuse == "civic" or landuse == "place_of_worship" or landuse == "utility" or landuse == "health":
                            num_storeys = 2
                                
                        elif landuse == "education" or landuse == "commercial":
                            num_storeys = 4
                            
                        elif landuse == "residential":
                            num_storeys = 10
                            
                        elif landuse == "reserve":
                            num_storeys = 1
                        else:
                            num_storeys = 1
                        
                        for not_parking in not_parking_list:
                            height = num_storeys*commercial_height
                            perror(not_parking, num_storeys, perror_list, inacc_buildings)
                            shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys)
                            
    return total_build_up, perror_list, constr_buildings, inacc_buildings
                   
def convert_apolygon_origlvl(rec, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list):
    poly_attribs=rec.record
    landuse = poly_attribs[landuse_index]
    landuse.strip()
    building = poly_attribs[building_index]
    building.strip()
    name = poly_attribs[name_index]
    name.strip()
    total_build_up = 0
    constr_buildings = []
    blevel_list = []
    #print "CONDITIONS:", building, landuse
    #=======================================================================================================
    #if the polygon has no building attrib and has no landuse attribute it is a boundary
    #=======================================================================================================
    if building == "" and landuse == "":
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occface_list = py3dmodel.construct.make_occfaces_frm_pypolygons(pypolygon_list3d)
            occface_list2 = []
            for occface in occface_list:
                pyptlist = py3dmodel.fetch.points_frm_occface(occface)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
                if is_anticlockwise:
                    r_face = py3dmodel.modify.reverse_face(occface)
                    #nrml = py3dmodel.calculate.face_normal(r_face)
                    occface_list2.append(r_face)
                else:
                    occface_list2.append(occface)
                    
            geometry_list = gml3dmodel.write_gml_triangle(occface_list2)
            
            citygml.add_tin_relief("lod1", "terrain", geometry_list)
    #=======================================================================================================
    #if the polygon has no building attrib and has a landuse attribute it is a landuse
    #=======================================================================================================               
    if building == "" and landuse != "":
        #the geometry is stored in parts and points
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occface_list = py3dmodel.construct.make_occfaces_frm_pypolygons(pypolygon_list3d)
            geometry_list = gml3dmodel.write_gml_srf_member(occface_list)
                
            if name.isspace():
                name = "plot" + str(count_shapes)
            
            function = shp2citygml.map_osm2citygml_landuse_function(landuse)
            generic_attrib_dict = {"landuse":landuse}
            
            plot_ratio =  poly_attribs[plot_ratio_index]
            if plot_ratio != None:
                generic_attrib_dict["plot_ratio"] = plot_ratio

            plot_area = shp2citygml.get_plot_area(rec)
            generic_attrib_dict["plot_area"] = plot_area
            
            citygml.add_landuse("lod1", name,geometry_list, function = function, generic_attrib_dict = generic_attrib_dict )
            
            #=======================================================================================================
            #find the buildings that belong to this plot
            #=======================================================================================================
            buildings_on_plot_list = shp2citygml.buildings_on_plot(rec, building_list)
            in_construction = False
            #check if any of the buildings are under construction 
            for cbuilding in buildings_on_plot_list:
                if cbuilding["building"] == "construction":
                    in_construction = True
                    constr_buildings.append(cbuilding)
                    
            if not in_construction:
                #then separate the buildings that are parkings and usable floor area 
                parking_list = []
                not_parking_list = list(buildings_on_plot_list)
                for building in buildings_on_plot_list:
                    if "amenity" in building:
                        if building["amenity"] == "parking" or building["amenity"] == "carpark" :
                            parking_list.append(building)
                            not_parking_list.remove(building)
                            
                #then measure the total building footprint on this plot
                build_footprint = 0 
                for not_parking in not_parking_list:
                    bgeom_list = not_parking["geometry"]
                    for bgeom in bgeom_list:
                        build_footprint = build_footprint + py3dmodel.calculate.face_area(bgeom)
                        
                #then measure the total parking footprint on this plot
                multi_parking_footprint = 0
                for parking in parking_list:
                    bgeom_list = parking["geometry"]
                    for bgeom in bgeom_list:
                        multi_parking_footprint = multi_parking_footprint + py3dmodel.calculate.face_area(bgeom)
    
                #base on the footprints calculate how many storeys are the buildings
                if build_footprint !=0:
                    residential_height = 3
                    commercial_height = 4
    
                    if plot_ratio != None:
                        total_build_up = total_build_up + (plot_area*plot_ratio)
                        num_storeys = int(round(total_build_up/build_footprint))
                        
                        if landuse == "residential":
                            height = num_storeys*residential_height
                            
                            if multi_parking_footprint !=0:
                                #base on the parking footprint estimate how high the multistorey carpark should be 
                                total_parking_area = shp2citygml.calc_residential_parking_area(total_build_up)
                                parking_storeys = int(round(total_parking_area/multi_parking_footprint))
                                parking_storey_height = 2.5
                                parking_height = parking_storey_height*parking_storeys
                                
                                #write the carparks as buildings
                                for parking in parking_list:
                                    if "building_l" in parking:
                                        blevel_list.append(parking)
                                        parking_storeys = parking["building_l"]
                                        parking_height = parking_storey_height*parking_storeys
                                        shp2citygml.building2citygml(parking, parking_height, citygml, landuse, parking_storeys)
                                    else:
                                        shp2citygml.building2citygml(parking, parking_height, citygml, landuse, parking_storeys, )
                                            
                        #TODO: calculate for commercial buildings in terms of parking space too 
                        else:
                            height = num_storeys*commercial_height
                            
                        
                        for not_parking in not_parking_list:
                            if "building_l" in not_parking:
                                blevel_list.append(not_parking)
                                num_storeys = not_parking["building_l"]
                                if landuse == "residential":
                                    height = residential_height*num_storeys
                                else:
                                    height = commercial_height*num_storeys
                                shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys)
                            else:
                                shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys)
                        
                    #================================================================================================================
                    #for those plots without plot ratio and might be educational or civic buildings
                    #================================================================================================================
                    else:
                        if landuse == "transport" or landuse == "recreation_ground" or landuse == "civic" or landuse == "place_of_worship" or landuse == "utility" or landuse == "health":
                            num_storeys = 2
                                
                        elif landuse == "education" or landuse == "commercial":
                            num_storeys = 4
                            
                        elif landuse == "residential":
                            num_storeys = 10
                            
                        elif landuse == "reserve":
                            num_storeys = 1
                            
                        else:
                            num_storeys = 1
                        
                        for not_parking in not_parking_list:
                            if "building_l" in not_parking:
                                blevel_list.append(not_parking)
                                num_storeys = not_parking["building_l"]
                                height = commercial_height*num_storeys
                                shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys)
                            else:
                                height = num_storeys*commercial_height
                                shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys)
                            
    return total_build_up, constr_buildings, blevel_list
    
def convert_polygonshpfile(field_name_list, shapeRecs, citygml, building_list, origlvl=False):
    #the attributes are mainly base on the attributes from osm 
    landuse_index = field_name_list.index("landuse")-1
    plot_ratio_index = field_name_list.index("plot_ratio")-1
    building_index = field_name_list.index("building")-1
    name_index = field_name_list.index("name")-1
    count_shapes = 0
    total_flr_area = 0
    shp_constr_list = []
    if origlvl == False:
        shp_perror_list = []
        shp_inacc_buildings = []
        for rec in shapeRecs:
            build_footprint, perror_list,constr_list, inacc_buildings = convert_apolygon(rec, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list)         
            shp_perror_list.extend(perror_list)    
            shp_constr_list.extend(constr_list)
            shp_inacc_buildings.extend(inacc_buildings)
            total_flr_area = total_flr_area + build_footprint
            count_shapes += 1
        return shp_perror_list, shp_constr_list, shp_inacc_buildings, total_flr_area
        
    if origlvl == True:
        shp_blevel_list = []
        for rec in shapeRecs:
            build_footprint, constr_list, blevel_list = convert_apolygon_origlvl(rec, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list)         
            shp_constr_list.extend(constr_list)
            shp_blevel_list.extend(blevel_list)
            total_flr_area = total_flr_area + build_footprint                    
            count_shapes += 1
        return shp_constr_list, total_flr_area, shp_blevel_list
            

def convert(shpfile_list, citygml):
    #get the building footprints
    building_list = []
    for shpfile in shpfile_list:
        buildings = shp2citygml.get_buildings(shpfile)
        if buildings:
            building_list.extend(buildings)
            
    print "done with getting buildings"
    print "TOTAL NUMBER OF BUILDINGS:", len(building_list)
    total_perror_list = []
    total_constr_list = []
    total_trpst_bldg_list = []
    total_inacc_buildings = []
    total_build_up_area = 0
    #read the shapefiles
    for shpfile in shpfile_list:
        sf = shapefile.Reader(shpfile)
        shapeRecs=sf.shapeRecords()
        shapetype = shapeRecs[0].shape.shapeType
        
        #get the project CRS of the shapefile
        epsg_num = "EPSG:" + shp2citygml.get_shpfile_epsg(shpfile)
        field_name_list = shp2citygml.get_field_name_list(sf)
        
        #shapetype 1 is point, 3 is polyline, shapetype 5 is polygon
        #if it is a point file it must be recording the location of the bus stops and subway stations
        if shapetype == 1:
            trpst_bldg_list = convert_ptshpfile(field_name_list, shapeRecs, citygml)          
            total_trpst_bldg_list.extend(trpst_bldg_list)
            
        if shapetype == 3:
            convert_polylineshpfile(field_name_list, shapeRecs, citygml)
            
        if shapetype == 5:
            shp_perror_list, shp_constr_list, shp_inacc_buildings, total_flr_area = convert_polygonshpfile(field_name_list, shapeRecs, citygml, building_list)
            if shp_perror_list:
                total_perror_list.extend(shp_perror_list)
            if shp_constr_list:
                total_constr_list.extend(shp_constr_list)
            if shp_inacc_buildings:
                total_inacc_buildings.extend(shp_inacc_buildings)
                
            total_build_up_area = total_build_up_area + total_flr_area
                
    print "NUMBER OF BUILDINGS IN CONSTRUCTION:", len(total_constr_list)
    print "NUMBER OF MRT/LRT STATIONS:", len(total_trpst_bldg_list)
    print "NUMBER OF BUILDINGS WITH LEVEL INFORMATION:", len(total_perror_list)
    print "TOTAL BUILD UP AREA:", total_build_up_area
    print "MEAN:", (sum(total_perror_list))/(len(total_perror_list))
    print "MAX:", max(total_perror_list)
    print "MIN:", min(total_perror_list)
    print "MEDIAN:", findmedian(total_perror_list)
    print "NUMBER OF INACCURATE BUILDINGS:", len(total_inacc_buildings)
    
def convert_origlvl(shpfile_list, citygml):
    #get the building footprints
    building_list = []
    for shpfile in shpfile_list:
        buildings = shp2citygml.get_buildings(shpfile)
        if buildings:
            building_list.extend(buildings)
            
    total_constr_list = []
    total_build_up_area = 0
    total_trpst_bldg_list = []
    total_blevel_list = []
    print "done with getting buildings"
    print "TOTAL NUMBER OF BUILDINGS:", len(building_list)
    #read the shapefiles
    for shpfile in shpfile_list:
        sf = shapefile.Reader(shpfile)
        shapeRecs=sf.shapeRecords()
        shapetype = shapeRecs[0].shape.shapeType
        
        #get the project CRS of the shapefile
        epsg_num = "EPSG:" + shp2citygml.get_shpfile_epsg(shpfile)
        field_name_list = shp2citygml.get_field_name_list(sf)
        
        #shapetype 1 is point, 3 is polyline, shapetype 5 is polygon
        #if it is a point file it must be recording the location of the bus stops and subway stations
        if shapetype == 1:
            trpst_bldg_list = convert_ptshpfile(field_name_list, shapeRecs, citygml)
            total_trpst_bldg_list.extend(trpst_bldg_list)
            
        if shapetype == 3:
            convert_polylineshpfile(field_name_list, shapeRecs, citygml)
            
        if shapetype == 5:
            shp_constr_list, total_flr_area, shp_blevel_list  = convert_polygonshpfile(field_name_list, shapeRecs, citygml, building_list, origlvl=True)
            if shp_constr_list:
                total_constr_list.extend(shp_constr_list)
            if shp_blevel_list:
                total_blevel_list.extend(shp_blevel_list)
            total_build_up_area = total_build_up_area + total_flr_area
                
    print "NUMBER OF BUILDINGS IN CONSTRUCTION:", len(total_constr_list)
    print "NUMBER OF MRT/LRT STATIONS:", len(total_trpst_bldg_list)
    print "NUMBER OF BUILDINGS WITH LEVEL INFORMATION:", len(total_blevel_list)
    print "TOTAL BUILD UP AREA:", total_build_up_area
    
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================
current_path = os.path.dirname(__file__)
parent_path = parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))

#specify all the shpfiles
shpfile1 = os.path.join(parent_path, "example_files", "shpfiles", "punggol_buildings", "punggol_buildings.shp")
shpfile2 = os.path.join(parent_path, "example_files", "shpfiles", "punggol_plots", "punggol_plots.shp")
shpfile3 = os.path.join(parent_path, "example_files", "shpfiles", "punggol_trpst_network","punggol_trpst_network.shp")
shpfile4 = os.path.join(parent_path, "example_files", "shpfiles", "boundary_file", "punggol_boundary.shp")

#specify the result citygml file
citygml_filepath = os.path.join(parent_path, "example_files", "citygml", "results", "punggol.gml")
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================

#=========================================================================================================================================
#main SCRIPT
#=========================================================================================================================================
print "CONVERTING ... ..."
time1 = time.clock()  

#initialise the citygml writer
citygml_writer = pycitygml.Writer()
citygml_writer_origlvl = pycitygml.Writer()
#convert the shpfiles into 3d citygml using the citygmlenv library
convert_origlvl([shpfile1,shpfile2,shpfile3, shpfile4], citygml_writer_origlvl)
citygml_writer_origlvl.write(citygml_filepath)

convert([shpfile1,shpfile2,shpfile3],citygml_writer)
citygml_writer.write(citygml_filepath)

time2 = time.clock()
time = (time2-time1)/60.0
print "TIME TAKEN:", time
print "CityGML GENERATED"