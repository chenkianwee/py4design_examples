import os
import time
from pyliburo import py3dmodel, urbangeom, shp2citygml
import shapefile
import gdal
import numpy as np

#===========================================================================================
#INPUTS
#===========================================================================================
bldg_footprint_shp_file = "F:\\kianwee_work\\smart\\DeliveryHeightDTM\\punggol_bldg_footprint\\punggol_bldg_footprint_lesser.shp"
dtm_tif_file = "F:\\kianwee_work\\smart\\DeliveryHeightDTM\\punggol_dtm\\punggol_dtm_1.tif"

#specify the name of the height attribute
height_attrib = "heightmedi"

#specify the directory to store the results which includes
#north_facade, south_facade, east_facade, west_facade, roof, footprint and terrain collada file 
result_directory = "F:\\kianwee_work\\smart\\DeliveryHeightDTM\\dae"

#specify if you want to view the result interactively
viewer = True
#===========================================================================================
#FUNCTIONS
#===========================================================================================
def raster_reader(input_terrain_raster):
    '''
    __author__ = "Paul Neitzel, Kian Wee Chen"
    __copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
    __credits__ = ["Paul Neitzel", "Jimeno A. Fonseca"]
    __license__ = "MIT"
    __version__ = "0.1"
    __maintainer__ = "Daren Thomas"
    __email__ = "cea@arch.ethz.ch"
    __status__ = "Production"
    '''
    # read raster records
    raster_dataset = gdal.Open(input_terrain_raster)
    band = raster_dataset.GetRasterBand(1)
    a = band.ReadAsArray(0, 0, raster_dataset.RasterXSize, raster_dataset.RasterYSize)
    (y_index, x_index) = np.nonzero(a >= 0)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster_dataset.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2)  # add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2)  # to centre the point

    return [(x, y, z) for x, y, z in zip(x_coords, y_coords, a[y_index, x_index])]

#===========================================================================================
#THE RESULT FILES
#===========================================================================================
north_facade_collada_filepath = os.path.join(result_directory, "north_facade.dae")
south_facade_collada_filepath = os.path.join(result_directory, "south_facade.dae")
east_facade_collada_filepath = os.path.join(result_directory, "east_facade.dae")
west_facade_collada_filepath = os.path.join(result_directory, "west_facade.dae")
roof_collada_filepath = os.path.join(result_directory, "roof.dae")
footprint_collada_filepath = os.path.join(result_directory, "footprint.dae")
terrain_collada_filepath = os.path.join(result_directory, "terrain.dae")
#===========================================================================================
#CONSTRUCT THE TERRAIN 
#===========================================================================================
time1 = time.clock()
display_2dlist = []
#read the tif terrain file and create a tin from it 
pyptlist = raster_reader(dtm_tif_file)
print "CONSTRUCTING THE TERRAIN ... ..."
tin_occface_list = py3dmodel.construct.delaunay3d(pyptlist)
terrain_shell = py3dmodel.construct.sew_faces(tin_occface_list)[0]
#===========================================================================================
#EXTRUDE THE BUILDING
#===========================================================================================
sf = shapefile.Reader(bldg_footprint_shp_file)
shapeRecs=sf.shapeRecords()
attrib_name_list = shp2citygml.get_field_name_list(sf)
height_index = attrib_name_list.index(height_attrib) - 1

solid_list = []
face_list = []

print "EXTRUDING THE BUILDINGS ... ..."
cnt = 0
for rec in shapeRecs:
    poly_attribs=rec.record
    height = poly_attribs[height_index]
    pypolygon_list2d = shp2citygml.get_geometry(rec)
    if pypolygon_list2d:
        pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
        occface_list = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
        for occface in occface_list:
            if height >0:
                occsolid = py3dmodel.construct.extrude(occface, (0,0,1), height)
                solid_list.append(occsolid)
                face_list.append(occface)
    cnt+=1

#move all the faces to a very high elevation and project them down onto the terrain so that we know where to place the buildings
face_cmpd = py3dmodel.construct.make_compound(face_list)
f_midpt = py3dmodel.calculate.get_centre_bbox(face_cmpd)
loc_pt = [f_midpt[0], f_midpt[1], 1000]
t_face_cmpd = py3dmodel.modify.move(f_midpt, loc_pt, face_cmpd)
face_list2 = py3dmodel.fetch.topo_explorer(t_face_cmpd, "face")
#face_list2 = face_list2[0:50]

msolid_list = []

print "PLACING THE BUILDINGS ... ..."
fcnt = 0
for face2 in face_list2:
    pyptlist = py3dmodel.fetch.points_frm_occface(face2)
    #print "NUM PTS:", len(pyptlist)
    z_list = []
    for pypt in pyptlist:
        interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(terrain_shell, pypt, (0,0,-1))
        if interpt:
            z = interpt[2]
            z_list.append(z)
    if z_list:
        min_z = min(z_list)
        #print min_z
        face = face_list[fcnt]
        face_midpt = py3dmodel.calculate.face_midpt(face)
        bldg_loc_pt = [face_midpt[0], face_midpt[1], min_z]
        bsolid = solid_list[fcnt]
        m_bsolid = py3dmodel.modify.move(face_midpt, bldg_loc_pt, bsolid)
        msolid_list.append(m_bsolid)
    fcnt+=1
            
print "CLASSFYING THE BUILDING SURFACES ... ..."
total_facade_list = []
total_roof_list = []
total_footprint_list = []
for solid in msolid_list:
    facade_list, roof_list, footprint_list = urbangeom.identify_building_surfaces(solid)
    total_facade_list.extend(facade_list)
    total_roof_list.extend(roof_list)
    total_footprint_list.extend(footprint_list)
    
n_list,s_list, e_list, w_list=urbangeom.identify_surface_direction(total_facade_list)

print "WRITING THE BUILDING SURFACES ... ..."
py3dmodel.export_collada.write_2_collada(n_list, north_facade_collada_filepath)
py3dmodel.export_collada.write_2_collada(s_list, south_facade_collada_filepath)
py3dmodel.export_collada.write_2_collada(e_list, east_facade_collada_filepath)
py3dmodel.export_collada.write_2_collada(w_list, west_facade_collada_filepath)
py3dmodel.export_collada.write_2_collada(total_roof_list, roof_collada_filepath)
py3dmodel.export_collada.write_2_collada(total_footprint_list, footprint_collada_filepath)
py3dmodel.export_collada.write_2_collada([terrain_shell], terrain_collada_filepath)

time2 = time.clock()
time = (time2-time1)/60.0
print "TOTAL PROCESSING TIME:", time, "mins"

if viewer == True:
    cmpd = py3dmodel.construct.make_compound(msolid_list)
    display_2dlist.append([cmpd])
    display_2dlist.append([terrain_shell])
    py3dmodel.utility.visualise(display_2dlist, ["RED", "WHITE"])