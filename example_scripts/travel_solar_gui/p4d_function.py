import os
import json
import colorsys
import collections
import datetime
from dateutil.parser import parse

import PyQt5
from py4design import py3dmodel, shp2citygml, shapeattributes
import numpy as np
import pyqtgraph.opengl as gl
import shapefile
from pyproj import Proj

week_hours = 168
weekly_hr_list = [168, 336, 504, 672, 840, 1008, 1176, 1344, 1512, 1680, 1848, 2016, 2184, 2352, 2520, 2688, 
                  2856, 3024, 3192, 3360, 3528, 3696, 3864, 4032, 4200, 4368, 4536, 4704, 4872, 5040, 5208, 
                  5376, 5544, 5712, 5880, 6048, 6216, 6384, 6552, 6720, 6888, 7056, 7224, 7392, 7560, 7728, 
                  7896, 8064, 8232, 8400, 8568, 8760]

#===========================================================================================
#GUI RELATED FUNCTIONS
#===========================================================================================
def gen_falsecolour_bar(min_val, max_val):
#    flist, bcolour, txt_geom, str_col, float_list = py3dmodel.utility.generate_falsecolour_bar(min_val,max_val,"W/m2", 
#                                                                                         5, bar_pos = (4,0,0))
    
    interval = 10.0
    inc1 = (max_val-min_val)/(interval)
    inc2 = inc1/2.0    
    float_list = list(np.arange(min_val+inc2, max_val, inc1))
    bcolour = py3dmodel.utility.falsecolour(float_list, min_val, max_val)
    new_c_list = []
    for c in bcolour:
        new_c = [c[0]*255, c[1]*255, c[2]*255]
        new_c_list.append(new_c)
        
    rangex = max_val-min_val
    intervals = rangex/10.0
    intervals_half = intervals/2.0
    str_list = []
    for f in float_list:
        f = round(f)
        mi = f - intervals_half
        ma = f + intervals_half
        strx = str(mi) + " - " + str(ma)
        str_list.append(strx)
        
    falsecolour = dict(name='Falsecolour', type='group', expanded = True, title = "Colour Legend (W/m2)",
                            children =  [dict(name = str_list[0], type = 'color', value = new_c_list[0], readonly = True),
                                         dict(name = str_list[1], type = 'color', value = new_c_list[1], readonly = True),
                                         dict(name = str_list[2], type = 'color', value = new_c_list[2], readonly = True),
                                         dict(name = str_list[3], type = 'color', value = new_c_list[3], readonly = True),
                                         dict(name = str_list[4], type = 'color', value = new_c_list[4], readonly = True),
                                         dict(name = str_list[5], type = 'color', value = new_c_list[5], readonly = True),
                                         dict(name = str_list[6], type = 'color', value = new_c_list[6], readonly = True),
                                         dict(name = str_list[7], type = 'color', value = new_c_list[7], readonly = True),
                                         dict(name = str_list[8], type = 'color', value = new_c_list[8], readonly = True),
                                         dict(name = str_list[9], type = 'color', value = new_c_list[9], readonly = True)]
                        )
    return falsecolour

def edit_falsecolour(params2, min_val, max_val):
    falsecolour = params2.param("Falsecolour")
    params2.removeChild(falsecolour)
    new_falsecolour = gen_falsecolour_bar(min_val, max_val)
    params2.insertChild(0,new_falsecolour)
    
#===========================================================================================
#3D VIEW RELATED FUNCTIONS
#===========================================================================================
def viz_graphic_items(graphic_item_list, view3d):
    for m in graphic_item_list:
        view3d.addItem(m)
 
def edit_mesh_colour(meshes, colour):
    for m in meshes:
        m.setColor(colour)
    return meshes

def edit_mesh_face_colours(mesh, colour_list):
    meshdata = mesh.opts['meshdata']
    
    if type(colour_list) == np.ndarray:
        meshdata.setFaceColors(colour_list, indexed=None)
    else:
        meshdata.setFaceColors(np.array(colour_list), indexed=None)
        
    mesh.meshDataChanged()

def set_graphic_items_visibility(graphic_item_list, visibility):
    for m in graphic_item_list:
        if m !=None:
            m.setVisible(visibility)
        
def is_graphic_items_visible(graphic_item_list):
    is_vis = True
    for m in graphic_item_list:
        if not m.visible():
            is_vis = False
            break
    return is_vis

def edit_mesh_shader(meshes, shader):
    for m in meshes:
        m.setShader(shader)
    return meshes
    
def clear_3dview(view_3d):
    all_items = view_3d.items
    nitems = len(all_items)
    while (nitems !=0):
        for i in all_items:
            view_3d.removeItem(i)
        
        all_items = view_3d.items
        nitems = len(all_items)
#===========================================================================================
#DRAW FACES RELATED FUNCTIONS
#===========================================================================================
def topos2meshes_json(topo_list, json_filepath, face_colours2d = None, att_dict_list = None):
    ntopo = len(topo_list)
    if face_colours2d  != None:
        ncolours = len(face_colours2d)
        if ncolours != ntopo:
            print("SOMETHING IS WRONG THE COLOURS LIST DOES NOT MATCH THE NUMBER OF TOPOS")
            
    json_list = []
    for cnt in range(ntopo):
        topo = topo_list[cnt]
        if face_colours2d !=None:
            colour_list = face_colours2d[cnt]
        else:
            colour_list = None
            
        if att_dict_list !=None:
            att_dict = att_dict_list[cnt]
        else:
            att_dict = None
            
        mesh_dict = topo2mesh_dict(topo, face_colours = colour_list, 
                                   att_dict = att_dict)
        json_list.append(mesh_dict)
    
    json_str = json.dumps(json_list)
    f = open(json_filepath, "w")
    f.write(json_str)
    f.close()
    
def topo2mesh_dict(topo, face_colours = None, att_dict = None, reverse = False):
    mesh_dict = py3dmodel.construct.topo2mesh(topo, reverse = reverse)
    mesh_dict["face_colours"] = face_colours
    mesh_dict["attributes"] = att_dict
    return mesh_dict

def tri_faces2mesh_json(tri_face_list, json_filepath, face_colours = None, att_dict_list = None):    
    mesh_dict = tri_faces2mesh_dict(tri_face_list, face_colours = face_colours, att_dict_list = att_dict_list)
    mesh_list = [mesh_dict]
    json_str = json.dumps(mesh_list)
    f = open(json_filepath, "w")
    f.write(json_str)
    f.close()
    
def tri_faces2mesh_dict(tri_face_list, face_colours = None, att_dict_list = None):
    vert_list = []
    index_list = []
    
    for face in tri_face_list:
        indices = []
        pyptlist = py3dmodel.fetch.points_frm_occface(face)
        pyptlist.reverse()
        for pypt in pyptlist:
            if pypt not in vert_list:
                vert_list.append(pypt)
        
            index = vert_list.index(pypt)
            indices.append(index)
        
        index_list.append(indices)
    
    mesh_dict = {"indices": index_list, "vertices": vert_list, "face_colours": face_colours}
    return mesh_dict
    
def read_meshes_json(json_filepath, shader = "shaded", gloptions = "opaque", draw_edges = False, edge_colours = [0,0,0,1]):
    f = open(json_filepath, "r")
    json_data = json.load(f)
    mesh_list = []
    for data in json_data:
        verts = data["vertices"]
        faces = data["indices"]
        verts = np.array(verts)
        faces = np.array(faces)
        face_colours = data["face_colours"]
        
        if face_colours != None:
            face_colours = np.array(face_colours)
            
        mesh = make_mesh(verts, faces, face_colours, shader = shader, gloptions = gloptions, draw_edges = draw_edges, 
                         edge_colours =edge_colours)
        
        mesh_list.append(mesh)
        
    f.close()
    return mesh_list

def make_mesh(vertices_array, indices_array, face_colours_array, shader = "shaded", gloptions = "opaque", draw_edges = False, 
                edge_colours = [0,0,0,1]):
    
    mesh = gl.GLMeshItem(vertexes=vertices_array, faces=indices_array, 
                         faceColors=face_colours_array,
                         edgeColor = edge_colours,
                         smooth=False,
                         drawEdges=draw_edges, 
                         shader = shader,
                         glOptions = gloptions)
    
    return mesh
    

def read_meshes_att_json(json_filepath, shader = "shaded", gloptions = "opaque", draw_edges = False, edge_colours = [0,0,0,1]):
    f = open(json_filepath, "r")
    json_data = json.load(f)
    mesh_list = []
    att_list = []
    cnt = 0
    for data in json_data:
        verts = data["vertices"]
        faces = data["indices"]
        verts = np.array(verts)
        faces = np.array(faces)
        face_colours = data["face_colours"]
        att_dict = data["attributes"]     
        att_list.append(att_dict)
        if face_colours != None:
            face_colours = np.array(face_colours)
            
        mesh = make_mesh(verts, faces, face_colours, shader = shader, gloptions = gloptions, draw_edges = draw_edges, 
                         edge_colours =edge_colours)
        
        mesh_list.append(mesh)
        cnt+=1
    
    return mesh_list, att_list

def triangulate_faces(face_list):
    tri_face_list = []
    for face in face_list:
        tri_faces = py3dmodel.construct.simple_mesh(face)
        tri_face_list.extend(tri_faces)
    return tri_face_list
#===========================================================================================
#DRAW EDGES RELATED FUNCTIONS
#===========================================================================================
def draw_boundary_edge_json(topo_list, json_filepath, att_dict_list = None):
    json_data = []
    cnt = 0
    for topo in topo_list:
        if att_dict_list !=None:
            att_dict = att_dict_list[cnt]
        else:
            att_dict = None
            
        edge_dict = draw_boundary_edge(topo, att_dict=att_dict)
        json_data.append(edge_dict)
        
        cnt+=1
            
    json_str = json.dumps(json_data)
    f = open(json_filepath, "w")
    f.write(json_str)
    f.close()
    
def draw_boundary_edge(topo, att_dict = None):
    faces = py3dmodel.fetch.topo_explorer(topo, "face")
    pyptlist = []
    for f in faces:
        edges = py3dmodel.fetch.topo_explorer(f, "edge")
        for e in edges:
            pypts = py3dmodel.fetch.points_frm_edge(e)
            pyptlist.extend(pypts)
            
    edge_dict = {"vertices": pyptlist, "attributes": att_dict}
    return edge_dict
            
def draw_edge_json(topo_list, json_filepath, att_dict_list = None):
    json_data = []
    cnt = 0
    for topo in topo_list:
        if att_dict_list !=None:
            att_dict = att_dict_list[cnt]
        else:
            att_dict = None
            
        edge_dict = draw_edges(topo, att_dict = att_dict)
        json_data.append(edge_dict)
        cnt+=1
        
    json_str = json.dumps(json_data)
    f = open(json_filepath, "w")
    f.write(json_str)
    f.close()

def draw_edges(topo, att_dict=None):
    edges = py3dmodel.fetch.topo_explorer(topo, "edge")
    pyptlist = []
    for e in edges:
        pypts = py3dmodel.fetch.points_frm_edge(e)
        pyptlist.extend(pypts)
            
    edge_dict = {"vertices": pyptlist, "attributes": att_dict}
    return edge_dict
    
def read_edges_json(json_filepath, line_colour = (1,1,1,1), width = 1, antialias=True, mode="lines"):
    lines = []
    f = open(json_filepath, "r")
    json_data = json.load(f)
    for data in json_data:
        vertices = data["vertices"]
        vertices  = np.array(vertices )
        plt = gl.GLLinePlotItem(pos=vertices, color= line_colour, width=width, antialias=antialias, mode = mode)
        lines.append(plt)
    
    return lines

def read_edges_att_json(json_filepath, line_colour = (1,1,1,1), width = 1, antialias=True, mode="lines"):
    lines = []
    att_dict_list = []
    f = open(json_filepath, "r")
    json_data = json.load(f)
    for data in json_data:
        vertices = data["vertices"]
        att_dict = data["attributes"]
        att_dict_list.append(att_dict)
        vertices  = np.array(vertices )
        plt = gl.GLLinePlotItem(pos=vertices, color= line_colour, width=width, antialias=antialias, mode = mode)
        lines.append(plt)
    
    return lines, att_dict_list
#===========================================================================================
#RETRIEVE DYNAMIC DATA RELATED
#===========================================================================================    
def date2index(date):
    str_sp_date = str(2019) + "-" + str(1) + "-" + str(1) + "-" +\
                    str(0) + ":" + str(0) + ":" + str(0)
                    
    date0 = parse(str_sp_date)
    date1 = date
    td2 = date1-date0
    hours = td2.total_seconds()/3600
    return int(hours)

def index2date(hour_index):
    str_sp_date = str(2019) + "-" + str(1) + "-" + str(1) + "-" +\
                    str(0) + ":" + str(0) + ":" + str(0)
                    
    
    date0 = parse(str_sp_date)
    
    td = datetime.timedelta(hours=hour_index)
    date1 = date0+td

    return date1

def pseudocolor(val, minval, maxval, inverse = False):
    # convert val in range minval..maxval to the range 0..120 degrees which
    # correspond to the colors red..green in the HSV colorspace
    if val <= minval:
        if inverse == False:
            h = 250.0
        else:
            h=0.0
    elif val>=maxval:
        if inverse == False:
            h = 0.0
        else:
            h=250.0
    else:
        if inverse == False:
            h = 250 - (((float(val-minval)) / (float(maxval-minval)))*250)
        else:
            h = (((float(val-minval)) / (float(maxval-minval)))*250)
    # convert hsv color (h,1,1) to its rgb equivalent
    # note: the hsv_to_rgb() function expects h to be in the range 0..1 not 0..360
    r, g, b = colorsys.hsv_to_rgb(h/360, 1., 1.)
    return r,g,b,1

def retrieve_colour(hour_index, solar_dir, minval, maxval):
    numpycolour = np.vectorize(pseudocolor)
    for i in range(52):
        i2 = i+1
        end_hr = week_hours * i2
        start_hr = end_hr - week_hours
        if i == 51:
            end_hr = 8759

        if start_hr <= hour_index < end_hr:
            json_filepath = os.path.join(solar_dir, "viz_grd_solar_week" + str(i) + ".json")
            f = open(json_filepath, "r")
            json_data = json.load(f)
            hour_index2 = hour_index - start_hr
            solars = json_data[hour_index2]["solar"]
            colours = numpycolour(solars, minval, maxval)
            colours = np.array(colours)
            colours = colours.T
            break
    
    return colours

def retrieve_solar_data(solar_mesh, hour_index, solar_dir, minval, maxval):            
    face_colours = retrieve_colour(hour_index, solar_dir, minval, maxval)
    face_colours  = np.repeat(face_colours, 2, axis=0)
    edit_mesh_face_colours(solar_mesh, face_colours)
    
def retrieve_parking_data(hour_index, parking_dir, parking_mesh, view_3d, minval, maxval):
    numpycolour = np.vectorize(pseudocolor)
    if parking_mesh[0] != None:
        view_3d.removeItem(parking_mesh[0])
        
    for i in range(52):
        end_hr = weekly_hr_list[i]
        if i ==0:
            start_hr = 0
        else:
            start_hr = weekly_hr_list[i-1]
        
        if start_hr <= hour_index < end_hr:
            try:
                parking_filepath = os.path.join(parking_dir, "viz", "viz_parking_wk" + str(i) + ".json")
                parking_f = open(parking_filepath, "r")
                json_data = json.load(parking_f)
                parking_f.close()
                if str(hour_index) in json_data.keys():
                    chosen = json_data[str(hour_index)]
                    verts = np.array(chosen["vertices"])
                    indices = np.array(chosen["indices"])
                    
                    solar_result = chosen["attributes"]["solar_result"]
                    colours = numpycolour(solar_result, minval, maxval)
                    colours = np.array(colours)
                    colours = colours.T
                
                    mesh = make_mesh(verts, indices, colours, shader = "shaded", gloptions = "opaque", draw_edges = False, edge_colours = [0,0,0,1])
                    return mesh
            except:
                break
    
def retrieve_travel_data(hour_index, travel_dir, extrude_mesh, extrude_bdry, path, view_3d):
    if extrude_mesh[0] != None:
        view_3d.removeItem(extrude_mesh[0])
        view_3d.removeItem(extrude_bdry[0])
    if path[0] != None:
        view_3d.removeItem(path[0])
    
    extrude_mesh_list  = []
    ext_mesh_att_list = []
    
    extrude_line_list = []
    path_line_list = []
    path_att_list = []
    
    for i in range(52):
        end_hr = weekly_hr_list[i]
        if i ==0:
            start_hr = 0
        else:
            start_hr = weekly_hr_list[i-1]
        
        if start_hr <= hour_index < end_hr:
            try:
                extrude_filepath = os.path.join(travel_dir, "extrude_meshes_wk" + str(i) + ".json")
                extrude_edges_filepath = os.path.join(travel_dir, "extrude_bdry_wk" + str(i) +  ".json")
                path_edges_filepath = os.path.join(travel_dir, "path_wk"+ str(i) + ".json")
                
                #read all the meshes and lines
                extrude_mesh_list, ext_mesh_att_list  = read_meshes_att_json(extrude_filepath, shader = "shaded", gloptions = "additive")
        
                #read the boundary edges
                extrude_line_list = read_edges_json(extrude_edges_filepath, line_colour = (1,0,0,1), width = 3, antialias=True, mode="lines")
        
                #read the path 
                path_line_list, path_att_list = read_edges_att_json(path_edges_filepath, line_colour = (1,0,0,1), width = 3, antialias=True, mode="lines")
                break
            except:
                break
    
    mesh_vis = None
    bdry_vis = None
    path_vis = None
    
    acnt = 0
    for att in ext_mesh_att_list:
        hi = att["hour_index"]
        if hour_index == hi:
            mesh_vis = extrude_mesh_list[acnt]
            bdry_vis = extrude_line_list[acnt]
        acnt+=1
    
    bcnt = 0
    for att2 in path_att_list:
        hi = att2["hour_index"]
        if hour_index == hi:
            path_vis = path_line_list[bcnt]
        bcnt+=1
    
    return mesh_vis, bdry_vis, path_vis
#===========================================================================================
#SHAPEFILE RELATED
#===========================================================================================  
def read_sf_poly(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            occfaces = shp2citygml.shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
            for occface in occfaces:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(occface)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def read_sf_polyline(sf_filepath):
    sf = shapefile.Reader(sf_filepath)
    attrib_name_list = shp2citygml.get_field_name_list(sf)[1:]
    shapeRecs=sf.shapeRecords()
    shpatt_list = []
    
    for rec in shapeRecs:
        poly_atts=rec.record
        pypolygon_list2d = shp2citygml.get_geometry(rec)
        if pypolygon_list2d:
            pypolygon_list3d = shp2citygml.pypolygon_list2d_2_3d(pypolygon_list2d, 0.0)
            for polyline in pypolygon_list3d:
                shpatt = shapeattributes.ShapeAttributes()
                shpatt.set_shape(polyline)
                att2shpatt(shpatt, attrib_name_list, poly_atts)
                shpatt_list.append(shpatt)
                
    return shpatt_list

def att2shpatt(shpatt, attrib_name_list, poly_atts):
    natt = len(attrib_name_list)
    for cnt in range(natt):
        att_name = attrib_name_list[cnt]
        att = poly_atts[cnt]
        shpatt.set_key_value(att_name, att)
        
#===========================================================================================
#ANALYSIS RELATED FUNCTIONS
#=========================================================================================== 
def id_week(hour):    
    for i in range(52):
        end_hr = weekly_hr_list[i]
        if i ==0:
            start_hr = 0
        else:
            start_hr = weekly_hr_list[i-1]
        
        if start_hr <= hour < end_hr:
            return i
        
def id_weeks(start_hour, end_hour):
    week_list = []
    #generate all the hours 
    hours_interest = range(start_hour, end_hour+1)
    for hour in hours_interest:
        week_index = id_week(hour)
        if week_index not in week_list:
            week_list.append(week_index)
    return week_list
            
def retrieve_travel_ext_analysis(travel_shp_dir, start_hour, end_hour):
    travel_dict = {}
    week_list = id_weeks(start_hour, end_hour)
    hour_interest = range(start_hour, end_hour+1)
    for week in week_list:    
        shp_filepath = os.path.join(travel_shp_dir, "extrusions_week" + str(week) + ".shp")
        if os.path.isfile(shp_filepath):
            shpatts = read_sf_poly(shp_filepath)
            travels = shpatt2dict(shpatts)
            #find only the hours of interest
            end_wk_hr = weekly_hr_list[week]
            if week == 0:
                start_wk_hr = 0
            else:
                start_wk_hr = weekly_hr_list[week-1]
            
            week_range = range(start_wk_hr, end_wk_hr)
            
            a_multiset = collections.Counter(week_range)
            b_multiset = collections.Counter(hour_interest)

            overlap = list((b_multiset & a_multiset).elements())
#            week_remainder = list((a_multiset - b_multiset).elements())
            
            chosen = {}
            for h in overlap:
                if h in travels.keys():
                    chosen[h] = travels[h]
                
            travel_dict.update(chosen)

    return travel_dict

def retrieve_travel_path_analysis(travel_shp_dir, start_hour, end_hour):
    travel_dict = {}
    week_list = id_weeks(start_hour, end_hour)
    hour_interest = range(start_hour, end_hour+1)
    for week in week_list:    
        shp_filepath = os.path.join(travel_shp_dir, "paths_week" + str(week) + ".shp")
        if os.path.isfile(shp_filepath):
            shpatts = read_sf_polyline(shp_filepath)
            travels = shpatt2dict(shpatts)
            #find only the hours of interest
            end_wk_hr = weekly_hr_list[week]
            if week == 0:
                start_wk_hr = 0
            else:
                start_wk_hr = weekly_hr_list[week-1]
            
            week_range = range(start_wk_hr, end_wk_hr)
            
            a_multiset = collections.Counter(week_range)
            b_multiset = collections.Counter(hour_interest)

            overlap = list((b_multiset & a_multiset).elements())
            
            chosen = {}
            for h in overlap:
                if h in travels.keys():
                    chosen[h] = travels[h]
                
            travel_dict.update(chosen)

    return travel_dict

def retrieve_parking_analysis(parking_dir, start_hour, end_hour):
    parking_dict = {}
    week_list = id_weeks(start_hour, end_hour)
    hour_interest = range(start_hour, end_hour+1)
    for week in week_list:    
        json_filepath = os.path.join(parking_dir,"analysis", "parking_wk" + str(week) + ".json")
        if os.path.isfile(json_filepath):
            json_file = open(json_filepath, "r")
            json_data = json.load(json_file)
            #find only the hours of interest
            end_wk_hr = weekly_hr_list[week]
            if week == 0:
                start_wk_hr = 0
            else:
                start_wk_hr = weekly_hr_list[week-1]
            
            week_range = range(start_wk_hr, end_wk_hr)
            
            a_multiset = collections.Counter(week_range)
            b_multiset = collections.Counter(hour_interest)

            overlap = list((b_multiset & a_multiset).elements())
            
            chosen = {}
            for h in overlap:
                if str(h) in json_data.keys():
                    chosen[h] = json_data[str(h)]
                
            parking_dict.update(chosen)
            json_file.close()

    return parking_dict

def shpatt2dict(shpatt_list):
    dictx = {}
    for shpatt in shpatt_list:
        d = shpatt.dictionary
        hour = int(d["hour_index"])
        if hour in dictx.keys():
            dictx[hour].append(d)
        else:
            dictx[hour] = [d]
    return dictx

def find_stops(travel_dict, stop_threshold = 0.5):
    new_dict = {}
    for h, lst in travel_dict.items():
        new_list = []
        for x in lst:
            norm_val = x["norm_val"]
            if norm_val >= stop_threshold:
                new_list.append(x)
        if new_list:
            new_dict[h] = new_list

    return new_dict

def extract_pyptlist(pt_dict_list):
    pyptlist = []
    for pt_dict in pt_dict_list:
        pypt = pt_dict["point"]
        pyptlist.append(pypt)
    return pyptlist

def get_solar_pts(solar_dir):
    #first loads the points 
    pt_filepath = os.path.join(solar_dir, "viz_pts.json")
    pt_file = open(pt_filepath, "r")
    pt_dict_list = json.load(pt_file)
    pyptlist = extract_pyptlist(pt_dict_list)
    return pyptlist

def points_in_bdry(pyptlist, rangex, rangey, rangez=[]):
    zipped = zip(*pyptlist)
    xlist = np.array(zipped[0])
    ylist = np.array(zipped[1])
    zlist = np.array(zipped[2])
    
    x_valid = np.logical_and((rangex[0] <= xlist),
                             (rangex[1] >= xlist))
    
    y_valid = np.logical_and((rangey[0] <= ylist),
                             (rangey[1] >= ylist))
    
    if rangez:
        z_valid = np.logical_and((rangez[0] <= zlist),
                                 (rangez[1] >= zlist))
    
        indices = np.where(np.logical_and(x_valid, y_valid, z_valid))
        
    else:
        indices = np.where(np.logical_and(x_valid, y_valid))
        
    if indices[0].size > 0:
#        pyptlist_in_bdry = np.take(pyptlist, indices, axis=0)[0]
#        return pyptlist_in_bdry.tolist()
        return indices[0]
    else:
        return []

def retrieve_solar4analysis(hour_index, solar_dir):
    solars = []
    for i in range(52):
        i2 = i+1
        end_hr = week_hours * i2
        start_hr = end_hr - week_hours
        if i == 51:
            end_hr = 8759

        if start_hr <= hour_index < end_hr:
            json_filepath = os.path.join(solar_dir, "viz_grd_solar_week" + str(i) + ".json")
            f = open(json_filepath, "r")
            json_data = json.load(f)
            hour_index2 = hour_index - start_hr
            solars = json_data[hour_index2]["solar"]
            f.close()
            break
    
    return solars

def find_parking4_the_hour(stops, solar_pts, hour, parking_radius, solar_dir):
    analyse_dict = {}
    analyse_dict[hour] = []
    for stop in stops:
        stop_face = stop["shape"]
        #find all the points in within the spot
        #get the boundary of the stop
        midpt = py3dmodel.calculate.face_midpt(stop_face)
        polygon_cirlce = py3dmodel.construct.make_polygon_circle(midpt, [0,0,1], parking_radius)
        xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(polygon_cirlce)
        
        #get the points inside the boundary
        solar_pts_indices = points_in_bdry(solar_pts, [xmin,xmax],  [ymin, ymax])
        solar_res = retrieve_solar4analysis(hour, solar_dir)
        solar_pts_in_bdry = np.take(solar_pts, solar_pts_indices, axis=0).tolist()
        solar_res_in_bdry = np.take(solar_res, solar_pts_indices, axis=0).tolist()
        #in the end i need generate a series of meshes
        stop["shape"] = [xmin, ymin, zmin, xmax, ymax, zmax ]
        stop["solar_points"] = solar_pts_in_bdry
        stop["solar_results"] = solar_res_in_bdry
        analyse_dict[hour].append(stop)
        
    return analyse_dict

def draw_grids_w_pts(pyptlist):
    rec = py3dmodel.construct.make_rectangle(5,5)
    midpt = py3dmodel.calculate.face_midpt(rec)
    tri_faces = py3dmodel.construct.simple_mesh(rec)
    rec = py3dmodel.construct.make_compound(tri_faces)
    grid_list = []
    for pypt in pyptlist:
        m_rec = py3dmodel.modify.move(midpt, pypt, rec)
        m_recs = py3dmodel.fetch.topo_explorer(m_rec, "face")
        grid_list.extend(m_recs)
    
    return grid_list

def find_potential_parkings(start_hour, end_hour, solar_dir, travel_shp_dir, parking_dir, parking_radius, stop_time_threshold = 0.5):   
    travel_dict = retrieve_travel_ext_analysis(travel_shp_dir, start_hour, end_hour)
    stop_dict = find_stops(travel_dict, stop_threshold = stop_time_threshold)
    solar_pts = get_solar_pts(solar_dir)
    result_dicts = {}
    for hour, stops in stop_dict.items():
        #for each hour find the potential parking spot
        result_dict = find_parking4_the_hour(stops, solar_pts, hour, parking_radius, solar_dir)
        result_dicts.update(result_dict)
    
    hour_list = result_dicts.keys()
    hour_list.sort()
    week_list = id_weeks(start_hour, end_hour)
    for week in week_list:
        end_wk_hr = weekly_hr_list[week]
        if week == 0:
            start_wk_hr = 0
        else:
            start_wk_hr = weekly_hr_list[week-1]
        
        week_range = range(start_wk_hr, end_wk_hr)
        
        a_multiset = collections.Counter(week_range)
        b_multiset = collections.Counter(hour_list)
    
        overlap = list((b_multiset & a_multiset).elements())
        if overlap:
            mesh_dicts = {}
            dict4write = {}
            for o in overlap:
                hour_stops = result_dicts[o]
                dict4write[o] = hour_stops
                grid_list = []
                solar_res_list = []
                for stop in hour_stops:
                    pyptlist = stop["solar_points"]
                    solar_res = stop["solar_results"]
                    solar_res = np.repeat(np.array(solar_res), 2, axis=0).tolist()
                    grids = draw_grids_w_pts(pyptlist)
                    grid_list.extend(grids)
                    solar_res_list.extend(solar_res)
                
                grid_cmpd = py3dmodel.construct.make_compound(grid_list)
                mesh_dict = topo2mesh_dict(grid_cmpd , face_colours = None, att_dict = {"solar_result":solar_res_list})
                mesh_dicts[o] = mesh_dict
                
            parking_viz_filepath = os.path.join(parking_dir,"viz",  "viz_parking_wk" + str(week) + ".json")
            parking_viz = open(parking_viz_filepath, "w")
            json_str1 = json.dumps(mesh_dicts)
            parking_viz.write(json_str1)
            parking_viz.close()
            
            parking_filepath = os.path.join(parking_dir, "analysis", "parking_wk" + str(week) + ".json")
            parking_f = open(parking_filepath, "w")
            json_str = json.dumps(dict4write)
            parking_f.write(json_str)
            parking_f.close()
        
def export_data(start_hour, end_hour, travel_shp_dir, parking_dir):
    path_dict = retrieve_travel_path_analysis(travel_shp_dir, start_hour, end_hour)
#    travel_dict = retrieve_travel_ext_analysis(travel_shp_dir, start_hour, end_hour)
    parking_dict = retrieve_parking_analysis(parking_dir, start_hour, end_hour)
    strx = "Date,DistanceTravelled(m),ParkingTime(hr),SolarMax(wh/m2),SolarMaxPos,SolarMaxZ(m),SolarMin(wh/m2),SolarMinPos,SolarMinZ(m),SolarMedian(wh/m2),SolarMedPos,SolarMedZ(m)\n"
    hour_interest = range(start_hour, end_hour+1)
    
    p = Proj(proj='utm',zone=18,ellps='GRS80', preserve_units=False)
    
    for hour in hour_interest:
        date = index2date(hour)
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        total_dist = 0
        if hour in path_dict.keys():
            paths = path_dict[hour]
            for path in paths:
                dist = path["dist"]
                total_dist+=dist
            
        
        total_park_time = 0
        solar_res_list = []
        total_solar_points = []
        if hour in parking_dict.keys():    
            parkings = parking_dict[hour]
            for parking in parkings:
                solar_res = parking["solar_results"]
                solar_res_list.extend(solar_res)
                park_time = parking["norm_val"]
                total_park_time+=park_time
                solar_points = parking["solar_points"]
                total_solar_points.extend(solar_points)
        
        
        solar_max = 0
        solar_min = 0
        solar_median = 0
        solar_max_pos = ""
        solar_min_pos = ""
        solar_med_pos = ""
        maxz = 0
        minz = 0
        medz = 0
        if solar_res_list:
            solar_max = max(solar_res_list)
            solar_max_index = solar_res_list.index(solar_max)
            solar_max_pos = total_solar_points[solar_max_index]
            maxz = solar_max_pos[2]
            solar_max_pos = (p(solar_max_pos[0], solar_max_pos[1], inverse = True))
            solar_max_pos = str(solar_max_pos[0]) + ";" + str(solar_max_pos[1])
            
            solar_min = min(solar_res_list)
            solar_min_index = solar_res_list.index(solar_min)
            solar_min_pos = total_solar_points[solar_min_index]
            minz = solar_min_pos[2]
            solar_min_pos = (p(solar_min_pos[0], solar_min_pos[1], inverse = True))
            solar_min_pos = str(solar_min_pos[0]) + ";" + str(solar_min_pos[1])
            
            if len(solar_res_list)%2 == 0:
                solar_res_list.append(solar_res_list[-1])
            solar_median = np.median(solar_res_list)
            solar_median_index = solar_res_list.index(solar_median)
            solar_med_pos = total_solar_points[solar_median_index]
            medz = solar_med_pos[2]
            solar_med_pos = (p(solar_med_pos[0], solar_med_pos[1], inverse = True))
            solar_med_pos = str(solar_med_pos[0]) + ";" + str(solar_med_pos[1])
            
        strdata = date_str + "," + str(total_dist) + "," + str(total_park_time) + "," +\
                    str(solar_max) + "," + str(solar_max_pos) + "," + str(maxz) + "," +\
                    str(solar_min) + "," + str(solar_min_pos) + "," + str(minz) + "," +\
                    str(solar_median) + "," + str(solar_med_pos) + "," + str(medz) + "\n"        
        
        strx = strx + strdata
    
    return strx
        
#solar_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\solar_ground4cart_json\\viz"
#travel_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\travel_extrude4carts_shp"
#parking_dir = "F:\\kianwee_work\\princeton\\2019_06_to_2019_12\\campus_as_a_lab\\data\\parking4carts"
#start = 5866 
#end = 5874
#strx = export_data(start, end, travel_dir, parking_dir)
#print strx
#find_potential_parkings(start, end, solar_dir, travel_dir, parking_dir, 100)

#hour_index = 5867
#parking_mesh=[None]
#view_3d = None
#
#min_val = 133.0
#max_val = 914.0
#        
#mesh = retrieve_parking_data(hour_index, parking_dir, parking_mesh, view_3d, min_val, max_val)
#print mesh