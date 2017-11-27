import os
import time

import shapefile
import collada
from collada import polylist, triangleset
from py4design import py3dmodel

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "dae", "example1.dae")

#or just insert a dae and citygml file you would like to analyse here:
dae_file = "F:\\kianwee_work\\smart\\nov2017-mar2018\\shp4juan\\dae\\area_c_4_cooling_spore.dae"
dae_file2 = "F:\\kianwee_work\\smart\\nov2017-mar2018\\shp4juan\\dae\\test\\area_c_4_cooling_spore1by1.dae"
shp_file = "F:\\kianwee_work\\smart\\nov2017-mar2018\\shp4juan\\shp\\test\\area_c_4_cooling_spore1by1.shp"
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
time1 = time.clock()
print "READING COLLADA FILE ... ..."
xdim = 1
ydim = 1
display_2dlist = []
colour_list = []
occface_list = []

def redraw_occfaces(occcompound):
    #redraw the surfaces so the domain are right
    #TODO: fix the scaling 
    faces = py3dmodel.fetch.topo_explorer(occcompound, "face")
    recon_faces = []
    for face in faces:
        pyptlist = py3dmodel.fetch.points_frm_occface(face)
        recon_face = py3dmodel.construct.make_polygon(pyptlist)
        recon_faces.append(recon_face)
        
    edges = py3dmodel.fetch.topo_explorer(occcompound, "edge")
    recon_edges = []
    for edge in edges:
        epyptlist = py3dmodel.fetch.points_frm_edge(edge)
        recon_edges.append(py3dmodel.construct.make_edge(epyptlist[0], epyptlist[1]))
        
    return recon_faces, recon_edges

def pyptlist3222d(pyptlist3d):
    pyptlist2d = []
    for pypt in pyptlist3d:
        pyptlist2d.append((pypt[0], pypt[1]))
    return pyptlist2d

mesh = collada.Collada(dae_file)
unit = mesh.assetInfo.unitmeter or 1
geoms = mesh.scene.objects('geometry')
geoms = list(geoms)
g_cnt = 0
#print len(geoms)
for geom in geoms:   
    prim2dlist = list(geom.primitives())
    for primlist in prim2dlist:     
        if primlist:
            #display_list.append([])
            for prim in primlist:
                if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                    pyptlist = prim.vertices.tolist()
                    if pyptlist:
                        occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                        is_face_null = py3dmodel.fetch.is_face_null(occpolygon)
                        if not is_face_null:
                            occface_list.append(occpolygon)
                    g_cnt +=1
                        

print len(occface_list)
#occface_list = occface_list[0:1000]
#make a compound from all the faces
cmpd = py3dmodel.construct.make_compound(occface_list)
#get the centre pt for bbox
ref_pt = py3dmodel.calculate.get_centre_bbox(cmpd)
ref_pt = (ref_pt[0],ref_pt[1],0)
#scale the geometry to the right units
scaled_shape = py3dmodel.modify.scale(cmpd, unit,ref_pt)
recon_faces, recon_edges = redraw_occfaces(scaled_shape)
scaled_cmpd = py3dmodel.construct.make_compound(recon_faces)
#get the bounding box of the cmpd
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(scaled_cmpd)
#draw the bounding box footprint
zmax_plus = zmax + 10
footprint_pyptlist = [(xmin,ymax,zmax_plus ), (xmin,ymin,zmax_plus ), (xmax,ymin,zmax_plus), (xmax,ymax,zmax_plus)]
bbfootprint = py3dmodel.construct.make_polygon(footprint_pyptlist)
#grid the bbfootpront
print "GRIDDING THE BOUNDARY FOOTPRINT ... ..."
occgrid_list = py3dmodel.construct.grid_face(bbfootprint, xdim, ydim)
ngrid = len(occgrid_list)
print ngrid
extrude_list = []
intersection_list = []

print "WRITING TO SHAPEFILE ... ... "
w = shapefile.Writer(shapeType = 5)
w.field('height','F',20, 5)
#write the grids into shapefile
gcnt = 0
for g in occgrid_list:
    g_mid_pt = py3dmodel.calculate.face_midpt(g)
    interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(scaled_cmpd, g_mid_pt, (0,0,-1))
    if interpt:
        zmax1 = interpt[2]
        height = zmax1-zmin
        #get the points from the grids
        pyptlist3d = py3dmodel.fetch.points_frm_occface(g)
        pyptlist2d = pyptlist3222d(pyptlist3d)
        w.poly(parts = [pyptlist2d])
        w.record(height)
        extrude = py3dmodel.construct.extrude(g,(0,0,1),height)
        extrude_moved = py3dmodel.modify.move(g_mid_pt, (g_mid_pt[0], g_mid_pt[1], zmin), extrude)
        extrude_list.append(extrude_moved)
    if gcnt%100.0 == 0:
        print "WRITING SHAPEFILE ... ...", gcnt, "/", ngrid
    gcnt+=1

w.save(shp_file)
time2 = time.clock()
time_taken = (time2-time1)/60.0
print "TIME TAKEN:", time_taken


display_2dlist.append(recon_faces)
colour_list.append("WHITE")
e_cmpd = py3dmodel.construct.make_compound(extrude_list)
e_edges = py3dmodel.fetch.topo_explorer(e_cmpd, "edge")
display_2dlist.append(e_edges)
colour_list.append("BLACK")
print "WRITING COLLADA ... ..."
py3dmodel.export_collada.write_2_collada(occgrid_list, dae_file2, occedge_list = e_edges)
print "DONE WRITING COLLADA ... ..."
py3dmodel.utility.visualise(display_2dlist, colour_list)