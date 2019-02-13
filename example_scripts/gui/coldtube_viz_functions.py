from py4design import py3dmodel
import numpy as np
import pyqtgraph.opengl as gl

def collada2meshes(path, face_colours = None):
    faces = read_collada(path)
    meshes = faces2meshes(faces, face_colours = face_colours)
    return meshes
    
def viz_mesh(meshes, view3d):
    for m in meshes:
        view3d.addItem(m)
 
def edit_mesh_colour(meshes, colour):
    for m in meshes:
        m.setColor(colour)
    return meshes

def read_collada(filename):
    import collada
    from collada import polylist, triangleset
    mesh = collada.Collada(filename)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    display_list = []
    g_cnt = 0
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist:     
            if primlist:
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                        is_face_null = py3dmodel.fetch.is_face_null(occpolygon)
                        if not is_face_null:
                            display_list.append(occpolygon)
                        g_cnt +=1
                        
    cmpd = py3dmodel.construct.make_compound(display_list)
    scaled_cmpd = py3dmodel.modify.scale(cmpd, unit,(0,0,0))
    face_list = py3dmodel.fetch.topo_explorer(scaled_cmpd,"face")
    
    return face_list

def faces2meshes(occface_list, face_colours = None):
    mesh_list = []
    cnt = 0
    for face in occface_list:
        if face_colours != None:
            mesh = face2mesh(face, face_colour = face_colours[cnt])
        else:
            mesh = face2mesh(face, face_colour = None)
            
        mesh_list.append(mesh)
        cnt+=1
        
    return mesh_list

def face2mesh(occface, face_colour = None):
    mesh_dict = py3dmodel.construct.face2mesh(occface)
    verts = mesh_dict["vertices"]
    faces = mesh_dict["indices"]
    verts = np.array(verts)
    faces = np.array(faces)
        
    mesh = gl.GLMeshItem(vertexes=verts, faces=faces,
                         smooth=False,
                         shader = "edgeHilight",
                         glOptions = "opaque")
    
    if face_colour == None:
       face_colour = [0.6,0.6,0.6,1]
       
    mesh.setColor(face_colour)

    return mesh

def draw_boundary_edge(path, view3d):
    faces = read_collada(path)
    faces2 = py3dmodel.construct.merge_faces(faces)
    for f in faces2:
        midpt = py3dmodel.calculate.face_midpt(f)
        nrml = py3dmodel.calculate.face_normal(f)
        loc_pt = py3dmodel.modify.move_pt(midpt, nrml, 50)
        moved_f = py3dmodel.modify.move(midpt, loc_pt, f)
        moved_f = py3dmodel.fetch.topo2topotype(moved_f)
        pyptlist = py3dmodel.fetch.points_frm_occface(moved_f)
        pyptlist.append(pyptlist[0])
        pyptlist = np.array(pyptlist)
        plt = gl.GLLinePlotItem(pos=pyptlist, color= (1,1,1,1), width=3, antialias=True)
        view3d.addItem(plt)

def read_data2memory(start_date, end_date):
    import os
    current_path = os.path.dirname(__file__)
    data_path = os.path.join(current_path, "coldtube_data")
    
    name_list = ["panel1", "panel2", "panel3", "panel4",
                 "panel5", "panel6", "panel7", "panel8",
                 "panel10", "red_tank", "blue_tank", "environment"]
    
    data_dict = {}
    
    for name in name_list:
        csv_path = os.path.join(data_path, name+".csv")
        d, date_list = load_csv(csv_path, start_date, end_date)
        data_dict[name] = d 
        
    return data_dict, name_list, date_list
    
def load_csv(csv_path, start_date, end_date):
    import csv
    from dateutil.parser import parse
    from dateutil import tz

    from_zone = tz.tzutc()
    to_zone = tz.gettz("Asia/Singapore")
    f = open(csv_path, mode = "r")
    csv_reader = csv.reader(f, delimiter = ";")
    date_list = []
    titles = []
    d = {}
    cnt = 0
    for r in csv_reader:
        if cnt == 1:
            titles = r
        if cnt > 1:
            date_str = r[0]
            #print date_str
            date = parse(date_str)
            utc= date.replace(tzinfo=from_zone)
            date = utc.astimezone(to_zone)
            #print date, start_date, end_date
            if start_date <= date <= end_date:
                date_list.append(date)
                nr = len(r)
                d2 = {}
                
                for i in range(nr-1):
                    d2[titles[i+1]] = r[i+1]
                    
                d[date] = d2
        cnt+=1
        
    #date_list.sort()
    return d, date_list

def edit_mesh_shader(meshes, shader):
    for m in meshes:
        m.setShader(shader)
    return meshes

def get_env_temps(date, data):
    env_data = data["environment"]
    date_data = env_data[date]
    air_temp = float(date_data["Air"])
    dew = float(date_data["Dewpoint"])
    globe = float(date_data["Cletus Globe"])
    return round(air_temp,2), round(dew,2), round(globe,2)
    
def map_data23d(date, data, geometry, data_keys, min_val, max_val, view3d):
    clear_3dview(view3d)
    #map the data onto the geometry
    
    mesh_list = []
    
    #regen the falsecolor just in case
    #self.params2.clearChildren()
    #self.gen_falsecolour_bar(min_val, max_val)
    #self.params2.addChild(self.falsecolour)
    
    #viz geoms that does not have data
    fmeshes = geometry["floor"]
    meshes9 = geometry["panel9"]
    meshes10 = geometry["panel10"]
    nd_meshes = fmeshes + meshes9 + meshes10

    mesh_list.extend(nd_meshes)
    
    for key in data_keys:
        component = data[key]
        #print component
        date_data = component[date]
        
        if key[0:5] == "panel" and key != "panel10":
            temp_data = date_data["Surface Temp"]
            if temp_data == "null" or temp_data == "undefined":
                colour = [0, 0, 0, 1]
            else:
                temp_data = float(temp_data)
                colour = py3dmodel.utility.pseudocolor(temp_data, min_val, max_val)
                colour = [colour[0], colour[1], colour[2], 1]
            
            meshes = geometry[key]
            meshes2 = geometry[key[0:5]+"_membrane_"+ key[-1]]
            meshes3 = meshes + meshes2
            meshes3 = edit_mesh_colour(meshes3, colour)
            meshes3 = edit_mesh_shader(meshes3, "balloon")
            mesh_list.extend(meshes3)
            
        elif key == "red_tank" or key == "blue_tank":
            temp_data = date_data["Tank"]
            if temp_data == "null" or temp_data == "undefined":
                colour = [0, 0, 0, 1]
            else:
                temp_data = float(temp_data)
                colour = py3dmodel.utility.pseudocolor(temp_data, min_val, max_val)
                colour = [colour[0], colour[1], colour[2], 1]
            
            meshes = geometry[key]
            meshes = edit_mesh_colour(meshes, colour)
            meshes = edit_mesh_shader(meshes, "balloon")
            mesh_list.extend(meshes)
            
        if key == "panel2":
            temp_data1 = date_data["Supply"]
            
            if temp_data1 == "null" or temp_data1 == "undefined":
                colour1 = [0, 0, 0, 1]
            else:
                temp_data1 = float(temp_data1)
                colour1 = py3dmodel.utility.pseudocolor(temp_data1, min_val, max_val)
                colour1 = [colour1[0], colour1[1], colour1[2], 1]
            
            temp_data2 = date_data["Return"]
            
            if temp_data2 == "null" or temp_data2 == "undefined":
                colour2 = [0, 0, 0, 1]
            else:
                temp_data2 = float(temp_data2)
                colour2 = py3dmodel.utility.pseudocolor(temp_data2, min_val, max_val)
                colour2 = [colour2[0], colour2[1], colour2[2], 1]
            
            meshes1 = geometry["red_tank_supply"]
            meshes1 = edit_mesh_colour(meshes1, colour1)
            meshes1 = edit_mesh_shader(meshes1, "balloon")
            mesh_list.extend(meshes1)
            
            meshes2 = geometry["red_tank_return"]
            meshes2 = edit_mesh_colour(meshes2, colour2)
            meshes2 = edit_mesh_shader(meshes2, "balloon")
            mesh_list.extend(meshes2)
        
        if key == "panel6":
            temp_data1 = date_data["Supply"]
            
            if temp_data1 == "null" or temp_data1 == "undefined":
                colour1 = [0, 0, 0, 1]
            else:
                temp_data1 = float(temp_data1)
                colour1 = py3dmodel.utility.pseudocolor(temp_data1, min_val, max_val)
                colour1 = [colour1[0], colour1[1], colour1[2], 1]
            
            temp_data2 = date_data["Return"]
            
            if temp_data2 == "null" or temp_data2 == "undefined":
                colour2 = [0, 0, 0, 1]
            else:
                temp_data2 = float(temp_data2)
                colour2 = py3dmodel.utility.pseudocolor(temp_data2, min_val, max_val)
                colour2 = [colour2[0], colour2[1], colour2[2], 1]
            
            meshes1 = geometry["blue_tank_supply"]
            meshes1 = edit_mesh_colour(meshes1, colour1)
            meshes1 = edit_mesh_shader(meshes1, "balloon")
            mesh_list.extend(meshes1)
            
            meshes2 = geometry["blue_tank_return"]
            meshes2 = edit_mesh_colour(meshes2, colour2)
            meshes2 = edit_mesh_shader(meshes2, "balloon")
            mesh_list.extend(meshes2)
            
    return mesh_list
    
def clear_3dview(view_3d):
    all_items = view_3d.items
    nitems = len(all_items)
    while (nitems !=0):
        for i in all_items:
            view_3d.removeItem(i)
        
        all_items = view_3d.items
        nitems = len(all_items)
        
def gen_falsecolour_bar(min_val, max_val):
        flist, bcolour, txt_geom, str_col, float_list = py3dmodel.utility.generate_falsecolour_bar(min_val,max_val,"C", 
                                                                                              5, bar_pos = (4,0,0))
        new_c_list = []
        for c in bcolour:
            new_c = [c[0]*255, c[1]*255, c[2]*255]
            new_c_list.append(new_c)
            
        rangex = max_val-min_val
        intervals = rangex/10.0
        intervals_half = intervals/2.0
        str_list = []
        for f in float_list:
            mi = f - intervals_half
            ma = f + intervals_half
            strx = str(mi) + " - " + str(ma)
            str_list.append(strx)
            
        falsecolour = dict(name='Falsecolour', type='group', expanded = True, title = "Colour Legend (C)",
                                children =  [dict(name = str_list[0], type = 'color', value = new_c_list[0], readonly = True),
                                             dict(name = str_list[1], type = 'color', value = new_c_list[1], readonly = True),
                                             dict(name = str_list[2], type = 'color', value = new_c_list[2], readonly = True),
                                             dict(name = str_list[3], type = 'color', value = new_c_list[3], readonly = True),
                                             dict(name = str_list[4], type = 'color', value = new_c_list[4], readonly = True),
                                             dict(name = str_list[5], type = 'color', value = new_c_list[5], readonly = True),
                                             dict(name = str_list[6], type = 'color', value = new_c_list[6], readonly = True),
                                             dict(name = str_list[7], type = 'color', value = new_c_list[7], readonly = True),
                                             dict(name = str_list[8], type = 'color', value = new_c_list[8], readonly = True),
                                             dict(name = str_list[9], type = 'color', value = new_c_list[9], readonly = True),
                                            ]
                            )
        return falsecolour