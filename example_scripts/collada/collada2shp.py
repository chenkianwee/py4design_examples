import os
import time
import math

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
dae_file = "F:\\kianwee_work\\smart\\nov2017-mar2018\\shp4juan\\dae\\cbd.dae"
result_dir = "F:\\kianwee_work\\smart\\nov2017-mar2018\\shp4juan\\shp\\cbd_3by3_svy21"

#================================================================================
#FUNCTIONS
#================================================================================
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

def write2shp(pyptlist2d_list, height_list, shp_filepath):
    w = shapefile.Writer(shapeType = 5)
    w.field('height','F',20, 5)
    cnt = 0
    for pyptlist2d in pyptlist2d_list:
        w.poly(parts = [pyptlist2d])
        height = height_list[cnt]
        w.record(height)
        cnt+=1
    w.save(shp_filepath)
    
def index_faces(occface_list, xdim, ydim, xmin, ymin, intervali, occgrid_list, zmax_plus):
    face_dict_list = []
    for face in occface_list:
        face_dict = {}
        fxm,fym,fzm, fxmx,fymx,fzmx = py3dmodel.calculate.get_bounding_box(face)
        
        imin = int(math.floor((fxm-xmin)/xdim))
        imax = int(math.ceil((fxmx-xmin)/xdim))
        irange = range(imin, imax+1)
        
        jmin = int(math.floor((fym-ymin)/ydim))
        jmax = int(math.ceil((fymx-ymin)/ydim))
        jrange = range(jmin, jmax+1)
        
#        print "IMIN", imin
#        print "IMAX", imax
#        print "JMIN", jmin
#        print "JMAX", jmax
        
        glist = []
        for i in irange:
            for j in jrange:
                g = j*intervali+i
                glist.append(g)

        #py3dmodel.utility.visualise([[bbfootprint], occgrid_list], ["BLUE", "RED"])
        face_dict["geometry"] = face
        face_dict["grange"] = glist
        face_dict_list.append(face_dict)
        
    return face_dict_list
        
def get_occface_frm_dict_list(grid_cnt, face_dict_list):
    chosen_face_list = []
    for face_dict in face_dict_list:
        grange = face_dict["grange"]

        if grid_cnt in grange:
            chosen_face_list.append(face_dict["geometry"])
            
    return chosen_face_list
#================================================================================
#MAIN SCRIPT
#================================================================================
time1 = time.clock()
print "#============================"
print "READING COLLADA FILE ... ..."
print "#============================"
xdim = 3
ydim = 3
display_2dlist = []
colour_list = []
occface_list = []

ref_dir = [0,0,1]

mesh = collada.Collada(dae_file)
unit = mesh.assetInfo.unitmeter or 1
geoms = mesh.scene.objects('geometry')
geoms = list(geoms)
g_cnt = 0
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
                            n = py3dmodel.calculate.face_normal(occpolygon)
                            angle = py3dmodel.calculate.angle_bw_2_vecs(ref_dir,n)
                            if angle <90:
                                occface_list.append(occpolygon)
                    g_cnt +=1
        
print "NUMBER OF FACES IN THE COLLADA FILE THAT HAS NORMAL FACING UPWARDS:", len(occface_list)
#make a compound from all the faces
cmpd = py3dmodel.construct.make_compound(occface_list)
#get the centre pt for bbox
ref_pt = py3dmodel.calculate.get_centre_bbox(cmpd)
ref_pt = (ref_pt[0],ref_pt[1],0)
#scale the geometry to the right units
scaled_shape = py3dmodel.modify.scale(cmpd, unit,ref_pt)
recon_faces, recon_edges = redraw_occfaces(scaled_shape)
scaled_cmpd = py3dmodel.construct.make_compound(recon_faces)

print "#========================================"
print "GRIDDING THE BOUNDARY FOOTPRINT ... ..."
print "#========================================"
#get the bounding box of the cmpd
xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(scaled_cmpd)

#draw the bounding box footprint
zmax_plus = zmax + 10
intervali = int(math.ceil((xmax-xmin)/xdim))
intervalj = int(math.ceil((ymax-ymin)/ydim))
xmax2 = xmin + (intervali*xdim)
ymax2 = ymin + (intervalj*ydim)
        
footprint_pyptlist = [(xmin,ymax2,zmax_plus ), (xmin,ymin,zmax_plus ), (xmax2,ymin,zmax_plus), (xmax2,ymax2,zmax_plus)]
bbfootprint = py3dmodel.construct.make_polygon(footprint_pyptlist)

#grid the bbfootpront
occgrid_list = py3dmodel.construct.grid_face(bbfootprint, xdim, ydim)
occgrid_list = py3dmodel.modify.sort_face_by_xy(occgrid_list)
ngrid = len(occgrid_list)
print "NUMBER OF GRIDS:", ngrid

#index the collada faces
face_dict_list = index_faces(recon_faces, xdim, ydim, xmin, ymin, intervali, occgrid_list, zmax_plus)

print "#============================="
print "WRITING TO SHAPEFILE ... ... "
print "#============================="
extrude_list = []
intersection_list = []

height_list = []
pyptlist2d_list = []
gcnt = 0
for g in occgrid_list:
    #get the collada faces that is within this grid
    chosen_faces = get_occface_frm_dict_list(gcnt, face_dict_list)
    #py3dmodel.utility.visualise([chosen_faces, [g]], ["RED", "BLUE"])
    fcmpd = py3dmodel.construct.make_compound(chosen_faces)
    
    g_mid_pt = py3dmodel.calculate.face_midpt(g)
    interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(fcmpd, g_mid_pt, (0,0,-1))
        
    if interpt:
        zmax1 = interpt[2]
        height = zmax1-zmin
        height_list.append(height)
        #get the points from the grids
        pyptlist3d = py3dmodel.fetch.points_frm_occface(g)
        pyptlist2d = pyptlist3222d(pyptlist3d)
        pyptlist2d_list.append(pyptlist2d)
        
    if gcnt%100.0 == 0:
        print "WRITING SHAPEFILE ... ...", gcnt, "/", ngrid
    if gcnt%10000 == 0:
        interim = os.path.join(result_dir, "interim" + str(gcnt) + ".shp")
        write2shp(pyptlist2d_list, height_list, interim)
    gcnt+=1

shp_filepath = os.path.join(result_dir, "cbd_3by3.shp")
write2shp(pyptlist2d_list, height_list, shp_filepath)
time2 = time.clock()
time_taken = (time2-time1)/60.0
print "TIME TAKEN:", time_taken

#display_2dlist.append(recon_faces)
#colour_list.append("WHITE")
#e_cmpd = py3dmodel.construct.make_compound(extrude_list)
#e_edges = py3dmodel.fetch.topo_explorer(e_cmpd, "edge")
#display_2dlist.append(e_edges)
#colour_list.append("BLACK")
#print "WRITING COLLADA ... ..."
#py3dmodel.export_collada.write_2_collada(dae_file2, occface_list = occgrid_list, occedge_list = e_edges)
#print "DONE WRITING COLLADA ... ..."
#py3dmodel.utility.visualise(display_2dlist, colour_list)